import subprocess
import sys
from pathlib import Path

import pytest

# Tests live in the skill; the tool is in the sibling scripts/ dir. Put that on the path
# so `import decisions` loads the tool directly — no symlink needed.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


@pytest.fixture
def publish_upstream():
    """Point a synthetic tree's `origin/main` at whatever it holds right now.

    `warn_upstream_collisions` compares the working tree against the ref already on
    disk, so a test of it needs a real ref to read — there is nothing to stub. This
    makes tmp_path a git work tree and moves refs/remotes/origin/main onto a commit of
    its current contents; the caller then edits the tree into the branch state. No
    remote is involved and nothing is fetched, which is the point: the check never
    fetches either. Call it again to move the ref.

    Identity and signing are forced per invocation rather than read from the
    developer's config, or a machine that signs every commit cannot run these.
    """

    def publish(root: Path) -> None:
        def git(*args: str) -> None:
            subprocess.run(
                ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
            )

        if not (root / ".git").exists():
            git("init", "--quiet")
        git("add", "--all")
        git(
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "--message",
            "upstream",
        )
        git("update-ref", "refs/remotes/origin/main", "HEAD")

    return publish
