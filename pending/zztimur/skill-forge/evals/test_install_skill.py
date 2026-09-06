"""Real filesystem regressions for reviewed local runtime installation."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from runtime_manifest import build_synthetic_manifest, write_canonical_archive
from runtime_manifest import SKILL_FORGE_RUNTIME_SELECTORS


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.skills = self.root / "skills"
        self.skills.mkdir()
        self.target = self.skills / "skill-forge"
        self.archive = self.root / "reviewed.zip"
        files = {}
        for selector in SKILL_FORGE_RUNTIME_SELECTORS:
            source = ROOT / selector
            for path in ([source] if source.is_file() else source.rglob("*")):
                if path.is_file():
                    files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
        write_canonical_archive(build_synthetic_manifest(files), self.archive)
        self.digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()

    def installer(self):
        self.assertIsNotNone(importlib.util.find_spec("install_skill"),
                             "reviewed archive installer is not implemented")
        import install_skill
        return install_skill

    def old_install(self):
        self.target.mkdir()
        (self.target / "SKILL.md").write_text("local edits\n")
        (self.target / "obsolete.py").write_text("old\n")

    def test_replacement_removes_stale_files_and_preserves_backup_and_parity(self):
        installer = self.installer()
        self.old_install()
        result = installer.install_archive(self.archive, self.digest, self.skills)
        self.assertEqual(result["status"], "installed")
        backup = Path(result["backup"])
        self.assertFalse(backup.is_relative_to(self.skills))
        self.assertEqual((backup / "SKILL.md").read_text(), "local edits\n")
        self.assertEqual((backup / "obsolete.py").read_text(), "old\n")
        self.assertFalse((self.target / "obsolete.py").exists())
        with zipfile.ZipFile(self.archive) as archive:
            expected = {name.removeprefix("skill-forge/"): archive.read(name)
                        for name in archive.namelist()}
        actual = {p.relative_to(self.target).as_posix(): p.read_bytes()
                  for p in self.target.rglob("*") if p.is_file()}
        self.assertEqual(actual, expected)
        again = installer.install_archive(self.archive, self.digest, self.skills)
        self.assertEqual(again["status"], "unchanged")
        self.assertIsNone(again["backup"])

    def test_bad_checksum_does_not_mutate_installation(self):
        installer = self.installer()
        self.old_install()
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        with self.assertRaises(installer.InstallError):
            installer.install_archive(self.archive, "f" * 64, self.skills)
        self.assertEqual((self.target / "SKILL.md").read_text(), "local edits\n")
        self.assertEqual(before, sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*")))

    def test_fresh_install_and_removal_of_untracked_empty_directory(self):
        installer = self.installer()
        result = installer.install_archive(self.archive, self.digest, self.skills)
        self.assertEqual(result["status"], "installed")
        self.assertIsNone(result["backup"])
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["reviewed.zip", "skills"])
        (self.target / "empty-stale-directory").mkdir()
        result = installer.install_archive(self.archive, self.digest, self.skills)
        self.assertFalse((self.target / "empty-stale-directory").exists())
        self.assertTrue((Path(result["backup"]) / "empty-stale-directory").is_dir())

    def test_archive_symlink_is_refused(self):
        installer = self.installer()
        alias = self.root / "alias.zip"
        alias.symlink_to(self.archive)
        with self.assertRaises(installer.InstallError):
            installer.install_archive(alias, self.digest, self.skills)
        self.assertFalse(self.target.exists())

    def test_existing_environment_file_is_refused_without_opening_it(self):
        installer = self.installer()
        self.old_install()
        protected = self.target / ".env.local"
        protected.write_text("SYNTHETIC_TEST_ONLY=example\n")
        original_open = Path.open
        def guard_environment_open(path, *args, **kwargs):
            if path.name == ".env" or path.name.startswith(".env."):
                raise AssertionError("installer opened a protected environment file")
            return original_open(path, *args, **kwargs)
        with mock.patch.object(Path, "open", guard_environment_open):
            with self.assertRaisesRegex(installer.InstallError, "environment"):
                installer.install_archive(self.archive, self.digest, self.skills)
            protected = protected.rename(self.target / ".env")
            with self.assertRaisesRegex(installer.InstallError, "environment"):
                installer.install_archive(self.archive, self.digest, self.skills)
        self.assertEqual((self.target / "SKILL.md").read_text(), "local edits\n")
        self.assertTrue(protected.is_file())
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["reviewed.zip", "skills"])

    def test_interrupted_swap_restores_original_tree(self):
        installer = self.installer()
        self.old_install()
        rename = os.rename
        def interrupt_stage(source, destination):
            if Path(destination) == self.target and Path(source).name == "staged":
                raise KeyboardInterrupt("simulated interruption")
            return rename(source, destination)
        with mock.patch.object(installer.os, "rename", side_effect=interrupt_stage):
            with self.assertRaises(KeyboardInterrupt):
                installer.install_archive(self.archive, self.digest, self.skills)
        self.assertEqual((self.target / "SKILL.md").read_text(), "local edits\n")
        self.assertEqual((self.target / "obsolete.py").read_text(), "old\n")

    def test_interrupt_immediately_after_stage_rename_restores_original_tree(self):
        installer = self.installer()
        self.old_install()
        rename = os.rename
        def interrupt_after_rename(source, destination):
            result = rename(source, destination)
            if Path(destination) == self.target and Path(source).name == "staged":
                raise KeyboardInterrupt("signal after rename completed")
            return result
        with mock.patch.object(installer.os, "rename", side_effect=interrupt_after_rename):
            with self.assertRaises(KeyboardInterrupt):
                installer.install_archive(self.archive, self.digest, self.skills)
        self.assertEqual((self.target / "SKILL.md").read_text(), "local edits\n")
        self.assertEqual((self.target / "obsolete.py").read_text(), "old\n")

    def test_symlink_target_or_nested_file_is_refused(self):
        installer = self.installer()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "sentinel").write_text("untouched")
        self.target.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            installer.install_archive(self.archive, self.digest, self.skills)
        self.target.unlink()
        self.old_install()
        (self.target / "linked").symlink_to(outside / "sentinel")
        with self.assertRaises(installer.InstallError):
            installer.install_archive(self.archive, self.digest, self.skills)
        self.assertEqual((outside / "sentinel").read_text(), "untouched")

    def test_symlink_skills_parent_is_refused(self):
        installer = self.installer()
        alias = self.root / "alias"
        alias.symlink_to(self.skills, target_is_directory=True)
        with self.assertRaises(installer.InstallError):
            installer.install_archive(self.archive, self.digest, alias)
        self.assertFalse(self.target.exists())

    def test_correct_hash_for_noncanonical_zip_does_not_authorize_install(self):
        installer = self.installer()
        self.old_install()
        with zipfile.ZipFile(self.archive, "a") as archive:
            archive.writestr("skill-forge/unreviewed.txt", "unexpected")
        digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        with self.assertRaises(installer.InstallError):
            installer.install_archive(self.archive, digest, self.skills)
        self.assertEqual((self.target / "SKILL.md").read_text(), "local edits\n")


if __name__ == "__main__":
    unittest.main()
