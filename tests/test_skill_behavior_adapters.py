import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


behavior = load_module("behavior_for_adapter_tests", REPO / "scripts/test-skill-behavior.py")
codex = load_module("codex_adapter_tests", REPO / "scripts/skill_behavior_adapters/codex.py")
claude = load_module("claude_adapter_tests", REPO / "scripts/skill_behavior_adapters/claude.py")


class SkillBehaviorAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="forgekit-adapter-tests-")
        self.root = Path(self.temp.name)
        self.workspace = self.root / "fixture"
        self.workspace.mkdir()
        (self.workspace / ".forgekit-skill-behavior-fixture").write_text("isolated\n", encoding="ascii")

    def tearDown(self):
        self.temp.cleanup()

    def fake_client(self, events, *, invalid=False):
        script = self.root / ("fake-invalid.py" if invalid else f"fake-{len(list(self.root.glob('fake-*.py')))}.py")
        output = "not-json" if invalid else "\n".join(json.dumps(event) for event in events)
        script.write_text(
            "import json, os, pathlib, sys\n"
            "prompt = sys.stdin.read() if '-' in sys.argv else (sys.argv[-1] if len(sys.argv) > 1 else '')\n"
            "observed = {'cwd': str(pathlib.Path.cwd()), 'argv': sys.argv[1:], 'prompt': prompt, "
            "'home': os.environ.get('HOME'), 'userprofile': os.environ.get('USERPROFILE'), "
            "'env_keys': sorted(os.environ), 'user_config_visible': (pathlib.Path(os.environ['HOME']) / '.codex/config.toml').exists()}\n"
            "pathlib.Path('adapter-observed.json').write_text(json.dumps(observed), encoding='utf-8')\n"
            f"print({output!r})\n",
            encoding="utf-8",
        )
        return script

    def invoke_fake(self, adapter, events, prompt="safe; no shell injection", invalid=False, auth_names=None):
        fake = self.fake_client(events, invalid=invalid)
        context = behavior.build_isolated_context(self.root / "runtime", auth_names)
        availability = {
            "available": True,
            "executable": str(fake),
            "command_prefix": [sys.executable, str(fake)],
            "version": "fake-1",
        }
        isolation = {
            "ready": True,
            "fixture_read_boundary": True,
            "network_external_actions_denied": True,
            "observed_flags": {},
        }
        with mock.patch.object(adapter, "probe", return_value=availability), mock.patch.object(
            adapter, "assess_isolation", return_value=isolation
        ):
            result = adapter.invoke(self.workspace, prompt, "implicit", context)
        observed = json.loads((self.workspace / "adapter-observed.json").read_text(encoding="utf-8"))
        (self.workspace / "adapter-observed.json").unlink()
        return result, observed, context

    def test_fake_clients_receive_isolated_roots_minimal_environment_and_safe_prompt(self):
        host_home = self.root / "host-home"
        (host_home / ".codex").mkdir(parents=True)
        (host_home / ".codex/config.toml").write_text("host config\n", encoding="utf-8")
        secrets = {
            "HOME": str(host_home),
            "USERPROFILE": str(host_home),
            "SSH_AUTH_SOCK": "host-ssh",
            "GITHUB_TOKEN": "host-github",
            "AWS_SECRET_ACCESS_KEY": "host-cloud",
            "OPENAI_API_KEY": "explicit-openai",
        }
        events = [
            {"type": "metadata", "model": "fake-model", "skill_source": {"name": "code-review", "path": "skills/code-review/SKILL.md"}},
            {"type": "tool_call", "tool": "Read", "path": "src/note.txt"},
        ]
        with mock.patch.dict(os.environ, secrets, clear=False):
            for adapter in (codex, claude):
                with self.subTest(adapter=adapter.__name__):
                    auth = ["OPENAI_API_KEY"] if adapter is codex else []
                    result, observed, context = self.invoke_fake(adapter, events, auth_names=auth)
                    self.assertEqual(str(self.workspace), observed["cwd"])
                    self.assertEqual(str(context["home"]), observed["home"])
                    self.assertEqual(str(context["home"]), observed["userprofile"])
                    self.assertFalse(observed["user_config_visible"])
                    for forbidden in ("SSH_AUTH_SOCK", "GITHUB_TOKEN", "AWS_SECRET_ACCESS_KEY"):
                        self.assertNotIn(forbidden, observed["env_keys"])
                    self.assertEqual("safe; no shell injection", observed["prompt"])
                    self.assertNotIn("shell=True", json.dumps(observed))
                    self.assertTrue(result["capabilities"]["isolation"])
                    self.assertEqual("fake-model", result["model"])
                    self.assertTrue(result["tool_trace"])
                    self.assertEqual("code-review", result["skill_source"][0]["name"])

    def test_isolation_unavailable_fails_closed_before_prompt_launch(self):
        fake = self.fake_client([])
        context = behavior.build_isolated_context(self.root / "runtime")
        availability = {"available": True, "executable": str(fake), "command_prefix": [sys.executable, str(fake)], "version": "fake"}
        for adapter in (codex, claude):
            with self.subTest(adapter=adapter.__name__), mock.patch.object(adapter, "probe", return_value=availability), mock.patch.object(
                adapter,
                "assess_isolation",
                return_value={"ready": False, "reason": "isolation capability unavailable: fixture read boundary"},
            ):
                result = adapter.invoke(self.workspace, "RUN_EXTERNAL", "implicit", context)
                self.assertFalse(result["available"])
                self.assertIn("isolation capability unavailable", result["reason"])
                self.assertFalse((self.workspace / "adapter-observed.json").exists())

    def test_evidence_capabilities_and_structured_parse_failure(self):
        variants = {
            "complete": [
                {"type": "metadata", "model": "m", "skill_source": {"name": "s", "path": "skills/s/SKILL.md"}},
                {"type": "tool_call", "tool": "Read"},
            ],
            "missing_model": [
                {"type": "metadata", "skill_source": {"name": "s", "path": "skills/s/SKILL.md"}},
                {"type": "tool_call", "tool": "Read"},
            ],
            "missing_trace": [{"type": "metadata", "model": "m", "skill_source": {"name": "s", "path": "skills/s/SKILL.md"}}],
            "missing_source": [{"type": "metadata", "model": "m"}, {"type": "tool_call", "tool": "Read"}],
        }
        for adapter in (codex, claude):
            for name, events in variants.items():
                with self.subTest(adapter=adapter.__name__, variant=name):
                    result, _, _ = self.invoke_fake(adapter, events)
                    self.assertEqual(name != "missing_model", result["capabilities"]["model"])
                    self.assertEqual(name != "missing_trace", result["capabilities"]["tool_trace"])
                    self.assertEqual(name != "missing_source", result["capabilities"]["skill_source"])
                    if name == "missing_source":
                        case = {
                            "authorization": "read_only", "allowed_write_paths": [], "expected_skill": "s",
                            "forbidden_skills": [], "forbidden_actions": [], "grader": {"type": "deterministic"},
                        }
                        classification, _ = behavior.classify(case, result, [])
                        self.assertEqual("GRADER_UNCERTAIN", classification)
            broken, _, _ = self.invoke_fake(adapter, [], invalid=True)
            self.assertIn("structured output parse failed", broken["adapter_error"])


class SkillBehaviorCliExitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="forgekit-behavior-cli-")
        self.root = Path(self.temp.name)
        (self.root / "scripts/skill_behavior_adapters").mkdir(parents=True)
        shutil.copyfile(REPO / "scripts/test-skill-behavior.py", self.root / "scripts/test-skill-behavior.py")
        shutil.copytree(REPO / "config", self.root / "config")
        shutil.copytree(REPO / "skills", self.root / "skills")
        (self.root / "VERSION").write_text("0.44.1\n", encoding="utf-8")
        fixture = self.root / "fixture"
        fixture.mkdir()
        (fixture / "note.txt").write_text("before\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def write_case(self, failure):
        expected_skill = "project-init" if failure in {"ROUTING_FAILURE", "GRADER_UNCERTAIN"} else ""
        case = {
            "id": "cli-case", "title": "CLI class", "client": "codex", "fixture": "fixture",
            "prompt": "safe prompt", "invocation_mode": "implicit", "expected_skill": expected_skill,
            "forbidden_skills": [], "authorization": "read_only", "allowed_write_paths": [],
            "forbidden_actions": [], "expected_behavior": "classify", "grader": {"type": "deterministic"}, "tags": ["test"],
            "materialized_skills": [expected_skill] if expected_skill else [],
            "evidence_requirements": {
                "routing": bool(expected_skill), "skill_source": bool(expected_skill),
                "write_behavior": True, "forbidden_actions": False,
                "model": False, "tool_trace": False,
            },
        }
        (self.root / "cases.json").write_text(json.dumps({"schema_version": 1, "cases": [case]}), encoding="utf-8")
        probe = "{'available': False, 'reason': 'missing', 'executable': None, 'version': None}" if failure == "ENVIRONMENT_UNAVAILABLE" else "{'available': True, 'executable': 'fake', 'version': '1'}"
        invoke_body = {
            "ADAPTER_ERROR": "raise RuntimeError('adapter broke')",
            "ROUTING_FAILURE": "return result(skill=[{'name':'other','path':'skills/other/SKILL.md'}], skill_cap=True)",
            "UNAUTHORIZED_WRITE": "(workspace/'outside.txt').write_text('x'); return result()",
            "BEHAVIOR_FAILURE": "return result(exit_code=7)",
            "GRADER_UNCERTAIN": "return result(skill=None, skill_cap=False)",
            "PASS": "return result()",
        }.get(failure, "return result()")
        module = (
            "def probe():\n    return " + probe + "\n"
            "def result(exit_code=0, skill=None, skill_cap=False):\n"
            "    return {'available': True, 'executable': 'fake', 'version': '1', 'model': None, 'tool_trace': None, "
            "'skill_source': skill, 'capabilities': {'model': False, 'tool_trace': False, 'skill_source': skill_cap, "
            "'structured_output': True, 'isolation': True}, 'evidence_unavailable_reason': {}, 'safe_command': ['fake'], "
            "'stdout': 'ok', 'stderr': '', 'exit_code': exit_code}\n"
            "def invoke(workspace, prompt, invocation_mode, context):\n    " + invoke_body + "\n"
        )
        (self.root / "scripts/skill_behavior_adapters/codex.py").write_text(module, encoding="utf-8")

    def test_seven_failure_classes_have_stable_cli_exit_codes(self):
        for failure, expected in behavior.EXIT_CODES.items():
            with self.subTest(failure=failure):
                self.write_case(failure)
                command = [
                    sys.executable, "-B", str(self.root / "scripts/test-skill-behavior.py"), "run",
                    "--repo-root", str(self.root), "--cases", "cases.json", "--temp-root", str(self.root.parent),
                ]
                result = subprocess.run(command, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False)
                self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
                record = json.loads(result.stdout)[0]
                self.assertEqual(failure, record["failure_class"])


if __name__ == "__main__":
    unittest.main()
