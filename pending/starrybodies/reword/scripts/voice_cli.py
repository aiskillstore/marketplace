"""Explicit local commands for a private Reword voice collection."""

from pathlib import Path
import json

from voice_context import DESTINATIONS, compact_voice, render_style_card, resolve_context


COLLECTION_ACTIONS = {"onboard", "create", "add", "feedback", "learning", "refine", "update", "status", "export", "rollback", "forget"}


def register_collection_commands(actions):
    actions.add_parser("onboard", help="Show the optional voice-building invitation")
    create = actions.add_parser("create", help="Create a private voice collection")
    create.add_argument("collection")
    create.add_argument("--name", required=True)
    create.add_argument("--learn", action="store_true", help="Remember future author corrections when the host supplies them")
    add = actions.add_parser("add", help="Add deliberately chosen writing, with provenance")
    add.add_argument("collection")
    add.add_argument("file")
    add.add_argument("--role", choices=("authored", "reference"), default="authored")
    add.add_argument("--destination", choices=DESTINATIONS, default="general")
    add.add_argument("--label", default="")
    feedback = actions.add_parser("feedback", help="Record author preferences or an author revision")
    feedback.add_argument("collection")
    feedback.add_argument("--kind", choices=("preference", "revision", "accept", "reject"), required=True)
    feedback.add_argument("--destination", choices=DESTINATIONS, default="general")
    feedback.add_argument("--reason", default="")
    feedback.add_argument("--prefer", action="append", default=[])
    feedback.add_argument("--avoid", action="append", default=[])
    feedback.add_argument("--draft")
    feedback.add_argument("--final")
    feedback.add_argument("--automatic", action="store_true")
    learning = actions.add_parser("learning", help="Pause or enable ongoing feedback capture")
    learning.add_argument("collection")
    consent = learning.add_mutually_exclusive_group(required=True)
    consent.add_argument("--enabled", dest="enabled", action="store_true")
    consent.add_argument("--disabled", dest="enabled", action="store_false")
    refine = actions.add_parser("refine", help="Build a bounded voice-learning request; makes no model call")
    refine.add_argument("collection")
    refine.add_argument("--destination", choices=DESTINATIONS, default="general")
    refine.add_argument("--max-evidence-chars", type=int, default=12000)
    update = actions.add_parser("update", help="Apply a validated voice proposal to its exact learning request")
    update.add_argument("collection")
    update.add_argument("request")
    update.add_argument("proposal")
    update.add_argument("--automatic", action="store_true")
    status = actions.add_parser("status", help="Inspect coverage, pending evidence and profile versions")
    status.add_argument("collection")
    status.add_argument("--details", action="store_true", help="Include evidence labels and IDs, without their prose")
    export = actions.add_parser("export", help="Export a compact profile or portable voice card without the corpus")
    export.add_argument("collection")
    export.add_argument("--destination", choices=DESTINATIONS, default="general")
    export.add_argument("--format", choices=("profile", "card"), default="profile")
    rollback = actions.add_parser("rollback", help="Restore a previous voice profile, keeping author evidence")
    rollback.add_argument("collection")
    rollback.add_argument("--version", type=int, required=True)
    forget = actions.add_parser("forget", help="Remove evidence and invalidate derived profiles")
    forget.add_argument("collection")
    forget.add_argument("evidence_id")


def _read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON field: {key}")
            result[key] = value
        return result

    def invalid(value):
        raise ValueError(f"Invalid JSON constant: {value}")

    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=invalid)


def render_voice_card(profile, destination="general"):
    resolved = resolve_context(destination, preferences=profile.get("contexts", {}))
    card = compact_voice(profile, destination=resolved)
    parts = ["Use this chosen writing voice. " + render_style_card(resolved)]
    for key, value in card.get("traits", {}).items():
        parts.append(key.replace("_", " ").capitalize() + ": " + value)
    for key, label in (("preferences", "Prefer"), ("avoid", "Avoid")):
        for value in card.get(key, []):
            parts.append(label + ": " + value)
    parts.append("Apply these habits to wording, order and rhythm. Use only the current brief's facts; style evidence supplies no biography or claims.")
    return "\n".join(parts)


def handle_collection_command(args, *, read_text):
    from voice_store import (add_feedback, add_sample, create_collection, forget_evidence,
                             load_collection, rollback_profile, save_collection, set_learning)
    from voice_learning import (apply_learning_proposal, build_learning_request,
                                collection_status, compile_profile)

    action = args.voice_action
    if action == "onboard":
        return (Path(__file__).resolve().parents[1] / "assets/voice_onboarding.txt").read_text(encoding="utf-8").strip()
    if action == "create":
        store = create_collection(args.name, learning_enabled=args.learn)
        save_collection(args.collection, store, create=True)
        return {"saved": args.collection, "status": collection_status(store)}
    store = load_collection(args.collection)
    if action == "status":
        result = collection_status(store)
        result["available_versions"] = [value["version"] for value in store["history"]]
        if args.details:
            result["samples"] = [{key: sample[key] for key in ("id", "role", "destination", "label")}
                                 | {"characters": len(sample["text"])} for sample in store["samples"]]
            result["feedback"] = [{"id": value["id"], "kind": value["kind"], "destination": value["destination"]}
                                  for value in store["feedback"]]
        return result
    if action == "refine":
        return build_learning_request(store, args.destination, max_evidence_chars=args.max_evidence_chars)
    if action == "export":
        profile = compile_profile(store, args.destination)
        return render_voice_card(profile, args.destination) if args.format == "card" else profile
    if action == "add":
        updated = add_sample(store, read_text(args.file), role=args.role, destination=args.destination, label=args.label)
    elif action == "feedback":
        if args.draft == args.final == "-":
            raise ValueError("Supply at least one file for draft/final; stdin can be read only once.")
        updated = add_feedback(store, kind=args.kind, destination=args.destination, reason=args.reason,
            prefer=args.prefer, avoid=args.avoid, draft=read_text(args.draft) if args.draft else "",
            final=read_text(args.final) if args.final else "", automatic=args.automatic)
    elif action == "learning":
        updated = set_learning(store, args.enabled)
    elif action == "update":
        updated = apply_learning_proposal(store, _read_json(args.request), _read_json(args.proposal), automatic=args.automatic)
    elif action == "rollback":
        updated = rollback_profile(store, args.version)
    elif action == "forget":
        updated = forget_evidence(store, args.evidence_id)
    else:
        raise ValueError("Unknown voice collection action.")
    save_collection(args.collection, updated, expected_revision=store["revision"])
    return {"saved": args.collection, "changed": updated != store, "status": collection_status(updated)}
