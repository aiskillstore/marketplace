import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from aspeed import cli  # noqa: E402
from aspeed.adapters import claude_code, codex  # noqa: E402
from aspeed.analyze import AgentAgg, CatStats  # noqa: E402
from aspeed.attribute import attribute  # noqa: E402
from aspeed.classify import classify  # noqa: E402
from aspeed.estimate import cpu_ratio, project, project_all, validate_sensitivity  # noqa: E402
from aspeed.hardware import Hardware  # noqa: E402
from aspeed.models import Event  # noqa: E402
from aspeed.scores import estimate_from_specs, filter_catalog, find_cpu, load_catalog, load_json, resolve_baseline  # noqa: E402

SENTINEL = "SECRET_SENTINEL_42"


class ClassifyTests(unittest.TestCase):
    def check(self, command, category):
        self.assertEqual(classify(command)[0], category, command)

    def test_basic_categories(self):
        self.check("pytest -q", "test")
        self.check("cargo build --release", "build_compile")
        self.check("npm install", "dependency_install")
        self.check("git status", "vcs_local")
        self.check("git push origin main", "network")
        self.check("python script.py", "script_runtime")
        self.check("ls -la", "file_search_read")
        self.check("Start-Sleep -Seconds 5", "wait")
        self.check("docker build .", "container_vm")

    def test_shell_wrappers_are_unwrapped(self):
        self.check(["powershell.exe", "-Command", "corepack pnpm --filter @x test"], "test")
        self.check(["bash", "-lc", "pytest"], "test")
        self.check("wsl.exe -d Ubuntu --exec bash -lc 'cargo test'", "test")
        self.check("wsl --shutdown", "container_vm")

    def test_chained_commands_pick_the_heaviest_part(self):
        self.check("cd foo && npm run build", "build_compile")
        self.check("cd foo && git status && npm test", "test")

    def test_quoted_and_heredoc_text_is_not_executed(self):
        self.check("cat <<'EOF'\nnpm test\nEOF", "file_search_read")
        self.assertNotEqual(classify("echo 'npm test'")[0], "test")

    def test_empty_input(self):
        self.assertEqual(classify("")[0], "system_query")
        self.assertEqual(classify(None)[0], "system_query")


class AttributeTests(unittest.TestCase):
    def test_overlap_is_split_evenly(self):
        evs = [Event(0, 10, "tool", "test"), Event(5, 15, "tool", "test")]
        out = attribute(evs, 300)
        self.assertAlmostEqual(sum(b + x for _, b, x in out), 15.0)
        self.assertAlmostEqual(out[0][1], 7.5)

    def test_cap_moves_the_rest_to_excess(self):
        out = attribute([Event(0, 1000, "tool", "test")], 300)
        self.assertAlmostEqual(out[0][1], 300.0)
        self.assertAlmostEqual(out[0][2], 700.0)


