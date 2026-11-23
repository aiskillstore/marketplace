"""Resumable local-first orchestration for review-gated fine-cut workflows."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from draft_workspace import atomic

HERE = Path(__file__).resolve().parent
ENTRY = HERE / "fine_cut.py"
DEFAULT_CONFIG = Path(os.environ.get("CODEX_HOME", str(Path.home()/".codex"))) / "state/tiktok-drama-fine-cut/backend.json"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def signature(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def option(arguments, name):
    return arguments[arguments.index(name)+1]


class Runner:
    def __init__(self, args):
        self.args = args
        self.root = Path(args.workspace).resolve()
        self.state_path = self.root / "run.json"
        identity = {"draft": args.draft, "copy": args.copy, "episodes": args.episodes,
                    "reuse_copy": args.reuse_copy}
        if self.root.exists():
            if not self.state_path.is_file():
                raise ValueError("An existing run workspace must contain run.json; use a new directory for a new run")
            self.state = json.loads(self.state_path.read_bytes())
            if self.state.get("schema_version") != 1 or self.state.get("identity") != identity:
                raise ValueError("Run workspace belongs to a different draft, copy, episode selection or copy mode")
        else:
            self.root.mkdir(parents=True)
            self.state = {"schema_version": 1, "identity": identity, "status": "running",
                          "stages": {}, "outputs": {}, "created_at": time.time()}
            self.save()
        review_record = self.state.get("review_mode")
        selected_mode = review_record.get("mode") if isinstance(review_record, dict) else None
        requested_mode = getattr(args, "review_mode", None)
        if requested_mode not in (None, "assisted", "autonomous"):
            raise ValueError("--review-mode must be assisted or autonomous")
        if selected_mode and requested_mode and selected_mode != requested_mode:
            raise ValueError("Review mode cannot change within the same run; use a new workspace")

    def save(self):
        self.state["updated_at"] = time.time()
        atomic(self.state_path, json.dumps(self.state, ensure_ascii=False, indent=2).encode("utf-8"))

    def backend_signature(self):
        path = Path(self.args.config).resolve()
        scripts = ["fine_cut.py", "draft_workspace.py", "timeline_ops.py", "analyze_draft.py",
                   "plan_candidates.py", "preview_draft.py", "media_qc.py", "run_workflow.py",
                   "select_music_folder.ps1", "select_review_mode.ps1", "seam_review.py", "picture_range.py", "feedback_review.py", "automated_review.py",
                   "review_check.py", "audio_audition.py", "sfx_library.py"]
        return signature({"config": sha(path) if path.is_file() else None,
                          "scripts": {name: sha(HERE / name) for name in scripts}})

    def call(self, command, arguments):
        argv = [sys.executable, "-B", str(ENTRY), "--config", str(Path(self.args.config).resolve()),
                command, *map(str, arguments)]
        process = subprocess.run(argv, capture_output=True, timeout=self.args.stage_timeout,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        stdout = process.stdout.decode("utf-8", "replace").strip()
        stderr = process.stderr.decode("utf-8", "replace").strip()
        if process.returncode:
            raise ValueError(f"{command} failed: {(stderr or stdout)[-3000:]}")
        try:
            return json.loads(stdout)
        except ValueError as exc:
            raise ValueError(f"{command} returned non-JSON output: {stdout[-1000:]}") from exc

    def artifacts(self, paths):
        result = {}
        for value in paths:
            if value is None:
                continue
            path = Path(value).resolve()
            if not path.is_file():
                raise ValueError(f"Stage artifact is missing: {path}")
            result[str(path)] = sha(path)
        return result

    def stage(self, name, inputs, command, arguments, artifacts):
        stamp = signature({"inputs": inputs, "backend": self.backend_signature()})
        previous = self.state["stages"].get(name)
        if previous:
            if previous.get("signature") != stamp:
                raise ValueError(f"Stage {name} inputs changed; use a new run workspace for a new baseline")
            for path, expected in previous["artifacts"].items():
                if not Path(path).is_file() or sha(path) != expected:
                    raise ValueError(f"Stage {name} artifact changed or is missing: {path}")
            return previous["result"]
        self.state.update(status="running", current_stage=name)
        self.save()
        result = command() if callable(command) else self.call(command, arguments)
        artifact_paths = artifacts(result) if callable(artifacts) else artifacts
        record = {"signature": stamp, "result": result, "artifacts": self.artifacts(artifact_paths),
                  "completed_at": time.time()}
        self.state["stages"][name] = record
        self.state["outputs"][name] = result
        self.state["current_stage"] = None
        self.save()
        return result

    def finish(self, status, **extra):
        music = self.state.get("music", {})
        music_dir = music.get("path") if music.get("status") == "selected" else None
        review_record = self.state.get("review_mode")
        review_mode = review_record.get("mode") if isinstance(review_record, dict) else None
        self.state.update(status=status, current_stage=None, music_dir=music_dir,
                          review_mode=review_mode, **extra)
        self.save()
        return {"status": status, "workspace": str(self.root), "draft": self.args.draft,
                "copy": self.args.copy, "music_dir": music_dir, "review_mode": review_mode, **extra}

    def package(self, episodes, destination):
        if destination.exists():
            raise ValueError("Commit input directory must be new; recover the failed package stage explicitly")
        destination.mkdir()
        files = []
        for episode in episodes:
            edited = self.state["stages"][f"apply:{episode['id']}"]["result"]
            source = Path(edited["output"]).resolve(strict=True)
            if sha(source) != edited["output_sha256"]:
                raise ValueError(f"Edited JSON changed before packaging: {source}")
            target = destination / f"{episode['id']}.json"
            shutil.copyfile(source, target)
            if sha(target) != edited["output_sha256"]:
                raise ValueError(f"Packaged JSON checksum failed: {target}")
            files.append(str(target))
        return {"files": files, "sha256": {path: sha(path) for path in files}}

    def plans(self, episodes):
        result = {}
        for raw in self.args.plan or []:
            if "=" in raw:
                name, value = raw.split("=", 1)
            elif len(episodes) == 1:
                name, value = episodes[0]["name"], raw
            else:
                raise ValueError("With multiple episodes, use --plan '实际集名=计划路径' for every plan")
            matches = [episode for episode in episodes if episode["name"] == name]
            if len(matches) != 1 or name in result:
                raise ValueError(f"Plan episode is unknown or repeated: {name!r}")
            path = Path(value).expanduser().resolve(strict=True)
            if not path.is_file():
                raise ValueError(f"Plan is not a file: {path}")
            result[name] = path
        if self.args.transcript and len(episodes) != 1:
            raise ValueError("--transcript currently requires a single-episode run")
        return result

    def start_music_selection(self):
        selected = self.state.get("music", {}).get("path")
        supplied = Path(self.args.music_dir).expanduser().resolve() if self.args.music_dir else None
        if supplied is not None and (not supplied.is_dir()):
            raise ValueError(f"Music directory is not accessible: {supplied}")
        if selected and Path(selected).is_dir():
            if supplied is not None and supplied != Path(selected):
                raise ValueError("Music directory cannot change within the same run; use a new workspace")
            return None
        if supplied is not None:
            self.state["music"] = {"status": "selected", "path": str(supplied), "source": "--music-dir"}
            self.save()
            return None
        if os.name != "nt":
            self.state["music"] = {"status": "unavailable", "reason": "not_windows"}
            return None
        argv = ["powershell.exe", "-NoProfile", "-STA", "-File", str(HERE / "select_music_folder.ps1")]
        try:
            return subprocess.Popen(argv, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            self.state["music"] = {"status": "unavailable", "reason": "dialog_failed", "detail": str(exc)}
            return None

    def resolve_music_selection(self, process):
        current = self.state.get("music", {})
        if current.get("status") == "selected" and current.get("path") and Path(current["path"]).is_dir():
            return current
        result = current
        if process is not None:
            stdout, stderr = process.communicate()
            if process.returncode:
                result = {"status": "unavailable", "reason": "dialog_failed",
                          "detail": stderr.decode("utf-8", "replace")[-1200:]}
            else:
                try:
                    result = json.loads(stdout.decode("utf-8-sig", "replace").strip())
                except ValueError as exc:
                    result = {"status": "unavailable", "reason": "invalid_dialog_result", "detail": str(exc)}
        if result.get("status") == "selected" and result.get("path"):
            path = Path(result["path"]).expanduser().resolve()
            if path.is_dir():
                result = {"status": "selected", "path": str(path), "source": "folder_dialog"}
        else:
            result = {"status": result.get("status", "unavailable"),
                      "reason": result.get("reason") or result.get("status", "unavailable"),
                      "detail": result.get("detail", "")}
        self.state["music"] = result
        self.save()
        return result

    def start_review_mode_selection(self):
        current = self.state.get("review_mode")
        selected = current.get("mode") if isinstance(current, dict) else None
        if not hasattr(self.args, "review_mode"):
            self.state["review_mode"] = {"status": "selected", "mode": "assisted", "source": "compatibility_default"}
            self.save()
            return None
        requested = getattr(self.args, "review_mode", None)
        if selected:
            if requested and requested != selected:
                raise ValueError("Review mode cannot change within the same run; use a new workspace")
            return None
        if requested in ("assisted", "autonomous"):
            self.state["review_mode"] = {"status": "selected", "mode": requested, "source": "--review-mode"}
            self.save()
            return None
        if os.name != "nt":
            self.state["review_mode"] = {"status": "unavailable", "reason": "not_windows"}
            self.save()
            return None
        argv = ["powershell.exe", "-NoProfile", "-STA", "-File", str(HERE / "select_review_mode.ps1")]
        try:
            return subprocess.Popen(argv, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as exc:
            self.state["review_mode"] = {"status": "unavailable", "reason": "dialog_failed", "detail": str(exc)}
            self.save()
            return None

    def resolve_review_mode_selection(self, process):
        current = self.state.get("review_mode")
        if not isinstance(current, dict):
            current = {}
        if current.get("status") == "selected" and current.get("mode") in ("assisted", "autonomous"):
            return current
        result = current
        if process is not None:
            stdout, stderr = process.communicate()
            if process.returncode:
                result = {"status": "unavailable", "reason": "dialog_failed",
                          "detail": stderr.decode("utf-8", "replace")[-1200:]}
            else:
                try:
                    result = json.loads(stdout.decode("utf-8-sig", "replace").strip())
                except ValueError as exc:
                    result = {"status": "unavailable", "reason": "invalid_dialog_result", "detail": str(exc)}
        mode = result.get("mode")
        if result.get("status") == "selected" and mode in ("assisted", "autonomous"):
            result = {"status": "selected", "mode": mode, "source": result.get("source", "dialog")}
        else:
            result = {"status": result.get("status", "unavailable"),
                      "reason": result.get("reason") or result.get("status", "unavailable"),
                      "detail": result.get("detail", "")}
        self.state["review_mode"] = result
        self.save()
        return result

    def review_mode_required(self, result):
        return self.finish("review_mode_required", review_mode_selection=result,
                           next="Choose assisted or autonomous review when prompted, or resume with --review-mode assisted|autonomous")

    def music_required(self, result):
        return self.finish("music_selection_required", music=result,
                           next="Select a local BGM folder when prompted, or resume with --music-dir <absolute accessible folder>")

    def run(self):
        try:
            return self.execute()
        except Exception as exc:
            self.state.update(status="failed", error=str(exc))
            self.save()
            raise

    def execute(self):
        args = self.args
        music_process = self.start_music_selection()
        inspection = self.root / "inspection"
        start = self.stage("start", {"request": self.state["identity"]}, "start",
                           ["--draft", args.draft, "--episodes", *args.episodes, "--workspace", inspection],
                           [inspection / "inspection.json"])
        if start.get("status") != "ready":
            raise ValueError(f"Start did not resolve every requested episode: {start.get('episode_errors') or start.get('next')}")
        episodes = start["episodes"]
        plans = self.plans(episodes)
        music = self.resolve_music_selection(music_process)
        if music.get("status") != "selected":
            return self.music_required(music)
        review_process = self.start_review_mode_selection()
        review_selection = self.resolve_review_mode_selection(review_process)
        if review_selection.get("status") != "selected":
            return self.review_mode_required(review_selection)
        review_mode = review_selection["mode"]
        if self.state["stages"].get("commit") and not args.commit:
            raise ValueError("This workspace already has a committed transaction; resume with --commit or use a new workspace")
        removed = [episode["name"] for episode in episodes
                   if episode["name"] not in plans and self.state["stages"].get(f"apply:{episode['id']}")]
        if removed:
            raise ValueError(f"Plans cannot be removed after apply; use a new workspace: {removed}")
        if args.reuse_copy:
            located = self.stage("locate_copy", {"copy": args.copy}, "list", ["--draft", args.copy], [])
            copy_root = Path(located["path"])
            copy_result = {"status": "existing_copy", "path": str(copy_root)}
        else:
            clone_work = self.root / "clone"
            copy_result = self.stage("clone", {"source": args.draft, "copy": args.copy}, "clone",
                                     ["--source", args.draft, "--copy", args.copy, "--workspace", clone_work],
                                     [clone_work / "clone.json"])
            copy_root = Path(copy_result["path"])
        snapshot_work = self.root / "snapshot"
        snapshot = self.stage("snapshot", {"copy": copy_result, "episodes": episodes}, "snapshot",
                              ["--source", args.draft, "--copy", args.copy,
                               "--episodes", *[episode["name"] for episode in episodes], "--workspace", snapshot_work],
                              [snapshot_work / "snapshot.json"])
        baseline = Path(snapshot["baseline"])
        reviews = {}
        quality_reviews = {}
        precommit = {}
        missing = []
        for episode in episodes:
            name, tid = episode["name"], episode["id"]
            episode_root = self.root / "episodes" / tid
            baseline_json = baseline / f"{tid}.json"
            analysis_work = episode_root / "analysis"
            analysis = self.stage(f"analyze:{tid}", {"baseline": sha(baseline_json)}, "analyze",
                                  ["--input", baseline_json, "--copy-root", copy_root, "--workspace", analysis_work],
                                  [analysis_work / "analysis.json", analysis_work / "prepared.json"])
            if name not in plans:
                candidate_work = episode_root / "candidates"
                arguments = ["--input", baseline_json, "--analysis", analysis["analysis"]]
                if args.transcript:
                    arguments += ["--transcript", str(Path(args.transcript).resolve(strict=True))]
                arguments += ["--output", candidate_work]
                candidate = self.stage(f"propose:{tid}", {"baseline": sha(baseline_json),
                                       "analysis": sha(analysis["analysis"]),
                                       "transcript": sha(args.transcript) if args.transcript else None}, "propose", arguments,
                                       [candidate_work / "review.json", candidate_work / "plan.json"])
                reviews[name] = candidate["review"]
                missing.append(name)
                continue
            edited_work = episode_root / "edited"
            edited = self.stage(f"apply:{tid}", {"baseline": sha(baseline_json), "plan": sha(plans[name])}, "apply",
                                ["--input", baseline_json, "--plan", plans[name], "--output", edited_work],
                                [edited_work / "draft_content.json", edited_work / "report.json"])
            preview_work = episode_root / "preview"
            preview_args = ["--input", edited["output"], "--copy-root", copy_root, "--workspace", preview_work,
                            "--size", args.size]
            if args.software:
                preview_args.append("--software")
            preview = self.stage(f"preview:{tid}", {"edited": edited["output_sha256"],
                                 "size": args.size, "software": args.software}, "preview", preview_args,
                                 [preview_work / "preview.json", preview_work / "preview.mp4"])
            qc_report = episode_root / "precommit-qc.json"
            frames = episode_root / "precommit-frames"
            qc = self.stage(f"qc:{tid}", {"edited": edited["output_sha256"], "preview": preview["preview_sha256"]}, "qc",
                            ["--input", edited["output"], "--preview", preview_work,
                             "--edit-report", edited_work / "report.json", "--frames-dir", frames, "--report", qc_report],
                            [qc_report])
            precommit[name] = {"qc": str(qc_report), "technical_status": qc["technical_status"],
                               "issues": qc["issues"], "preview": preview["preview"]}
            seam_work = episode_root / "seam-review"
            seam_args = ["scan","--baseline",baseline_json,"--input",edited["output"],
                              "--edit-report",edited_work/"report.json","--copy-root",copy_root,"--preview",preview_work,"--output",seam_work]
            if review_mode == "autonomous":
                seam_args.append("--no-html")
            seam = self.stage(f"seams:{tid}", {"baseline":sha(baseline_json),"edited":edited["output_sha256"],"preview":preview["preview_sha256"],"review_mode":review_mode},
                              "seam-review", seam_args,
                              [seam_work/"seam_review.json"] + ([] if review_mode == "autonomous" else [seam_work/"decisions.template.json",seam_work/"review.html"]))
            from picture_range import required_ranges
            picture_ranges = []
            edit_report = json.loads((edited_work/'report.json').read_text(encoding='utf-8'))
            for requirement in required_ranges(edit_report, seam.get('primary_video_track_id')):
                range_work = episode_root/'picture-ranges'/requirement['range_id']
                range_args = ["inspect-range","--input",edited["output"],
                     "--edit-report",edited_work/'report.json',"--copy-root",copy_root,"--preview",preview_work,
                     "--range-id",requirement['range_id'],"--start-us",requirement['start_us'],
                     "--end-us",requirement['end_us'],"--primary-video-track-id",requirement['track_id'],
                     "--output",range_work]
                if review_mode == "autonomous":
                    range_args.append("--no-html")
                inspected = self.stage(f"picture_range:{tid}:{requirement['range_id']}",
                    {"edited":edited["output_sha256"],"edit_report":sha(edited_work/'report.json'),
                     "preview":preview["preview_sha256"],"range":requirement,"review_mode":review_mode},
                    "seam-review", range_args,
                    [range_work/'range_review.json'] + ([] if review_mode == "autonomous" else [range_work/'decisions.template.json',range_work/'review.html']))
                picture_ranges.append(inspected)
            precommit[name]['picture_ranges'] = picture_ranges
            new_sfx = self.state["stages"][f"apply:{tid}"]["result"].get("sfx_count",0)
            audition_manifest = None
            if review_mode == "autonomous" and new_sfx:
                audition_work = episode_root / "automated-audition"
                audition = self.stage(f"audition:{tid}", {"edited":edited["output_sha256"], "preview":preview["preview_sha256"], "review_mode":review_mode},
                    "audio-audition", ["--input",edited["output"],"--preview",preview_work,
                     "--edit-report",edited_work/"report.json","--output",audition_work,"--full-timeline","--no-html"],
                    [audition_work/"audition.json"])
                audition_manifest = audition.get("manifest")
            quality_template = episode_root / "quality-review.template.json"
            if review_mode == "assisted" and not quality_template.is_file():
                self.call("review-check", ["--input",edited["output"],"--edit-report",edited_work/"report.json", "--qc",qc_report,
                          "--seam-scan",seam_work/"seam_review.json","--template",quality_template])
            supplied = {}
            for raw in args.review or []:
                if "=" not in raw:raise ValueError("Use --review 实际集名=审阅文件.json")
                ep, path = raw.split("=",1)
                if ep in supplied:raise ValueError("Duplicate review episode: "+ep)
                supplied[ep]=path
            declared_sfx = any(beat.get("sound_action")=="sfx" for beat in edited.get("beat_events",[]))
            if review_mode == "autonomous":
                auto_template = episode_root / "automated-review.template.json"
                auto_evidence = episode_root / "automated-evidence"
                auto_args = ["build", "--input", edited["output"], "--edit-report", edited_work/"report.json",
                             "--qc", qc_report, "--seam-scan", seam_work/"seam_review.json",
                             "--preview", preview["preview"], "--output", auto_template, "--evidence-dir", auto_evidence]
                for inspected in picture_ranges:
                    auto_args += ["--range-report", inspected["report"]]
                if audition_manifest:
                    auto_args += ["--audition", audition_manifest]
                self.stage(f"automated_review_evidence:{tid}", {"edited":edited["output_sha256"], "qc":sha(qc_report),
                    "seam":sha(seam_work/"seam_review.json"), "ranges":[x.get("report") for x in picture_ranges],
                    "audition":audition_manifest, "review_mode":review_mode}, "automated-review", auto_args,
                    lambda result: [auto_template, auto_evidence/"overview-keyframes.json", *result.get("keyframe_sheets", [])])
                if name in supplied:
                    validate_args = ["validate", "--review", supplied[name], "--input", edited["output"],
                        "--edit-report", edited_work/"report.json", "--qc", qc_report,
                        "--seam-scan", seam_work/"seam_review.json"]
                    for inspected in picture_ranges:
                        validate_args += ["--range-report", inspected["report"]]
                    if audition_manifest:
                        validate_args += ["--audition", audition_manifest]
                    quality_reviews[name] = self.call("automated-review", validate_args)
                else:
                    evidence_result = self.state["stages"][f"automated_review_evidence:{tid}"]["result"]
                    quality_reviews[name] = {"status":"needs_agent_review", "template":str(auto_template),
                        "keyframe_sheets":evidence_result.get("keyframe_sheets", []), "seam_scan":str(seam_work/"seam_review.json"),
                        "picture_ranges":picture_ranges, "audition_manifest":audition_manifest,
                        "next":"Inspect the bound evidence, complete automated-review.template.json as automated-review.json, then resume with --review and --commit"}
            elif not new_sfx and not declared_sfx and not seam.get("required_review_count",0) and not picture_ranges:
                quality_reviews[name] = {"status":"passed","scope":"No new SFX, video joins or bridge/reframe ranges in this round"}
            elif name in supplied:
                quality_reviews[name] = self.call("review-check", ["--input",edited["output"],"--edit-report",edited_work/"report.json",
                    "--qc",qc_report,"--seam-scan",seam_work/"seam_review.json","--review",supplied[name]])
            else:
                quality_reviews[name] = {"status":"needs_review","template":str(quality_template),"seams":seam,
                                         "picture_ranges":picture_ranges}
        if missing:
            return self.finish("awaiting_plan", missing_plans=missing, reviews=reviews,
                               precommit=precommit, next="Review candidates, approve plans, then resume with --plan")
        commit_input = self.root / "commit-input"
        packaged_files = [commit_input / f"{episode['id']}.json" for episode in episodes]
        package = self.stage("package", {episode["id"]: self.state["stages"][f"apply:{episode['id']}"]["result"]["output_sha256"]
                                        for episode in episodes},
                             lambda: self.package(episodes, commit_input), [], packaged_files)
        if not args.commit:
            review_pending = any(item.get("status") != "passed" for item in quality_reviews.values())
            status = "awaiting_agent_review" if review_mode == "autonomous" and review_pending else "awaiting_commit"
            if status == "awaiting_agent_review":
                next_step = "Inspect the generated keyframe/audio evidence, complete the bound automated review JSON, then resume with --review 实际集名=文件 and --commit"
            elif review_mode == "autonomous":
                next_step = "Automated review passed; resume with --commit to write and verify the independent copy"
            else:
                next_step = "Complete seam/bridge/reframe decisions and native SFX solo/AB review, then resume with --review 实际集名=文件 and --commit"
            return self.finish(status, precommit=precommit, quality_reviews=quality_reviews, next=next_step)
        if any(item.get("status") != "passed" for item in quality_reviews.values()):
            status = "awaiting_agent_review" if review_mode == "autonomous" else "awaiting_quality_review"
            return self.finish(status,precommit=precommit,quality_reviews=quality_reviews,
                               next="Resolve the concrete review items and resume with the bound --review files; --commit alone does not complete review")
        transaction = snapshot_work / "transaction.json"
        commit_args = ["--workspace", snapshot_work, "--edited", commit_input]
        if args.register_media:
            commit_args.append("--register-media")
        committed = self.stage("commit", {"package": package, "snapshot": sha(snapshot_work / "snapshot.json"),
                                         "register_media": args.register_media}, "commit", commit_args, [transaction])
        verified = self.stage("verify", {"transaction": sha(transaction)}, "verify",
                              ["--workspace", snapshot_work], [transaction])
        final = {}
        for episode in episodes:
            name, tid = episode["name"], episode["id"]
            episode_root = self.root / "episodes" / tid
            readback_work = episode_root / "final-readback"
            readback = self.stage(f"readback:{tid}", {"transaction": sha(transaction)}, "readback",
                                  ["--workspace", snapshot_work, "--episode", name,
                                   "--report", episode_root / "edited" / "report.json", "--output", readback_work],
                                  [readback_work / "readback.json", readback_work / f"{tid}.json", readback_work / "report.json"])
            preview_work = episode_root / "final-preview"
            preview_args = ["--input", readback["json"], "--copy-root", copy_root,
                            "--workspace", preview_work, "--size", args.size]
            if args.software:
                preview_args.append("--software")
            preview = self.stage(f"final_preview:{tid}", {"readback": readback["sha256"],
                                 "size": args.size, "software": args.software}, "preview", preview_args,
                                 [preview_work / "preview.json", preview_work / "preview.mp4"])
            qc_report = episode_root / "final-qc.json"
            frames = episode_root / "final-frames"
            qc = self.stage(f"final_qc:{tid}", {"readback": readback["sha256"], "preview": preview["preview_sha256"]}, "qc",
                            ["--input", readback["json"], "--preview", preview_work,
                             "--edit-report", readback["report"], "--frames-dir", frames, "--report", qc_report], [qc_report])
            final[name] = {"json": readback["json"], "report": readback["report"],
                           "preview": preview["preview"], "qc": str(qc_report),
                           "technical_status": qc["technical_status"], "issues": qc["issues"]}
        final_status = "completed_needs_review" if any(row["technical_status"]!="passed" for row in final.values()) else "completed"
        if review_mode == "autonomous":
            next_step = ("Resolve final technical QC findings on affected sections and repeat final verification"
                         if final_status != "completed" else "Editable copy passed final technical QC and is ready for delivery")
            listening_scope = "No human listening or normal-speed viewing is claimed; see the hash-bound autonomous review record"
        else:
            next_step = "Review final QC and perform/listen to any remaining editorial or native-playback checks"
            listening_scope = "See hash-bound per-event declarations in quality_reviews; software does not independently verify listening"
        return self.finish(final_status, committed=committed, verified=verified, final=final,
                           quality_reviews=quality_reviews, subjective_audio_listening=listening_scope, next=next_step)


def package(arguments):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", required=True)
    parser.add_argument("--copy", required=True)
    parser.add_argument("--episodes", nargs="+", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--music-dir", help="Accessible local BGM folder selected for this run; omit to open the folder dialog")
    parser.add_argument("--review-mode", choices=("assisted", "autonomous"),
                        help="Review workflow; omit to choose assisted or autonomous in a Windows dialog")
    parser.add_argument("--plan", action="append", help="Approved plan path for one episode, or 实际集名=计划路径")
    parser.add_argument("--transcript")
    parser.add_argument("--review", action="append", help="实际集名=hash-bound SFX/seam/QC review JSON; agent review does not require new user permission")
    parser.add_argument("--commit", action="store_true", help="Write to the independent copy only after precommit QC")
    parser.add_argument("--reuse-copy", action="store_true", help="Snapshot an existing registered copy instead of cloning")
    parser.add_argument("--register-media", action=argparse.BooleanOptionalAction, default=True,
                        help="Register new media on commit (default: true; use --no-register-media only when unnecessary)")
    parser.add_argument("--software", action="store_true")
    parser.add_argument("--size", default="540x960")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--stage-timeout", type=float, default=3600)
    return parser.parse_args(arguments)


def main():
    sys.dont_write_bytecode = True
    args = package(sys.argv[1:])
    if args.stage_timeout <= 0:
        raise SystemExit("--stage-timeout must be positive")
    try:
        print(json.dumps(Runner(args).run(), ensure_ascii=False, indent=2))
    except Exception as exc:
        raise SystemExit(json.dumps({"status": "failed", "error": str(exc), "workspace": args.workspace},
                                    ensure_ascii=False))


if __name__ == "__main__":
    main()
