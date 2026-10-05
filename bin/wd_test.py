"""Tests for the wd CLI. Run: python3 -m unittest discover -s bin -p '*_test.py' -v"""

import importlib.machinery
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_WD_PATH = Path(__file__).with_name("wd")
_loader = importlib.machinery.SourceFileLoader("wd", str(_WD_PATH))
_spec = importlib.util.spec_from_loader("wd", _loader)
wd = importlib.util.module_from_spec(_spec)
sys.modules["wd"] = wd
_loader.exec_module(wd)

KEY_RE = r"[A-Z][A-Z0-9]+-[0-9]+"


def write_unit(root: Path, rel: str, **meta) -> Path:
    meta.setdefault("kind", "project")
    meta.setdefault("status", "active")
    meta.setdefault("title", rel.split("/")[-1])
    lines = ["---"] + [f"{k}: {wd.format_value(v)}" for k, v in meta.items()] + ["---", "", "# x", ""]
    if rel.endswith(".md"):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        d = root / rel
        d.mkdir(parents=True, exist_ok=True)
        path = d / "README.md"
        (d / "HANDOFF.md").write_text("# H\n\n## Status (2026-10-01)\n\nx\n\n## Next action\n\n1. Do the thing\n\n## Read first\n")
        (d / "LOG.md").write_text("# Log\n\n## 2026-10-01 — a — b\n\n## 2026-09-01 — a — c\n")
    path.write_text("\n".join(lines))
    return path


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


class FrontmatterTest(unittest.TestCase):
    def test_parses_scalars_lists_and_comments(self):
        meta = wd.parse_frontmatter("---\nkind: project  # c\njira: [A-1, B-2]\nbranches: []\nping_after:\n---\nbody")
        self.assertEqual(meta, {"kind": "project", "jira": ["A-1", "B-2"], "branches": [], "ping_after": ""})

    def test_no_frontmatter(self):
        self.assertIsNone(wd.parse_frontmatter("# title\n"))

    def test_update_replaces_and_appends_keeping_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "README.md"
            p.write_text("---\nkind: project\nbranches: []  # exact names\n---\n\nbody\n")
            wd.update_frontmatter(p, {"branches": ["b1"], "repos": ["webapp"]})
            text = p.read_text()
            self.assertIn("branches: [b1]  # exact names", text)
            self.assertIn("repos: [webapp]", text)
            self.assertTrue(text.endswith("\n---\n\nbody\n"))


class ResolveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write_unit(self.root, "projects/PROJ-100-search", kind="epic", jira=["PROJ-100"], repos=["webapp"])
        write_unit(self.root, "projects/PROJ-100-search/P1-indexer", jira=["PROJ-201", "PROJ-202"], repos=["webapp"])
        write_unit(self.root, "projects/PROJ-100-search/P2-ranking", jira=["PROJ-301"], repos=["webapp"],
                   branches=["feature/p2-work"])
        write_unit(self.root, "projects/PROJ-400-sso", jira=["PROJ-400"], repos=["webapp"])
        write_unit(self.root, "projects/old", jira=["PROJ-1"], status="done")
        write_unit(self.root, "projects/tools-cli", jira=[], repos=["tools"])
        write_unit(self.root, "reviews/PROJ-500_20260930.md", kind="review", jira=["PROJ-500"])
        self.units = wd.iter_units(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def names(self, found):
        return [u.rel for u in found]

    def test_branch_key_picks_subproject_over_epic(self):
        found = wd.resolve(self.units, "webapp", "feature/PROJ-201-indexer-harness", [], KEY_RE)
        self.assertEqual(self.names(found), ["projects/PROJ-100-search/P1-indexer"])

    def test_exact_branch_beats_key(self):
        found = wd.resolve(self.units, "webapp", "feature/p2-work", [], KEY_RE)
        self.assertEqual(self.names(found), ["projects/PROJ-100-search/P2-ranking"])

    def test_explicit_key_overrides_branch(self):
        found = wd.resolve(self.units, "webapp", "feature/PROJ-201-indexer-harness", ["PROJ-301"], KEY_RE)
        self.assertEqual(self.names(found), ["projects/PROJ-100-search/P2-ranking"])

    def test_explicit_name_fragment(self):
        found = wd.resolve(self.units, None, None, ["p2"], KEY_RE)
        self.assertEqual(self.names(found), ["projects/PROJ-100-search/P2-ranking"])

    def test_repo_only_tier_when_nothing_else(self):
        found = wd.resolve(self.units, "tools", "main", [], KEY_RE)
        self.assertEqual(self.names(found), ["projects/tools-cli"])

    def test_repo_only_match_must_be_unique(self):
        self.assertEqual(wd.resolve(self.units, "webapp", "stage", [], KEY_RE), [])

    def test_done_hidden_unless_all(self):
        self.assertEqual(wd.resolve(self.units, None, None, ["PROJ-1"], KEY_RE), [])
        self.assertEqual(self.names(wd.resolve(self.units, None, None, ["PROJ-1"], KEY_RE, include_done=True)),
                         ["projects/old"])

    def test_single_file_units_resolve_by_key(self):
        found = wd.resolve(self.units, None, None, ["PROJ-500"], KEY_RE)
        self.assertEqual(self.names(found), ["reviews/PROJ-500_20260930.md"])

    def test_no_match(self):
        self.assertEqual(wd.resolve(self.units, "other", "feature/x", [], KEY_RE), [])

    def test_epic_of(self):
        p1 = [u for u in self.units if u.rel.endswith("P1-indexer")][0]
        self.assertEqual(wd.epic_of(p1, self.units).rel, "projects/PROJ-100-search")

    def test_summaries(self):
        p1 = [u for u in self.units if u.rel.endswith("P1-indexer")][0]
        self.assertEqual(wd.last_log_date(p1), "2026-10-01")
        self.assertEqual(wd.next_action(p1), "Do the thing")
        review = [u for u in self.units if u.kind == "review"][0]
        self.assertEqual(wd.last_log_date(review), "2026-09-30")


class ExtractKeysTest(unittest.TestCase):
    def test_drops_dates_and_unknown_prefixes(self):
        text = "PROJ-9001-review-findings-20260529 proj-9002-pr-4242 webapp-2.3.1 TASK-1"
        self.assertEqual(wd.extract_keys(text, KEY_RE), {"PROJ-9001", "PROJ-9002", "PR-4242", "WEBAPP-2", "TASK-1"})
        self.assertEqual(wd.extract_keys(text, KEY_RE, "PROJ WEBAPP"), {"PROJ-9001", "PROJ-9002", "WEBAPP-2"})


class LintTest(unittest.TestCase):
    def test_reports_problems(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_unit(root, "projects/a", status="waiting", owner="me")
            (root / "projects/a/01-x.md").write_text("[ok](HANDOFF.md) [bad](missing.md) [web](https://x) `[c](nope.md)`\n"
                                                    "```\n[fenced](nope.md)\n```\n[line](LOG.md:12)\n")
            write_unit(root, "projects/b")
            (root / "projects/b/LOG.md").unlink()
            (root / "projects/a/archive").mkdir()
            (root / "projects/a/archive/old.md").write_text("[gone](gone.md)\n")
            problems = wd.lint(root, all_links=True)
            joined = "\n".join(problems)
            self.assertIn("unknown frontmatter keys ['owner']", joined)
            self.assertIn("waiting without ping_after", joined)
            self.assertIn("waiting without waiting_on", joined)
            self.assertIn("projects/b: missing LOG.md", joined)
            self.assertIn("broken link missing.md", joined)
            self.assertNotIn("nope.md", joined)
            self.assertNotIn("gone.md", joined)
            self.assertNotIn("LOG.md:12", joined)
            self.assertNotIn("missing.md", "\n".join(wd.lint(root, all_links=False)))

    def test_default_lint_checks_living_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_unit(root, "projects/a")
            (root / "projects/a/01-imported.md").write_text("[old](gone.md)\n")
            (root / "projects/a/HANDOFF.md").write_text("[bad](nope.md)\n## Next action\n")
            joined = "\n".join(wd.lint(root))
            self.assertIn("nope.md", joined)
            self.assertNotIn("gone.md", joined)
            self.assertIn("gone.md", "\n".join(wd.lint(root, all_links=True)))

    def test_clean_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_unit(Path(tmp), "projects/a")
            self.assertEqual(wd.lint(Path(tmp)), [])


class GitBackedTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.root = base / "workdocs"
        self.root.mkdir()
        self.repo = base / "webapp-2"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "feature/PROJ-201-x")
        git(self.repo, "remote", "add", "origin", "git@github.com:example/webapp.git")
        git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init")
        self.cfg = wd.load_config({"WORKDOCS_ROOT": str(self.root), "WORKDOCS_CONFIG": str(base / "nope"),
                                   "HOME": str(base)})

    def tearDown(self):
        self.tmp.cleanup()

    def test_git_context_uses_origin_basename(self):
        ctx = wd.git_context(self.repo)
        self.assertEqual((ctx.repo, ctx.branch), ("webapp", "feature/PROJ-201-x"))

    def test_not_a_repo(self):
        self.assertIsNone(wd.git_context(self.root))
        self.assertEqual(wd.session_start_lines(self.cfg, self.root), [])

    def test_session_start_lines(self):
        write_unit(self.root, "projects/E", kind="epic", jira=["PROJ-100"])
        write_unit(self.root, "projects/E/P1", jira=["PROJ-201"])
        lines = wd.session_start_lines(self.cfg, self.repo)
        self.assertIn(str(self.root / "projects/E/P1"), lines[0])
        self.assertIn("epic:", lines[1])

    def test_session_start_no_match_is_one_line(self):
        self.assertEqual(len(wd.session_start_lines(self.cfg, self.repo)), 1)

    def test_new_records_repo_and_feature_branch_but_not_trunk(self):
        old = os.getcwd()
        try:
            os.chdir(self.repo)
            args = wd.build_parser().parse_args(["new", "PROJ-201-indexer", "--title", "P1"])
            with redirect_stdout(io.StringIO()):
                self.assertEqual(wd.cmd_new(self.cfg, args), 0)
            meta = wd.parse_frontmatter((self.root / "projects/PROJ-201-indexer/README.md").read_text())
            self.assertEqual(meta["jira"], ["PROJ-201"])
            self.assertEqual(meta["repos"], ["webapp"])
            self.assertEqual(meta["branches"], ["feature/PROJ-201-x"])
            self.assertTrue((self.root / "projects/PROJ-201-indexer/LOG.md").is_file())
            self.assertNotIn("{{", (self.root / "projects/PROJ-201-indexer/README.md").read_text())

            git(self.repo, "checkout", "-q", "-b", "main")
            args = wd.build_parser().parse_args(["new", "tools-thing"])
            with redirect_stdout(io.StringIO()):
                wd.cmd_new(self.cfg, args)
            meta = wd.parse_frontmatter((self.root / "projects/tools-thing/README.md").read_text())
            self.assertEqual(meta["branches"], [])
        finally:
            os.chdir(old)

    def test_new_review_and_promote(self):
        args = wd.build_parser().parse_args(["new", "PROJ-500", "--kind", "review", "--slug", "PR review", "--no-git"])
        out = io.StringIO()
        with redirect_stdout(out):
            wd.cmd_new(self.cfg, args)
        review = Path(out.getvalue().strip())
        self.assertRegex(review.name, r"^PROJ-500_\d{8}_pr-review\.md$")
        args = wd.build_parser().parse_args(["promote", str(review), "--name", "PROJ-500-follow-up"])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(wd.cmd_promote(self.cfg, args), 0)
        project = self.root / "projects/PROJ-500-follow-up"
        self.assertFalse(review.exists())
        self.assertEqual(wd.parse_frontmatter((project / "README.md").read_text())["jira"], ["PROJ-500"])
        self.assertTrue(list(project.glob("01-review-*.md")))
        self.assertIn("promoted from", (project / "LOG.md").read_text())

    def test_link_refuses_trunk_and_records_branch(self):
        write_unit(self.root, "projects/P2", jira=["PROJ-301"])
        args = wd.build_parser().parse_args(["link", "P2", "--cwd", str(self.repo)])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(wd.cmd_link(self.cfg, args), 0)
        meta = wd.parse_frontmatter((self.root / "projects/P2/README.md").read_text())
        self.assertEqual(meta["branches"], ["feature/PROJ-201-x"])
        self.assertEqual(meta["repos"], ["webapp"])
        git(self.repo, "checkout", "-q", "-b", "stage")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(wd.cmd_link(self.cfg, args), 1)

    def test_checkpoint_commits_and_noops_when_clean(self):
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "t@t")
        git(self.root, "config", "user.name", "t")
        write_unit(self.root, "projects/a")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(wd.checkpoint(self.root, "first", auto=False), 0)
        self.assertEqual(wd._git(self.root, "status", "--porcelain"), "")
        self.assertEqual(wd.checkpoint(self.root, None, auto=True), 0)
        self.assertEqual(wd._git(self.root, "rev-list", "--count", "HEAD"), "1")

    def test_audit_classifies_entries(self):
        (self.repo / "PR_REVIEW_PROJ-400.md").write_text("x")
        (self.repo / "helper.ts").write_text("x")
        arts = self.repo / "ci-artifacts"
        arts.mkdir()
        for i in range(3):
            (arts / f"{i}.json").write_text("{}")
        entries = {e["path"].rstrip("/"): e for e in wd.audit_repo(self.repo)}
        self.assertEqual(entries["PR_REVIEW_PROJ-400.md"]["class"], "notes")
        self.assertEqual(entries["PR_REVIEW_PROJ-400.md"]["keys"], ["PROJ-400"])
        self.assertEqual(entries["helper.ts"]["class"], "code?")
        self.assertEqual(entries["ci-artifacts"]["class"], "artifacts")

    def test_hook_never_raises(self):
        args = wd.build_parser().parse_args(["hook", "session-start"])
        bad_cfg = dict(self.cfg, WORKDOCS_ROOT="/nonexistent/\0bad")
        with redirect_stdout(io.StringIO()), mock.patch.object(sys, "stdin", io.StringIO('{"cwd": "/"}')):
            self.assertEqual(wd.cmd_hook(bad_cfg, args), 0)

    def test_data_dir_mirrors_unit_path(self):
        write_unit(self.root, "projects/E/P2", kind="project")
        args = wd.build_parser().parse_args(["data", "P2"])
        out = io.StringIO()
        with redirect_stdout(out):
            wd.cmd_data(self.cfg, args)
        self.assertEqual(Path(out.getvalue().strip()), self.root / "data/E/P2")


