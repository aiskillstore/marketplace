"""Contract tests that pin this skill's task graph and CI workflow."""
import pathlib
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
CHECK_JOBS = ["validate", "lint-writing", "lint-code", "evals"]
REQUIRED_TASKS = ["ci", "test"] + CHECK_JOBS


def load_tasks(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle).get("tasks", {})


class TestTaskGraph(unittest.TestCase):
    def setUp(self):
        self.tasks = load_tasks(SKILL_DIR / "mise.toml")

    def test_every_required_task_exists(self):
        for name in REQUIRED_TASKS:
            self.assertIn(name, self.tasks, f"missing task: {name}")

    def test_ci_invokes_every_check_job(self):
        steps = self.tasks["ci"]["run"]
        self.assertIsInstance(steps, list)
        self.assertEqual(steps[0], "mise run test")
        joined = " ".join(steps)
        for job in CHECK_JOBS:
            self.assertIn(f"mise run {job}", joined)

    def test_every_task_has_a_description(self):
        for name, task in self.tasks.items():
            self.assertTrue(task.get("description"), f"{name} needs one")

    def test_each_check_job_runs_one_command(self):
        for job in CHECK_JOBS:
            run = self.tasks[job]["run"]
            self.assertIsInstance(run, str, f"{job} must run one command")
            self.assertIn("python3 scripts/", run)


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        path = SKILL_DIR / ".github" / "workflows" / "ci.yml"
        self.assertTrue(path.is_file(), "missing .github/workflows/ci.yml")
        self.text = path.read_text(encoding="utf-8")

    def test_workflow_runs_only_the_single_entry_point(self):
        run_lines = [line.strip() for line in self.text.splitlines()
                     if line.strip().startswith("- run:")]
        self.assertEqual(run_lines, ["- run: mise run ci"])

    def test_workflow_triggers_on_push_and_pull_request(self):
        self.assertIn("push:", self.text)
        self.assertIn("pull_request:", self.text)


if __name__ == "__main__":
    unittest.main()