class EstimateTests(unittest.TestCase):
    def setUp(self):
        self.sens = load_json("sensitivity.json")
        self.base = {"gb6_single": 1000, "gb6_multi": 3000}

    def agg(self):
        a = AgentAgg("x")
        a.cats["build_compile"] = CatStats(n=1, base=100.0)
        return a

    def test_same_hardware_changes_nothing(self):
        r = project(self.agg(), self.base, self.base, 1.0, self.sens, 1)
        self.assertAlmostEqual(r["total_speedup"], 1.0, places=3)

    def test_double_speed_formula(self):
        target = {"gb6_single": 2000, "gb6_multi": 6000}
        r = project(self.agg(), self.base, target, 1.0, self.sens, 1)
        cpu, disk = 0.75, 0.07
        expected = 100 * (1 - cpu - disk + cpu / 2 + disk)
        self.assertAlmostEqual(r["tool_new_s"], expected, places=1)

    def test_model_time_never_changes(self):
        a = self.agg()
        a.model_s = 900.0
        target = {"gb6_single": 4000, "gb6_multi": 12000}
        r = project(a, self.base, target, 1.0, self.sens, 2)
        self.assertLess(r["total_speedup"], 1000 / 900 + 1)
        self.assertGreater(r["total_new_s"], 900.0)

    def test_slower_target_is_slower(self):
        slow = {"gb6_single": 500, "gb6_multi": 1500}
        self.assertLess(cpu_ratio(self.base, slow, 0.5), 1.0)

    def test_extremely_fast_hardware_never_produces_negative_time(self):
        validate_sensitivity(self.sens)
        fast = {"gb6_single": 10 ** 12, "gb6_multi": 10 ** 12}
        for category in self.sens["categories"]:
            a = AgentAgg("x", model_s=50.0)
            a.cats[category] = CatStats(n=1, base=100.0)
            for result in project_all(a, self.base, fast, 10 ** 9, self.sens).values():
                self.assertGreaterEqual(result["tool_new_s"], 0)
                self.assertGreaterEqual(result["total_new_s"], a.model_s)

    def test_invalid_sensitivity_is_rejected(self):
        for cpu, disk, mt in (([0.9] * 3, [0.2] * 3, 0.5), ([float("nan")] * 3, [0.0] * 3, 0.5),
                              ([-0.1] * 3, [0.0] * 3, 0.5), ([0.1], [0.0] * 3, 0.5),
                              ([0.1] * 3, [0.0] * 3, 2)):
            with self.subTest(cpu=cpu, disk=disk, mt=mt), self.assertRaises(ValueError):
                validate_sensitivity({"categories": {"other_tool": {"cpu": cpu, "disk": disk, "mt": mt}}})