def tool_line(name: str, sidechain: bool = False, **inp) -> str:
    return json.dumps({"type": "assistant", "isSidechain": sidechain,
                       "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}})


class StopHookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.root = base / "workdocs"
        write_unit(self.root, "projects/E", kind="epic")
        write_unit(self.root, "projects/E/P2")
        self.unit = self.root / "projects/E/P2"
        self.transcript = base / "t.jsonl"
        self.cfg = wd.load_config({"WORKDOCS_ROOT": str(self.root), "WORKDOCS_CONFIG": str(base / "nope"),
                                   "HOME": str(base), "NUDGE_AFTER": "5", "STATE_DIR": str(base / "state")})
        self.payload = {"session_id": "s1", "transcript_path": str(self.transcript), "cwd": str(base)}

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, lines):
        self.transcript.write_text("\n".join(lines) + "\n")

    def test_no_unit_touched_means_no_nudge(self):
        self.write([tool_line("Bash", command="ls")] * 10)
        self.assertIsNone(wd.stop_decision(self.cfg, self.payload))

    def test_nudges_after_threshold_then_resets(self):
        lines = [tool_line("Read", file_path=str(self.unit / "HANDOFF.md"))] + [tool_line("Bash", command="make")] * 6
        self.write(lines)
        reason = wd.stop_decision(self.cfg, self.payload)
        self.assertIn(str(self.unit), reason)
        self.assertIn("7 tool calls", reason)
        # the same point is not nudged twice
        self.assertIsNone(wd.stop_decision(self.cfg, self.payload))
        # five more calls after the nudge trigger it again
        self.write(lines + [tool_line("Bash", command="make")] * 5)
        self.assertIsNotNone(wd.stop_decision(self.cfg, self.payload))

    def test_docs_update_resets_counter(self):
        self.write([tool_line("Bash", command="make")] * 6
                   + [tool_line("Edit", file_path=str(self.unit / "LOG.md"), old_string="a", new_string="b")]
                   + [tool_line("Bash", command="make")] * 3)
        self.assertIsNone(wd.stop_decision(self.cfg, self.payload))

    def test_bash_writes_and_wd_checkpoint_count_as_docs_update(self):
        for cmd in (f"cat >> {self.unit}/LOG.md <<EOF", "wd checkpoint -m x"):
            self.write([tool_line("Read", file_path=str(self.unit / "README.md"))] + [tool_line("Bash", command="make")] * 6
                       + [tool_line("Bash", command=cmd)])
            self.assertIsNone(wd.stop_decision(self.cfg, dict(self.payload, session_id=cmd[:3])), cmd)

    def test_stop_hook_active_and_sidechain_and_bookkeeping_ignored(self):
        self.write([tool_line("Read", file_path=str(self.unit / "HANDOFF.md"))]
                   + [tool_line("Bash", sidechain=True, command="x")] * 10
                   + [tool_line("ToolSearch", query="x")] * 10)
        self.assertIsNone(wd.stop_decision(self.cfg, self.payload))
        self.write([tool_line("Read", file_path=str(self.unit / "HANDOFF.md"))] + [tool_line("Bash", command="x")] * 10)
        self.assertIsNone(wd.stop_decision(self.cfg, dict(self.payload, stop_hook_active=True)))

    def test_tilde_paths_and_relative_writes_after_cd(self):
        home = Path.home()
        tilde_unit = home / "wd-test-unit-does-not-exist"
        self.assertFalse(tilde_unit.exists())
        rel = self.unit.relative_to(home) if self.unit.is_relative_to(home) else None
        cmd = f"cd {self.unit} && cat >> LOG.md <<EOF"
        self.write([tool_line("Bash", command="make")] * 6 + [tool_line("Bash", command=cmd)])
        self.assertIsNone(wd.stop_decision(self.cfg, self.payload))
        if rel is not None:
            self.write([tool_line("Bash", command=f"cat ~/{rel}/HANDOFF.md")])
            act = wd.analyse_transcript(self.transcript, self.root, wd.iter_units(self.root))
            self.assertEqual(act.unit_dir, self.unit)

    def test_deepest_unit_wins_and_compact_lines_name_it(self):
        self.write([tool_line("Bash", command=f"cat {self.root}/projects/E/README.md {self.unit}/HANDOFF.md")])
        act = wd.analyse_transcript(self.transcript, self.root, wd.iter_units(self.root))
        self.assertEqual(act.unit_dir, self.unit)
        self.assertIn(str(self.unit), wd.compact_lines(self.cfg, self.payload, self.root)[0])

    def test_hook_stop_prints_block_json(self):
        self.write([tool_line("Read", file_path=str(self.unit / "HANDOFF.md"))] + [tool_line("Bash", command="x")] * 6)
        args = wd.build_parser().parse_args(["hook", "stop"])
        out = io.StringIO()
        with redirect_stdout(out), mock.patch.object(sys, "stdin", io.StringIO(json.dumps(self.payload))), \
                mock.patch.object(wd.select, "select", lambda r, w, x, t: (r, [], [])):
            wd.cmd_hook(self.cfg, args)
        self.assertEqual(json.loads(out.getvalue())["decision"], "block")


class KitTest(unittest.TestCase):
    def test_kit_prints_dir_with_conventions(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(wd.main(["kit"]), 0)
        self.assertTrue((Path(out.getvalue().strip()) / "CONVENTIONS.md").is_file())


class ConfigTest(unittest.TestCase):
    def test_file_values_env_override_and_expansion(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfgfile = Path(tmp) / "config"
            cfgfile.write_text("# c\nWORKDOCS_ROOT=$HOME/wdocs\nAUDIT_REPOS=$HOME/a:~/b\n")
            cfg = wd.load_config({"WORKDOCS_CONFIG": str(cfgfile), "HOME": "/h"})
            self.assertEqual(cfg["WORKDOCS_ROOT"], "/h/wdocs")
            self.assertEqual(cfg["WORKDOCS_DATA"], "/h/wdocs/data")
            self.assertEqual(cfg["AUDIT_REPOS"].split(":")[0], "/h/a")
            cfg = wd.load_config({"WORKDOCS_CONFIG": str(cfgfile), "HOME": "/h", "WORKDOCS_ROOT": "/x"})
            self.assertEqual(cfg["WORKDOCS_ROOT"], "/x")


if __name__ == "__main__":
    unittest.main()