class ArgumentTests(unittest.TestCase):
    def test_invalid_numbers_and_agents_fail_before_scanning(self):
        for args in (["--current-gb6", "0", "100"], ["--custom-target", "CPU", "-1", "100"],
                     ["--custom-target", "CPU", "oops", "100"], ["--days", "nan"], ["--days", "0"],
                     ["--cap", "-1"], ["--max-stall", "inf"], ["--max-human", "-1"], ["--agents", "typo"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    cli.parse_args(args)
                self.assertEqual(raised.exception.code, 2)

    def test_bad_custom_sensitivity_does_not_write_a_report(self):
        with tempfile.TemporaryDirectory() as d:
            config, out = Path(d) / "bad.json", Path(d) / "out"
            config.write_text('{"categories": {}}', encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()), patch.object(cli, "scan") as scan:
                self.assertEqual(cli.main(["--sensitivity", str(config), "--out", str(out)]), 2)
            scan.assert_not_called()
            self.assertFalse(out.exists())


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.cpus = load_json("cpu_scores.json")["cpus"]

    def test_suffix_does_not_match_base_chip(self):
        self.assertIsNone(find_cpu("Apple M4 Pro", self.cpus))
        self.assertIsNone(find_cpu("Apple M4 Ultra", self.cpus))
        self.assertEqual(find_cpu("Apple M4 Pro (12-CPU 16-GPU)", self.cpus)["name"], "Apple M4 Pro (12-CPU 16-GPU)")
        self.assertIsNone(find_cpu("Apple M6 (16-CPU)", self.cpus))
        self.assertIsNone(find_cpu("Intel Core i7-4770Imaginary", self.cpus))

    def test_vendor_decoration_is_ignored(self):
        self.assertEqual(find_cpu("Intel(R) Core(TM) i5-1235U", self.cpus)["name"], "Intel Core i5-1235U")

    def test_unknown_cpu_with_stand_in(self):
        def without_measurement(name, data_dir=None):
            data = load_json(name, data_dir)
            if name == "cpu_scores.json":
                data["cpus"] = [c for c in data["cpus"] if c["name"] != "AMD Ryzen 5 3450U"]
            return data
        with patch("aspeed.scores.load_json", side_effect=without_measurement):
            cpu, source, note, unc = resolve_baseline("AMD Ryzen 5 3450U with Radeon Vega Mobile Gfx")
        self.assertEqual(cpu["name"], "Intel Core i5-8250U")
        self.assertEqual(source, "proxy")
        self.assertIn("stand-in", note)
        self.assertGreater(unc, 1.0)

    def test_unknown_cpu_without_stand_in(self):
        cpu, source, _, _ = resolve_baseline("Acme Imaginary 9000")
        self.assertIsNone(cpu)
        self.assertEqual(source, "")

    def test_spec_estimate_scales_with_threads(self):
        s8, _, unc = estimate_from_specs(8)
        s16, _, _ = estimate_from_specs(16)
        self.assertGreater(s16["gb6_multi"], s8["gb6_multi"])
        self.assertEqual(s16["gb6_single"], s8["gb6_single"])
        self.assertGreater(unc, 1.0)

    def test_uncertainty_widens_the_range_only(self):
        sens = load_json("sensitivity.json")
        a = AgentAgg("x")
        a.cats["build_compile"] = CatStats(n=1, base=100.0)
        base = {"gb6_single": 1000, "gb6_multi": 3000}
        target = {"gb6_single": 2000, "gb6_multi": 6000}
        plain = project_all(a, base, target, 1.0, sens, 1.0)
        wide = project_all(a, base, target, 1.0, sens, 1.3)
        self.assertAlmostEqual(plain["expected"]["total_speedup"], wide["expected"]["total_speedup"])
        self.assertLess(wide["conservative"]["total_speedup"], plain["conservative"]["total_speedup"])
        self.assertGreater(wide["optimistic"]["total_speedup"], plain["optimistic"]["total_speedup"])


def iso(t):
    return datetime.fromtimestamp(t, timezone.utc).isoformat().replace("+00:00", "Z")


class ClaudeAdapterTests(unittest.TestCase):
    def test_model_tool_and_human_time(self):
        t0 = 1_800_000_000
        rows = [
            {"type": "user", "timestamp": iso(t0), "message": {"content": "hello " + SENTINEL}},
            {"type": "assistant", "timestamp": iso(t0 + 5), "message": {"content": [
                {"type": "tool_use", "id": "a", "name": "Bash", "input": {"command": "pytest " + SENTINEL}}]}},
            {"type": "user", "timestamp": iso(t0 + 15), "message": {"content": [
                {"type": "tool_result", "tool_use_id": "a", "content": "ok"}]}},
            {"type": "assistant", "timestamp": iso(t0 + 20), "message": {"content": [{"type": "text", "text": "done"}]}},
            {"type": "user", "timestamp": iso(t0 + 50), "message": {"content": "next"}},
            {"type": "assistant", "timestamp": iso(t0 + 52), "message": {"content": [{"type": "text", "text": "ok"}]}},
        ]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.jsonl"
            p.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
            s = claude_code.parse_session(p)
        self.assertAlmostEqual(s.model_s, 5 + 5 + 2)
        self.assertAlmostEqual(s.human_s, 30)
        self.assertEqual(len(s.events), 1)
        self.assertEqual(s.events[0].category, "test")
        self.assertAlmostEqual(s.events[0].wall, 10)

    def test_ask_user_question_counts_as_human_time(self):
        t0 = 1_800_000_000
        rows = [
            {"type": "user", "timestamp": iso(t0), "message": {"content": "go"}},
            {"type": "assistant", "timestamp": iso(t0 + 2), "message": {"content": [
                {"type": "tool_use", "id": "q", "name": "AskUserQuestion", "input": {}}]}},
            {"type": "user", "timestamp": iso(t0 + 62), "message": {"content": [
                {"type": "tool_result", "tool_use_id": "q", "content": "A"}]}},
        ]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.jsonl"
            p.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
            s = claude_code.parse_session(p)
        self.assertAlmostEqual(s.human_s, 60)
        self.assertEqual(s.events, [])


def codex_rows(base=1000.0):
    def item(kind, a, b, **extra):
        return {"type": "event_msg", "payload": {
            "type": "item_completed", "turn_id": "T1", "started_at_ms": int(a * 1000),
            "completed_at_ms": int(b * 1000), "item": {"type": kind, **extra}}}
    return [
        {"type": "event_msg", "payload": {"type": "task_started", "turn_id": "T1", "started_at": base}},
        item("Reasoning", base, base + 3),
        item("CommandExecution", base + 3, base + 13, command=["powershell.exe", "-Command", "pytest " + SENTINEL],
             duration={"secs": 10, "nanos": 0}),
        item("AgentMessage", base + 13, base + 14),
        {"type": "event_msg", "payload": {"type": "task_complete", "turn_id": "T1", "started_at": base,
                                          "completed_at": base + 14, "duration_ms": 14000}},
    ]


class CodexAdapterTests(unittest.TestCase):
    def write(self, d, name="rollout-x.jsonl"):
        p = Path(d) / name
        p.write_text("\n".join(json.dumps(r) for r in codex_rows()), encoding="utf-8")
        return p

    def test_turn_split(self):
        with tempfile.TemporaryDirectory() as d:
            s = codex.parse_session(self.write(d))
        self.assertAlmostEqual(s.model_s, 4.0, places=2)
        self.assertEqual(s.events[0].category, "test")
        self.assertAlmostEqual(s.events[0].wall, 10.0, places=2)
        self.assertEqual(s.stalled_s, 0)

    def test_compressed_file_reads_the_same(self):
        try:
            from compression import zstd
        except ImportError:
            self.skipTest("compression.zstd needs Python 3.14+")
        with tempfile.TemporaryDirectory() as d:
            plain = self.write(d)
            packed = Path(d) / "rollout-y.jsonl.zst"
            packed.write_bytes(zstd.compress(plain.read_bytes()))
            a, b = codex.parse_session(plain), codex.parse_session(packed)
        self.assertAlmostEqual(a.model_s, b.model_s)
        self.assertEqual(len(a.events), len(b.events))

    def test_plain_file_wins_over_its_compressed_twin(self):
        with tempfile.TemporaryDirectory() as d:
            self.write(d, "rollout-z.jsonl")
            (Path(d) / "rollout-z.jsonl.zst").write_bytes(b"")
            found = codex.find_sessions([Path(d)])
        self.assertEqual([p.name for p in found], ["rollout-z.jsonl"])


class EndToEndPrivacyTests(unittest.TestCase):
    def setUp(self):
        hardware = patch.object(cli, "detect", return_value=Hardware(cpu_name="Apple M1", cores=8, threads=8, ram_gb=16, disk_class="nvme"))
        hardware.start()
        self.addCleanup(hardware.stop)

    def test_no_prompt_or_command_text_reaches_any_output(self):
        t0 = 1_800_000_000
        rows = [
            {"type": "user", "timestamp": iso(t0), "message": {"content": "prompt " + SENTINEL}},
            {"type": "assistant", "timestamp": iso(t0 + 2), "message": {"content": [
                {"type": "tool_use", "id": "a", "name": "Bash", "input": {"command": "pytest " + SENTINEL}}]}},
            {"type": "user", "timestamp": iso(t0 + 40), "message": {"content": [
                {"type": "tool_result", "tool_use_id": "a", "content": SENTINEL}]}},
            {"type": "assistant", "timestamp": iso(t0 + 44), "message": {"content": [{"type": "text", "text": SENTINEL}]}},
        ]
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / SENTINEL
            src.mkdir()
            (src / "s.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
            codex_src = Path(d) / "codex" / SENTINEL
            codex_src.mkdir(parents=True)
            (codex_src / (SENTINEL + ".jsonl")).write_text("\n".join(json.dumps(r) for r in codex_rows(t0)), encoding="utf-8")
            out = Path(d) / "out"
            with contextlib.redirect_stdout(io.StringIO()) as printed, contextlib.redirect_stderr(io.StringIO()):
                code = cli.main([
                    "--agents", "claude,codex", "--claude-dir", str(src), "--codex-dir", str(codex_src), "--out", str(out), "--lang", "en",
                    "--current-cpu", "Apple M1", "--current-gb6", "2163", "8217", "--current-disk", "nvme", "--json",
                ])
            self.assertEqual(code, 0)
            self.assertNotIn(SENTINEL, printed.getvalue())
            names = sorted(p.name for p in out.iterdir())
            self.assertEqual(names, ["cpu-catalog.json", "report.html", "report.md", "summary.json"])
            for p in out.iterdir():
                self.assertNotIn(SENTINEL, p.read_text(encoding="utf-8"), p.name)
            data = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertGreater(data["agents"]["all"]["tool_s"], 30)
            self.assertEqual(data["agents"]["codex"]["sessions"], 1)
            html = (out / "report.html").read_text(encoding="utf-8")
            self.assertNotIn(" ", html)
            self.assertIn('id="data"', html)


class NeverAskTests(unittest.TestCase):
    def setUp(self):
        hardware = patch.object(cli, "detect", return_value=Hardware(cpu_name="Apple M1", cores=8, threads=8, ram_gb=16, disk_class="nvme"))
        hardware.start()
        self.addCleanup(hardware.stop)

    def run_cli(self, extra):
        t0 = 1_800_000_000
        rows = [
            {"type": "user", "timestamp": iso(t0), "message": {"content": "go"}},
            {"type": "assistant", "timestamp": iso(t0 + 2), "message": {"content": [
                {"type": "tool_use", "id": "a", "name": "Bash", "input": {"command": "cargo build"}}]}},
            {"type": "user", "timestamp": iso(t0 + 62), "message": {"content": [
                {"type": "tool_result", "tool_use_id": "a", "content": "ok"}]}},
            {"type": "assistant", "timestamp": iso(t0 + 66), "message": {"content": [{"type": "text", "text": "done"}]}},
        ]
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        d = temp.name
        src = Path(d) / "in"
        src.mkdir()
        (src / "s.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        out = Path(d) / "out"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = cli.main(["--agents", "claude", "--claude-dir", str(src), "--out", str(out), "--lang", "en", "--no-html"] + extra)
        return code, out

    def test_unknown_cpu_still_produces_a_report(self):
        code, out = self.run_cli(["--current-cpu", "Acme Imaginary 9000", "--current-disk", "nvme"])
        self.assertEqual(code, 0)
        data = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(data["baseline"]["source"], "estimated")
        self.assertTrue(any("approximate" in n for n in data["notes"]))
        self.assertTrue(data["targets"])

    def test_unknown_target_fails_without_substitution(self):
        code, out = self.run_cli(["--current-cpu", "Apple M1", "--target", "Acme Imaginary 9000"])
        self.assertEqual(code, 2)
        self.assertFalse((out / "summary.json").exists())


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()
        cls.cpus = cls.catalog["cpus"]

    def test_generations_and_platforms_are_present(self):
        self.assertGreater(len(self.cpus), 1500)
        for gen in range(4, 15):
            self.assertTrue(filter_catalog(self.cpus, vendor="Intel", generation=f"Core {gen}th gen"))
        for gen in ("Zen 1", "Zen+", "Zen 2", "Zen 3", "Zen 3+", "Zen 4", "Zen 5"):
            self.assertTrue(filter_catalog(self.cpus, vendor="AMD", generation=gen), gen)
        for gen in range(1, 7):
            self.assertTrue(filter_catalog(self.cpus, vendor="Apple", generation=f"M{gen}"))
        self.assertGreater(len(filter_catalog(self.cpus, vendor="Apple", generation="Intel Mac")), 80)
        self.assertEqual(len({c["id"] for c in self.cpus}), len(self.cpus))

    def test_scores_keep_version_and_identity(self):
        scores = load_json("cpu_scores.json")["cpus"]
        for c in scores:
            self.assertEqual(c["benchmark"], "Geekbench 6")
            self.assertGreater(c["gb6_single"], 0)
            self.assertGreater(c["gb6_multi"], 0)
            self.assertTrue(c["source_url"].startswith("https://"))
            self.assertIn(c["id"], {r["id"] for r in self.cpus})
        self.assertTrue(any(not c.get("gb6_single") for c in self.cpus))

    def test_apple_core_counts_and_legacy_intel_numbers(self):
        by_name = {c["name"]: c for c in self.cpus}
        self.assertEqual(by_name["Apple M1 (8-CPU)"]["cpu_cores"], 8)
        self.assertEqual(by_name["Apple M2 (8-CPU)"]["cpu_cores"], 8)
        self.assertEqual(by_name["Apple M6 (12-CPU)"]["cpu_cores"], 12)
        self.assertNotIn("Intel Core i7-950", by_name)
        self.assertNotIn("Intel Core i3-530", by_name)
        self.assertFalse(any(" processor " in c["name"] for c in self.cpus))

    def test_curated_tiers_keep_exact_configurations(self):
        targets, primary = cli.build_targets(cli.parse_args(["--target-set", "tiers"]), self.cpus, "en")
        self.assertEqual(len(targets), 8)
        self.assertEqual(targets[primary][1], "mainstream")

    def test_all_scored_targets_are_default(self):
        args = cli.parse_args([])
        targets, primary = cli.build_targets(args, self.cpus, "en")
        self.assertEqual({c["id"] for c, _, _ in targets}, {c["id"] for c in self.cpus if c.get("gb6_single")})
        self.assertGreater(len(targets), 100)
        self.assertLess(primary, len(targets))

    def test_mac_reference_is_explicit_and_matches_cpu(self):
        by_id = {c["id"]: c for c in self.cpus}
        mapped = [c for c in self.cpus if c.get("cpu_reference_id")]
        self.assertTrue(mapped)
        for c in mapped:
            self.assertEqual(c["score_status"], "cpu-reference-gb6")
            cpu = by_id[c["cpu_reference_id"]]
            self.assertEqual((c["gb6_single"], c["gb6_multi"]), (cpu["gb6_single"], cpu["gb6_multi"]))

    def test_listing_needs_no_transcripts_or_hardware(self):
        with patch.object(cli, "detect", side_effect=AssertionError("should not detect")), contextlib.redirect_stdout(io.StringIO()) as output:
            code = cli.main(["--list-cpus", "--vendor", "Apple", "--generation", "M2", "--json"])
        self.assertEqual(code, 0)
        rows = json.loads(output.getvalue())["cpus"]
        self.assertTrue(rows)
        self.assertTrue(all(c["vendor"] == "Apple" and c["generation"] == "M2" for c in rows))

    def test_missing_scores_do_not_create_projections(self):
        missing = next(c for c in self.cpus if not c.get("gb6_single"))
        with self.assertRaises(ValueError):
            cli.build_targets(cli.parse_args(["--target", missing["name"]]), self.cpus, "en")
        with self.assertRaises(ValueError):
            cli.build_targets(cli.parse_args(["--search", "Imaginary-9000"]), self.cpus, "en")


class SourceHygieneTests(unittest.TestCase):
    def test_no_raw_line_separators_in_sources(self):
        for p in (ROOT / "scripts").rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            self.assertNotIn(chr(0x2028), text, p.name)
            self.assertNotIn(chr(0x2029), text, p.name)


if __name__ == "__main__":
    unittest.main()
