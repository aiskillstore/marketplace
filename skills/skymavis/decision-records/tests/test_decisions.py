"""
Tests for scripts/decisions.py — the decision-records registry tool.

Option B: the tool takes an injectable `root` (the docs/ dir), so every test runs
against a synthetic tree under tmp_path and never touches the real repo.
"""

import subprocess

import decisions
import pytest


# ── fixture helpers ─────────────────────────────────────────────────────────
def record_text(
    counter,
    typ,
    title,
    *,
    body="",
    status="accepted",
    relates_to="[]",
    supersedes="null",
    superseded_by="null",
    summary="one-line summary",
    tags="[]",
):
    return (
        f'---\nid: "{counter}"\ntitle: {title}\ntype: {typ}\nstatus: {status}\n'
        f"summary: {summary}\ntags: {tags}\nrelates_to: {relates_to}\n"
        f"supersedes: {supersedes}\nsuperseded_by: {superseded_by}\n---\n\n"
        f"# {counter} — {title}\n\n{body}\n"
    )


def place(root, counter, typ, title, *, lifecycle="decisions", subdir=None, **kw):
    d = (
        root / "decisions" / "accepted" / (subdir or typ)
        if lifecycle == "decisions"
        else root / "decisions" / lifecycle
    )
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{counter}-{title}.md"
    p.write_text(record_text(counter, typ, title, **kw), encoding="utf-8")
    return p


def place_draft(
    root,
    did,
    typ,
    title,
    *,
    status="draft",
    relates_to="[]",
    supersedes="null",
    superseded_by="null",
    body="",
):
    d = root / "decisions" / "drafts"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{did}-{title}.md"
    p.write_text(
        f"---\nid: {did}\ntitle: {title}\ntype: {typ}\nstatus: {status}\n"
        f"relates_to: {relates_to}\nsupersedes: {supersedes}\nsuperseded_by: {superseded_by}\n"
        f"---\n\n# {did} — {title}\n\n{body}\n",
        encoding="utf-8",
    )
    return p


def write_threat_model(root, body):
    root.mkdir(parents=True, exist_ok=True)
    (root / "threat-model.md").write_text(f"# Threat Model\n\n{body}\n", encoding="utf-8")


@pytest.fixture
def root(tmp_path):
    """docs/ with contiguous accepted 0001..0003; 0003 (security) cites 0001 & 0002."""
    docs = tmp_path / "docs"
    place(docs, "0001", "architecture", "alpha")
    place(docs, "0002", "architecture", "beta")
    place(docs, "0003", "security", "gamma", body="builds on `0001` and `0002`.")
    return docs


@pytest.fixture
def built(root):
    assert decisions.main(["build", "--relink"], root=root) == 0
    return root


# ── front-matter parsing: block scalars ─────────────────────────────────────
def test_folded_scalar_summary_joins_lines():
    text = (
        '---\nid: "0001"\nsummary: >-\n  A summary written as a folded block scalar\n'
        "  that continues across several indented lines.\nstatus: accepted\n---\n\nbody\n"
    )
    fm = decisions.parse_front_matter(text)
    assert fm["summary"] == (
        "A summary written as a folded block scalar that continues across several indented lines."
    )
    assert fm["status"] == "accepted"  # the field after the block is still parsed


def test_literal_scalar_summary_preserves_newlines():
    text = '---\nid: "0001"\nsummary: |\n  line one\n  line two\nstatus: accepted\n---\n\nbody\n'
    fm = decisions.parse_front_matter(text)
    assert fm["summary"] == "line one\nline two"


def test_block_scalar_with_no_continuation_is_empty():
    text = '---\nid: "0001"\nsummary: >-\nstatus: accepted\n---\n\nbody\n'
    fm = decisions.parse_front_matter(text)
    assert fm["summary"] == ""
    assert fm["status"] == "accepted"


def test_folded_summary_renders_in_index(root):
    p = root / "decisions/accepted/architecture/0001-alpha.md"
    p.write_text(
        p.read_text().replace(
            "summary: one-line summary",
            "summary: >-\n  A summary written as a folded block scalar\n  across two lines.",
        )
    )
    assert decisions.main(["build"], root=root) == 0
    index = (root / "decisions" / "INDEX.md").read_text()
    assert "A summary written as a folded block scalar across two lines." in index
    assert ">-" not in index


def test_check_flags_bare_scalar_indicator_summary(root):
    p = root / "decisions/accepted/architecture/0001-alpha.md"
    p.write_text(p.read_text().replace("summary: one-line summary", 'summary: ">-"'))
    assert decisions.main(["check"], root=root) == 1


# ── build / render ──────────────────────────────────────────────────────────
def test_build_writes_index_sorted(root):
    assert decisions.main(["build"], root=root) == 0
    index = (root / "decisions" / "INDEX.md").read_text()
    assert index.index("0001") < index.index("0002") < index.index("0003")
    assert "(accepted/architecture/0001-alpha.md)" in index
    assert "| architecture |" in index and "| security |" in index


def test_index_empty_when_no_decisions(tmp_path):
    docs = tmp_path / "docs"
    place_draft(docs, "ABCD", "security", "wip")
    assert decisions.main(["build"], root=docs) == 0
    assert "no decisions yet" in (docs / "decisions" / "INDEX.md").read_text()


def test_no_proposed_status_allowed(root):
    place(root, "0004", "architecture", "wip", status="proposed")
    assert decisions.main(["check"], root=root) == 1


# ── relink ──────────────────────────────────────────────────────────────────
def test_relink_cross_directory(built):
    body = (built / "decisions/accepted/security/0003-gamma.md").read_text()
    assert "[`0001`](../architecture/0001-alpha.md)" in body


def test_relink_idempotent(built):
    p = built / "decisions/accepted/security/0003-gamma.md"
    before = p.read_text()
    assert decisions.main(["build", "--relink"], root=built) == 0
    assert p.read_text() == before


def test_move_self_heals(built):
    src = built / "decisions/accepted/architecture/0001-alpha.md"
    src.rename(src.with_name("0001-alpha-renamed.md"))
    assert decisions.main(["check"], root=built) == 1
    assert decisions.main(["build", "--relink"], root=built) == 0
    assert decisions.main(["check"], root=built) == 0
    gamma = (built / "decisions/accepted/security/0003-gamma.md").read_text()
    assert "0001-alpha-renamed.md" in gamma


# ── drafts: UPPERCASE IDs, draft↔draft links ────────────────────────────────
def test_draft_to_draft_link(root):
    place_draft(root, "AAAA", "security", "one")
    place_draft(root, "BBBB", "architecture", "two", body="relates to `AAAA`.")
    assert decisions.main(["build", "--relink"], root=root) == 0
    assert "[`AAAA`](AAAA-one.md)" in (root / "decisions/drafts/BBBB-two.md").read_text()


def test_lowercase_draft_id_rejected(built):
    place_draft(built, "abcd", "security", "lower")
    assert decisions.main(["check"], root=built) == 1


def test_draft_requires_4letter_id(built):
    place_draft(built, "AB", "security", "shorty")
    assert decisions.main(["check"], root=built) == 1


def test_draft_duplicate_id(built):
    place_draft(built, "ABCD", "security", "one")
    place_draft(built, "ABCD", "architecture", "two")
    assert decisions.main(["check"], root=built) == 1


# ── threat-model.md in the link system ──────────────────────────────────────
def test_threat_model_gets_linked(built):
    write_threat_model(built, "Vector X addressed by `0001`.")
    assert decisions.main(["build", "--relink"], root=built) == 0
    link = "[`0001`](decisions/accepted/architecture/0001-alpha.md)"
    assert link in (built / "threat-model.md").read_text()
    assert decisions.main(["check"], root=built) == 0


def test_threat_model_broken_ref_flagged(built):
    write_threat_model(built, "Addressed by `0099`.")
    assert decisions.main(["check"], root=built) == 1


def test_any_doc_is_linked_and_checked(built):
    (built / "roadmap.md").write_text(
        "# Roadmap\n\nMilestone builds on `0001`.\n", encoding="utf-8"
    )
    assert decisions.main(["build", "--relink"], root=built) == 0
    link = "[`0001`](decisions/accepted/architecture/0001-alpha.md)"
    assert link in (built / "roadmap.md").read_text()
    (built / "roadmap.md").write_text("# Roadmap\n\nBuilds on `0099`.\n", encoding="utf-8")
    assert decisions.main(["check"], root=built) == 1


def test_templates_and_index_excluded_from_linkcheck(built):
    (built / "_scratch.md").write_text(
        "# scratch\n\nrefs `0099`.\n", encoding="utf-8"
    )  # _-prefixed
    assert decisions.main(["check"], root=built) == 0  # excluded, so its bad ref is ignored


# ── placement, duplicates, skips ────────────────────────────────────────────
def test_dir_must_match_type(root):
    place(root, "0004", "architecture", "misplaced", subdir="security")
    assert decisions.main(["check"], root=root) == 1


def test_custom_type_is_open(built):
    place_draft(built, "LEGL", "legal", "retention-policy")  # a type outside the usual set
    assert decisions.main(["promote", "LEGL"], root=built) == 0
    # the type's dir is auto-created on promotion
    assert (built / "decisions/accepted/legal/0004-retention-policy.md").exists()
    assert decisions.main(["check"], root=built) == 0


def test_invalid_type_slug_rejected(built):
    place_draft(built, "ABCD", "Security", "bad-slug")  # uppercase -> not a slug
    assert decisions.main(["check"], root=built) == 1


def test_new_type_warns_but_passes(built, capsys):
    place_draft(built, "LEGL", "legal", "thing")  # no decisions/legal/ yet
    assert decisions.main(["check"], root=built) == 0  # non-blocking
    assert "new type" in capsys.readouterr().err  # but warned


def test_archived_status_must_be_retired(root):
    place(root, "0004", "architecture", "notretired", lifecycle="archived", status="accepted")
    assert decisions.main(["check"], root=root) == 1


def test_superseded_in_archived_ok(built):
    place(built, "0004", "architecture", "retired", lifecycle="archived", status="superseded")
    assert decisions.main(["build", "--relink"], root=built) == 0
    assert decisions.main(["check"], root=built) == 0


def test_duplicate_counter(root):
    place(root, "0001", "security", "clash")
    assert decisions.main(["check"], root=root) == 1


def test_gap_in_counters(root):
    place(root, "0005", "architecture", "skipper")
    assert decisions.main(["check"], root=root) == 1


# ── decision → draft breach ─────────────────────────────────────────────────
def test_decision_referencing_draft_is_breach(built):
    place(built, "0004", "architecture", "leaky", body="depends on `WXYZ`.")
    place_draft(built, "WXYZ", "security", "candidate")
    assert decisions.main(["check"], root=built) == 1


def test_decision_relates_to_draft_is_breach(built):
    place(built, "0004", "architecture", "leaky2", relates_to='["WXYZ"]')
    place_draft(built, "WXYZ", "security", "candidate")
    assert decisions.main(["check"], root=built) == 1


def test_decision_linked_draft_ref_is_breach(built):
    # After relink a body ref becomes a markdown LINK; it must STILL be a breach, not only
    # bare inline-code refs (regression guard for the linked-ref blind spot).
    place_draft(built, "WXYZ", "security", "candidate")
    place(built, "0004", "architecture", "leaky3", body="builds on `WXYZ`.")
    assert decisions.main(["build", "--relink"], root=built) == 0  # refresh INDEX + linkify the ref
    body = (built / "decisions/accepted/architecture/0004-leaky3.md").read_text()
    assert "[`WXYZ`](" in body  # ref is now a markdown link
    assert decisions.main(["check"], root=built) == 1  # ...and is still flagged


# ── rename-draft-id ─────────────────────────────────────────────────────────
def test_rename_draft_repoints_refs(built):
    place_draft(built, "ABCD", "security", "target")
    place_draft(
        built, "EFGH", "architecture", "referrer", relates_to='["ABCD"]', body="depends on `ABCD`."
    )
    assert decisions.main(["rename-draft-id", "ABCD", "ZZZZ"], root=built) == 0
    ref = (built / "decisions/drafts/EFGH-referrer.md").read_text()
    assert "ZZZZ" in ref and "ABCD" not in ref
    assert decisions.main(["check"], root=built) == 0


def test_rename_draft_auto_uppercases(built):
    place_draft(built, "ABCD", "security", "thing")
    dest, err = decisions.rename_draft(built, "ABCD", "wxyz")
    assert err is None and dest.name == "WXYZ-thing.md"


def test_rename_draft_rejects_conflict(built):
    place_draft(built, "AAAA", "security", "one")
    place_draft(built, "BBBB", "architecture", "two")
    assert decisions.main(["rename-draft-id", "AAAA", "BBBB"], root=built) == 1


def test_rename_draft_rejects_invalid_id(built):
    place_draft(built, "AAAA", "security", "one")
    dest, err = decisions.rename_draft(built, "AAAA", "AB12")
    assert dest is None and err


# ── promote: single, closure/breach, multi, cycle ───────────────────────────
def test_promote_assigns_next_counter_accepted(built):
    place_draft(built, "QWER", "security", "new-idea")
    assert decisions.main(["promote", "QWER"], root=built) == 0
    dest = built / "decisions/accepted/security/0004-new-idea.md"
    assert dest.exists()
    assert 'id: "0004"' in dest.read_text() and "status: accepted" in dest.read_text()
    assert not (built / "decisions/drafts/QWER-new-idea.md").exists()
    assert decisions.main(["check"], root=built) == 0


def test_promote_rewrites_inbound_refs(built):
    place_draft(built, "ABCD", "security", "target")
    place_draft(
        built, "EFGH", "architecture", "referrer", relates_to='["ABCD"]', body="depends on `ABCD`."
    )
    assert decisions.main(["promote", "ABCD"], root=built) == 0
    ref = (built / "decisions/drafts/EFGH-referrer.md").read_text()
    assert "`0004`" in ref and "ABCD" not in ref
    assert decisions.main(["check"], root=built) == 0


def test_promote_breach_refused_with_closure(built):
    place_draft(built, "ABCD", "security", "needs-dep", body="see `EFGH`.")
    place_draft(built, "EFGH", "architecture", "dep")
    # promoting ABCD alone would leave a decision pointing at draft EFGH -> refused
    dests, err = decisions.promote(built, ["ABCD"])
    assert dests is None and err
    assert "EFGH" in err and "ABCD" in err and "requested" in err
    assert decisions.main(["promote", "ABCD"], root=built) == 1


def test_promote_closed_set_succeeds(built):
    place_draft(built, "ABCD", "security", "a", body="see `EFGH`.")
    place_draft(built, "EFGH", "architecture", "b")
    assert decisions.main(["promote", "ABCD", "EFGH"], root=built) == 0
    assert not list((built / "decisions" / "drafts").glob("[A-Z]*.md"))  # both consumed
    assert decisions.main(["check"], root=built) == 0  # no decision -> draft


def test_promote_cycle_needs_both(built):
    place_draft(built, "ABCD", "security", "a", body="see `EFGH`.")
    place_draft(built, "EFGH", "architecture", "b", body="see `ABCD`.")
    assert decisions.main(["promote", "ABCD"], root=built) == 1  # cycle -> breach
    assert decisions.main(["promote", "ABCD", "EFGH"], root=built) == 0  # together works
    assert decisions.main(["check"], root=built) == 0


def test_promote_assigns_counters_in_argument_order(built):
    # Counters follow the arguments, not their alphabetical order: a co-promoted set often
    # has one record the others build on, and it has to be nameable as the earlier one.
    place_draft(built, "ZZZZ", "security", "foundation", body="named by `AAAA`.")
    place_draft(built, "AAAA", "architecture", "built-on-it", body="builds on `ZZZZ`.")
    assert decisions.main(["promote", "ZZZZ", "AAAA"], root=built) == 0
    assert (built / "decisions/accepted/security/0004-foundation.md").exists()
    assert (built / "decisions/accepted/architecture/0005-built-on-it.md").exists()
    assert decisions.main(["check"], root=built) == 0


def test_promote_reverses_with_the_arguments(built):
    # The same pair the other way round — proof the order is read, not incidental.
    place_draft(built, "ZZZZ", "security", "foundation", body="named by `AAAA`.")
    place_draft(built, "AAAA", "architecture", "built-on-it", body="builds on `ZZZZ`.")
    assert decisions.main(["promote", "AAAA", "ZZZZ"], root=built) == 0
    assert (built / "decisions/accepted/architecture/0004-built-on-it.md").exists()
    assert (built / "decisions/accepted/security/0005-foundation.md").exists()


def test_blocking_message_suggests_a_command_that_keeps_the_requested_order(built):
    # The refusal prints a command to run. It must be a valid promotion AND must leave the
    # requested draft with the first counter — the caller's order survives the round-trip.
    place_draft(built, "ZZZZ", "security", "foundation", body="see `AAAA`.")
    place_draft(built, "AAAA", "architecture", "dep")
    dests, err = decisions.promote(built, ["ZZZZ"])
    assert dests is None and "promote ZZZZ AAAA" in err
    argv = err.split("Run:\n  ")[1].splitlines()[0].split()[2:]  # drop `python scripts/…`
    assert decisions.main(argv, root=built) == 0
    assert (built / "decisions/accepted/security/0004-foundation.md").exists()
    assert (built / "decisions/accepted/architecture/0005-dep.md").exists()
    assert decisions.main(["check"], root=built) == 0


def test_promote_comma_separated(built):
    place_draft(built, "ABCD", "security", "a", body="see `EFGH`.")
    place_draft(built, "EFGH", "architecture", "b")
    assert decisions.main(["promote", "ABCD,EFGH"], root=built) == 0
    assert decisions.main(["check"], root=built) == 0


def test_promote_disambiguates(built):
    place_draft(built, "QWER", "architecture", "alpha-cand")
    place_draft(built, "QWES", "security", "beta-cand")
    dests, err = decisions.promote(built, ["qwe"], input_fn=lambda _: "1")
    assert err is None and dests[0].name == "0004-alpha-cand.md"


def test_promote_no_match(built):
    assert decisions.main(["promote", "ZZZZ"], root=built) == 1


# ── promote: the heading carries the new ID ─────────────────────────────────
def test_promote_numbers_the_h1(built):
    place_draft(built, "QWER", "security", "new-idea")
    assert decisions.main(["promote", "QWER"], root=built) == 0
    body = (built / "decisions/accepted/security/0004-new-idea.md").read_text()
    assert "# 0004 — new-idea" in body and "# QWER" not in body


def test_promote_numbers_a_backticked_h1(built):
    p = place_draft(built, "QWER", "security", "new-idea")
    p.write_text(p.read_text().replace("# QWER — ", "# `QWER` — "))
    assert decisions.main(["promote", "QWER"], root=built) == 0
    dest = built / "decisions/accepted/security/0004-new-idea.md"
    assert "# 0004 — new-idea" in dest.read_text()


def test_heading_renders_an_em_dash_title_as_a_colon():
    # 0033's front-matter title carries its own em-dash; the H1 holds exactly one.
    assert decisions.heading_for("0033", "Egress proxy — the outbound chokepoint") == (
        "# 0033 — Egress proxy: the outbound chokepoint"
    )


def test_promote_inserts_a_missing_h1_from_the_title(built, capsys):
    p = place_draft(built, "QWER", "security", "new-idea")
    p.write_text(p.read_text().replace("# QWER — new-idea\n\n", ""))
    assert decisions.main(["promote", "QWER"], root=built) == 0
    body = (built / "decisions/accepted/security/0004-new-idea.md").read_text()
    assert body.split("---\n", 2)[2].lstrip().startswith("# 0004 — new-idea")
    assert "inserted the H1" in capsys.readouterr().err  # ...and says so


def test_promote_flags_an_h1_that_does_not_lead_with_the_id(built, capsys):
    p = place_draft(built, "QWER", "security", "new-idea")
    p.write_text(p.read_text().replace("# QWER — new-idea", "# Something else entirely"))
    assert decisions.main(["promote", "QWER"], root=built) == 0
    body = (built / "decisions/accepted/security/0004-new-idea.md").read_text()
    assert "# 0004 — Something else entirely" in body
    assert "check it" in capsys.readouterr().err


def test_heading_ignores_a_hash_inside_a_fence():
    text = "---\nid: ABCD\n---\n\n```py\n# ABCD is a comment\n```\n\n# ABCD — real\n"
    out, note = decisions.retitle_heading(text, "ABCD", "0004")
    assert "# ABCD is a comment" in out and "# 0004 — real" in out and note is None


def test_rename_draft_carries_the_h1(built):
    place_draft(built, "ABCD", "security", "thing")
    assert decisions.main(["rename-draft-id", "ABCD", "ZZZZ"], root=built) == 0
    assert "# ZZZZ — thing" in (built / "decisions/drafts/ZZZZ-thing.md").read_text()


# ── promote: relative links follow the move ─────────────────────────────────
def with_links(root):
    """A repo whose docs carry the hand-authored path classes a promotion invalidates."""
    (root / "glossary.md").write_text("# Glossary\n\n## sandbox\n\nbody\n", encoding="utf-8")
    (root / "deploy.md").write_text("# Deploy\n\nbody\n", encoding="utf-8")
    (root / "research").mkdir(parents=True, exist_ok=True)
    (root / "research" / "memo.md").write_text("# Memo\n\nbody\n", encoding="utf-8")
    (root.parent / "scripts").mkdir(parents=True, exist_ok=True)
    (root.parent / "scripts" / "spike.py").write_text("x = 1\n", encoding="utf-8")


def test_promote_repaths_every_relative_link_class(built):
    with_links(built)
    place_draft(
        built,
        "QWER",
        "security",
        "new-idea",
        body=(
            "A [sandbox](../../glossary.md#sandbox), the [memo](../../research/memo.md),\n"
            "[deploy](../../deploy.md), and [`../../../scripts/spike.py`]"
            "(../../../scripts/spike.py).\n\n## Heading\n\nAn [anchor](#heading) and "
            "an [away](https://example.com/x) link.\n"
        ),
    )
    assert decisions.main(["promote", "QWER"], root=built) == 0  # 1 if a link stayed broken
    body = (built / "decisions/accepted/security/0004-new-idea.md").read_text()
    assert "(../../../glossary.md#sandbox)" in body  # accepted/<type>/ sits a level deeper
    assert "(../../../research/memo.md)" in body
    assert "(../../../deploy.md)" in body
    # a link labelled with its own path moves label and target together
    assert "[`../../../../scripts/spike.py`](../../../../scripts/spike.py)" in body
    assert "(#heading)" in body and "(https://example.com/x)" in body  # neither is ours to move
    assert decisions.main(["check"], root=built) == 0


def test_promote_exits_nonzero_when_a_link_stays_broken(built, capsys):
    place_draft(built, "QWER", "security", "new-idea", body="a [gone](../../nowhere.md) link.")
    assert decisions.main(["promote", "QWER"], root=built) == 1  # promoted, but says so
    assert "broken link" in capsys.readouterr().err
    assert (built / "decisions/accepted/security/0004-new-idea.md").exists()


def test_promote_repoints_a_spelled_out_path(built):
    place_draft(built, "QWER", "security", "new-idea")
    (built / "research").mkdir(parents=True, exist_ok=True)
    (built / "research" / "memo.md").write_text(
        "# Memo\n\nFeeds the draft (`docs/decisions/drafts/QWER-new-idea.md`).\n", encoding="utf-8"
    )
    assert decisions.main(["promote", "QWER"], root=built) == 0
    memo = (built / "research" / "memo.md").read_text()
    assert "`docs/decisions/accepted/security/0004-new-idea.md`" in memo


# ── promote: the mnemonic stops reading anywhere ────────────────────────────
def test_promote_converts_bare_prose_mnemonics(built):
    place_draft(built, "QWER", "security", "door", body="QWER fixes the door; see `QWER`.")
    place_draft(built, "EFGH", "architecture", "referrer", body="Behind QWER's door.")
    assert decisions.main(["promote", "QWER"], root=built) == 0
    record = (built / "decisions/accepted/security/0004-door.md").read_text()
    assert record.count("QWER") == 0 and "0004 fixes the door" in record  # self-refs too
    assert "Behind 0004's door." in (built / "decisions/drafts/EFGH-referrer.md").read_text()


def test_promote_converts_the_mnemonic_in_front_matter_prose(built):
    place_draft(built, "QWER", "security", "door")
    p = place_draft(built, "EFGH", "architecture", "referrer")
    p.write_text(
        p.read_text().replace("type:", 'summary: "Behind QWER\'s door"\ntype:', 1),
        encoding="utf-8",
    )
    assert decisions.main(["promote", "QWER"], root=built) == 0
    assert 'summary: "Behind 0004\'s door"' in p.read_text()


def test_prose_sweep_spares_code_and_link_targets(built):
    # The hazard that made this manual: a mnemonic also reads as a plausible identifier.
    place_draft(built, "QWER", "security", "door")
    place_draft(
        built,
        "EFGH",
        "architecture",
        "referrer",
        body=(
            '```py\nQWER = "qwer"  # an enum member, not the record\n```\n\n'
            "Inline `QWER_TOKEN` and the [memo](../../research/notes-QWER.md).\n"
        ),
    )
    (built / "research").mkdir(parents=True, exist_ok=True)
    (built / "research" / "notes-QWER.md").write_text("# Notes\n\nbody\n", encoding="utf-8")
    assert decisions.main(["promote", "QWER"], root=built) == 0
    ref = (built / "decisions/drafts/EFGH-referrer.md").read_text()
    assert 'QWER = "qwer"' in ref  # a fenced identifier keeps its name
    assert "`QWER_TOKEN`" in ref  # ...and so does a longer identifier
    assert "(../../research/notes-QWER.md)" in ref  # a path is a path


def test_residual_mnemonics_reports_code_but_never_edits_it(built, capsys):
    src = built.parent / "src"
    src.mkdir(parents=True, exist_ok=True)
    (src / "constants.py").write_text('QWER = "qwer"\n', encoding="utf-8")
    place_draft(built, "QWER", "security", "door")
    assert decisions.main(["promote", "QWER"], root=built) == 0
    assert (src / "constants.py").read_text() == 'QWER = "qwer"\n'  # untouched
    err = capsys.readouterr().err
    assert "src/constants.py:1" in err and "leave any identifier named QWER alone" in err


# ── promote: front matter round-trips clean ─────────────────────────────────
def test_blank_ref_fields_keep_no_trailing_space(built):
    p = built / "decisions/accepted/architecture/0001-alpha.md"
    p.write_text(p.read_text().replace("supersedes: null", "supersedes:"))
    place_draft(built, "QWER", "security", "new-idea")
    assert decisions.main(["promote", "QWER"], root=built) == 0
    # the pre-commit `trailing-whitespace` hook would strip these straight back out
    assert "supersedes:\n" in p.read_text() and "supersedes: \n" not in p.read_text()
    assert not [ln for ln in p.read_text().splitlines() if ln != ln.rstrip()]


# ── deref / blocking / replace ──────────────────────────────────────────────
def test_promote_deref_inverts_frontmatter_edge(built):
    place_draft(built, "AAAA", "architecture", "alpha", relates_to='["BBBB"]')
    place_draft(built, "BBBB", "security", "beta")
    dests, err = decisions.promote(built, ["AAAA"])  # front-matter-only ref
    assert dests is None and "--deref" in err
    assert decisions.main(["promote", "--deref", "AAAA"], root=built) == 0
    assert (built / "decisions/accepted/architecture/0004-alpha.md").exists()
    assert '"0004"' in (built / "decisions/drafts/BBBB-beta.md").read_text()  # link moved onto BBBB
    assert decisions.main(["check"], root=built) == 0


def test_promote_deref_inverts_superseded_by_edge(built):
    # superseded_by is a scalar edge: inverting it must set BBBB's *single* `supersedes`
    # counter, not coerce it into a list (which would crash check on the unhashable value).
    place_draft(built, "AAAA", "architecture", "alpha", superseded_by='"BBBB"')
    place_draft(built, "BBBB", "security", "beta")
    dests, err = decisions.promote(built, ["AAAA"])  # front-matter-only ref
    assert dests is None and "--deref" in err
    assert decisions.main(["promote", "--deref", "AAAA"], root=built) == 0
    assert (built / "decisions/accepted/architecture/0004-alpha.md").exists()
    bbbb = decisions.parse_front_matter((built / "decisions/drafts/BBBB-beta.md").read_text())
    assert bbbb["supersedes"] == "0004"  # scalar counter, not a list
    assert decisions.main(["check"], root=built) == 0


def test_prose_ref_blocks_and_beats_deref(built):
    place_draft(built, "AAAA", "architecture", "alpha", relates_to='["BBBB"]', body="see `BBBB`.")
    place_draft(built, "BBBB", "security", "beta")
    dests, err = decisions.promote(built, ["AAAA"])
    assert dests is None and "blocked" in err and "--deref" not in err  # blocking wins


def test_deref_rejected_when_blocking(built):
    place_draft(built, "AAAA", "architecture", "alpha", body="see `BBBB`.")
    place_draft(built, "BBBB", "security", "beta")
    assert decisions.main(["promote", "--deref", "AAAA"], root=built) == 1


def test_relinked_body_ref_still_blocks_deref(built):
    # `build --relink` turns every bare body ref into a markdown link. A blocking check
    # that reads only the bare form goes blind after the first build, and --deref then
    # promotes into a breach `check` catches afterwards. It must refuse up front.
    place_draft(built, "AAAA", "architecture", "alpha", relates_to='["BBBB"]', body="see `BBBB`.")
    place_draft(built, "BBBB", "security", "beta")
    assert decisions.main(["build", "--relink"], root=built) == 0
    assert "[`BBBB`](" in (built / "decisions/drafts/AAAA-alpha.md").read_text()  # now a link
    dests, err = decisions.promote(built, ["AAAA"])
    assert dests is None and "blocked" in err  # not "dereferenceable"
    assert decisions.main(["promote", "--deref", "AAAA"], root=built) == 1
    assert (built / "decisions/drafts/AAAA-alpha.md").exists()  # nothing moved


def test_supersedes_decision_needs_replace_then_archives(built):
    place_draft(built, "CCCC", "architecture", "newer", supersedes='"0001"')
    assert decisions.main(["promote", "CCCC"], root=built) == 1  # needs --allow-replace
    assert decisions.main(["promote", "CCCC", "--allow-replace"], root=built) == 0
    archived = built / "decisions/archived/0001-alpha.md"
    assert archived.exists() and "superseded" in archived.read_text()
    assert decisions.main(["check"], root=built) == 0


# ── check semantics & CLI ───────────────────────────────────────────────────
def test_check_clean(built):
    assert decisions.main(["check"], root=built) == 0


def test_check_read_only(built):
    p = built / "decisions/accepted/security/0003-gamma.md"
    before = (p.read_text(), (built / "decisions" / "INDEX.md").read_text())
    assert decisions.main(["check"], root=built) == 0
    assert (p.read_text(), (built / "decisions" / "INDEX.md").read_text()) == before


def test_check_detects_stale_index(built):
    p = built / "decisions/accepted/architecture/0001-alpha.md"
    p.write_text(p.read_text().replace("one-line summary", "changed"))
    assert decisions.main(["check"], root=built) == 1


def test_bare_relink_folds_into_build(root):
    assert decisions.main(["--relink"], root=root) == 0
    assert "[`0001`]" in (root / "decisions/accepted/security/0003-gamma.md").read_text()


def test_unknown_subcommand_exits_2(root):
    with pytest.raises(SystemExit) as e:
        decisions.main(["bogus"], root=root)
    assert e.value.code == 2


def test_relink_not_valid_on_check(root):
    with pytest.raises(SystemExit) as e:
        decisions.main(["check", "--relink"], root=root)
    assert e.value.code == 2


def test_promote_requires_query(root):
    with pytest.raises(SystemExit) as e:
        decisions.main(["promote"], root=root)
    assert e.value.code == 2


def test_rename_requires_two_args(root):
    with pytest.raises(SystemExit) as e:
        decisions.main(["rename-draft-id", "ABCD"], root=root)
    assert e.value.code == 2


def test_install_scaffolds_fresh_repo(tmp_path):
    decisions.install(tmp_path)  # repo root = tmp_path (no upward search)
    docs = tmp_path / "docs"
    assert (tmp_path / "scripts" / "decisions.py").is_symlink()
    for p in (
        "decisions/accepted/.gitkeep",
        "decisions/archived/.gitkeep",
        "decisions/README.md",
        "decisions/AGENTS.md",
        "decisions/_template.md",
        "decisions/drafts/_template.md",
        "decisions/INDEX.md",
    ):
        assert (docs / p).exists(), p
    assert decisions.main(["check"], root=docs) == 0  # scaffolded repo is valid immediately

    # gitignores the machine-specific symlink (creating .gitignore in an empty repo)
    assert "scripts/decisions.py" in (tmp_path / ".gitignore").read_text().splitlines()

    # wires root entry points (absent in a fresh repo) with placeholders linking the scaffold
    readme, agents = (tmp_path / "README.md").read_text(), (tmp_path / "AGENTS.md").read_text()
    assert "docs/decisions/README.md" in readme and "docs/decisions/INDEX.md" in readme
    assert "docs/decisions/AGENTS.md" in agents

    decisions.install(tmp_path)  # idempotent re-run doesn't raise


def test_install_preserves_existing_entry_points(tmp_path):
    (tmp_path / "README.md").write_text("# Existing\n")
    (tmp_path / "AGENTS.md").write_text("# Existing agents\n")
    (tmp_path / ".gitignore").write_text("node_modules/\n")
    decisions.install(tmp_path)
    assert (tmp_path / "README.md").read_text() == "# Existing\n"  # never overwritten
    assert (tmp_path / "AGENTS.md").read_text() == "# Existing agents\n"
    gi = (tmp_path / ".gitignore").read_text().splitlines()
    assert "node_modules/" in gi and "scripts/decisions.py" in gi  # appended, not clobbered
    decisions.install(tmp_path)  # idempotent: a second run adds no duplicate ignore line
    assert (tmp_path / ".gitignore").read_text().count("scripts/decisions.py") == 1


# ── link check: code spans and anchors ──────────────────────────────────────
def test_heading_anchors_github_slugs():
    text = (
        "# Appendix — Harnesses evaluated (research notes, non-binding)\n\n"
        '## "dreaming"\n\n## Risks & open questions\n\n## dup\n\n## dup\n\n'
        "```\n## not a heading\n```\n"
    )
    assert decisions.heading_anchors(text) == {
        "appendix--harnesses-evaluated-research-notes-non-binding",
        "dreaming",
        "risks--open-questions",
        "dup",
        "dup-1",
    }


def test_link_inside_code_span_is_not_checked(built):
    p = built / "decisions/accepted/architecture/0001-alpha.md"
    p.write_text(p.read_text() + "\nUse the form `[term](../../glossary.md#term)` when linking.\n")
    assert decisions.main(["check"], root=built) == 0


def test_link_inside_fenced_block_is_not_checked(built):
    p = built / "decisions/accepted/architecture/0001-alpha.md"
    p.write_text(p.read_text() + "\n```md\n[term](../../nowhere.md#x)\n```\n")
    assert decisions.main(["check"], root=built) == 0


def test_broken_cross_file_anchor_is_flagged(built, capsys):
    (built / "glossary.md").write_text("# Glossary\n\n## sandbox\n\nbody\n")
    p = built / "decisions/accepted/architecture/0001-alpha.md"
    body = p.read_text()
    p.write_text(body + "\nsee [sandbox](../../../glossary.md#sandbox).\n")
    assert decisions.main(["check"], root=built) == 0
    p.write_text(body + "\nsee [sandbox](../../../glossary.md#sandbxo).\n")
    assert decisions.main(["check"], root=built) == 1
    assert "broken anchor" in capsys.readouterr().err


def test_intra_doc_anchor_is_validated(built, capsys):
    p = built / "decisions/accepted/architecture/0001-alpha.md"
    body = p.read_text() + "\n## Context\n\nsee [Context](#context).\n"
    p.write_text(body)
    assert decisions.main(["check"], root=built) == 0
    p.write_text(body.replace("(#context)", "(#contxt)"))
    assert decisions.main(["check"], root=built) == 1
    assert "broken anchor" in capsys.readouterr().err


# ── front matter: strict-YAML hazards ───────────────────────────────────────
def test_unquoted_colon_in_summary_fails_check(root, capsys):
    place(root, "0004", "product", "delta", summary="Two modes: channel and principal")
    assert decisions.main(["check"], root=root) == 1
    assert "unquoted ':'" in capsys.readouterr().err


def test_quoted_colon_in_summary_passes_check(root):
    place(root, "0004", "product", "delta", summary='"Two modes: channel and principal"')
    assert decisions.main(["build", "--relink"], root=root) == 0
    assert decisions.main(["check"], root=root) == 0


def test_block_scalar_colon_passes_check(root):
    place(root, "0004", "product", "delta", summary=">-\n  Two modes: channel and principal")
    assert decisions.main(["build", "--relink"], root=root) == 0
    assert decisions.main(["check"], root=root) == 0


def test_unbalanced_quote_fails_check(root, capsys):
    place(root, "0004", "product", "delta", summary='"half open')
    assert decisions.main(["check"], root=root) == 1
    assert "unbalanced quote" in capsys.readouterr().err


# ── upstream collisions ─────────────────────────────────────────────────────
# Every check above reads one tree, so a duplicate ID can only fail once both copies
# are in it — after a rebase, by which point the record is written and cross-referenced.
# These cover the same question asked one tree earlier, against origin/main. It warns
# and never gates; see `warn_upstream_collisions`.
def branch_off(root, publish_upstream):
    """origin/main holds 0001..0003 and the draft CONF, all under their own names."""
    place_draft(root, "CONF", "architecture", "confidence")
    assert decisions.main(["build", "--relink"], root=root) == 0
    publish_upstream(root.parent)
    return root


def check(root, capsys):
    capsys.readouterr()
    return decisions.main(["check"], root=root), capsys.readouterr()


def test_a_counter_taken_upstream_by_another_file_warns(root, capsys, publish_upstream):
    branch_off(root, publish_upstream)
    was = root / "decisions" / "accepted" / "architecture" / "0002-beta.md"
    was.rename(was.with_name("0002-something-else.md"))
    decisions.main(["build", "--relink"], root=root)
    _, out = check(root, capsys)
    assert (
        "WARN decisions: 0002 is taken on origin/main by 0002-beta.md, and here by "
        "0002-something-else.md — renumber to 0004 before the trees meet" in out.err
    )


def test_a_draft_id_taken_upstream_by_another_file_warns(root, capsys, publish_upstream):
    branch_off(root, publish_upstream)
    was = root / "decisions" / "drafts" / "CONF-confidence.md"
    was.rename(was.with_name("CONF-a-different-idea.md"))
    decisions.main(["build", "--relink"], root=root)
    _, out = check(root, capsys)
    assert (
        "WARN drafts: CONF is taken on origin/main by CONF-confidence.md, and here by "
        "CONF-a-different-idea.md — re-mint it before the trees meet" in out.err
    )


def test_the_same_id_in_the_same_file_is_not_a_collision(root, capsys, publish_upstream):
    """That is the record, edited — the case every branch is in."""
    branch_off(root, publish_upstream)
    code, out = check(root, capsys)
    assert code == 0 and "WARN" not in out.err


def test_archiving_a_record_keeps_its_filename_and_stays_silent(root, capsys, publish_upstream):
    """accepted/<type>/ -> archived/ moves a record without renaming it."""
    branch_off(root, publish_upstream)
    was = root / "decisions" / "accepted" / "architecture" / "0002-beta.md"
    place(root, "0002", "architecture", "beta", lifecycle="archived", status="superseded")
    was.unlink()
    decisions.main(["build", "--relink"], root=root)
    _, out = check(root, capsys)
    assert "WARN decisions" not in out.err


def test_an_id_free_upstream_is_silent(root, capsys, publish_upstream):
    branch_off(root, publish_upstream)
    place(root, "0004", "architecture", "delta")
    place_draft(root, "TIER", "architecture", "tiering")
    decisions.main(["build", "--relink"], root=root)
    code, out = check(root, capsys)
    assert code == 0 and "WARN" not in out.err


def test_a_missing_origin_main_skips_silently(root, capsys, publish_upstream):
    """A fresh clone, an offline machine, a CI checkout that fetched only the branch."""
    branch_off(root, publish_upstream)
    subprocess.run(
        ["git", "-C", str(root.parent), "update-ref", "-d", "refs/remotes/origin/main"], check=True
    )
    was = root / "decisions" / "accepted" / "architecture" / "0002-beta.md"
    was.rename(was.with_name("0002-something-else.md"))
    decisions.main(["build", "--relink"], root=root)
    code, out = check(root, capsys)
    assert code == 0 and out.err == ""


def test_a_tree_outside_git_skips_silently(built, capsys, tmp_path):
    assert not (tmp_path / ".git").exists()
    code, out = check(built, capsys)
    assert code == 0 and out.err == ""


def test_the_warning_does_not_change_the_exit_code(root, capsys, publish_upstream):
    """Warning and errors are independent: neither creates nor masks the other."""
    branch_off(root, publish_upstream)
    was = root / "decisions" / "accepted" / "architecture" / "0002-beta.md"
    was.rename(was.with_name("0002-something-else.md"))  # 0003 cites 0002: links go stale
    code, out = check(root, capsys)
    assert code == 1
    assert "WARN decisions: 0002 is taken on origin/main by 0002-beta.md" in out.err
    assert "broken link" in out.err or "stale" in out.err


# ── minting against origin/main ─────────────────────────────────────────────
# `check` only warns about a counter taken upstream, because origin/main moves under a
# branch. Minting is the other side of that: it is a write, and by the time anything
# reads the number the record has been renamed, its H1 rewritten and every inbound link
# repathed — so promote asks the ref rather than reporting on it afterwards.
def behind_main(root, publish_upstream, *, last="0004"):
    """A branch that forked before `last` landed: origin/main holds it, this tree does not."""
    held = [f"{n:04d}" for n in range(4, int(last) + 1)]
    for counter in held:
        place(root, counter, "architecture", f"held-{counter}")
    assert decisions.main(["build", "--relink"], root=root) == 0
    publish_upstream(root.parent)
    for counter in held:
        (root / "decisions" / "accepted" / "architecture" / f"{counter}-held-{counter}.md").unlink()
    assert decisions.main(["build", "--relink"], root=root) == 0
    return root


def test_promote_mints_past_a_counter_origin_main_holds(root, publish_upstream):
    behind_main(root, publish_upstream)
    place_draft(root, "QWER", "security", "new-idea")
    assert decisions.main(["promote", "QWER"], root=root) == 0
    assert (root / "decisions/accepted/security/0005-new-idea.md").exists()
    assert not (root / "decisions/accepted/security/0004-new-idea.md").exists()


def test_promote_says_which_counters_upstream_holds(root, capsys, publish_upstream):
    behind_main(root, publish_upstream)
    place_draft(root, "QWER", "security", "new-idea")
    decisions.main(["promote", "QWER"], root=root)
    assert (
        "origin/main holds 0004, so this starts at 0005. Rebase to close the sequence."
        in capsys.readouterr().err
    )


def test_the_note_names_a_range_when_upstream_is_further_ahead(root, capsys, publish_upstream):
    behind_main(root, publish_upstream, last="0006")
    place_draft(root, "QWER", "security", "new-idea")
    decisions.main(["promote", "QWER"], root=root)
    assert "origin/main holds 0004..0006, so this starts at 0007" in capsys.readouterr().err


def test_co_promoted_drafts_all_start_past_upstream(root, publish_upstream):
    behind_main(root, publish_upstream)
    place_draft(root, "QWER", "security", "first")
    place_draft(root, "ZXCV", "security", "second")
    assert decisions.main(["promote", "QWER", "ZXCV"], root=root) == 0
    assert (root / "decisions/accepted/security/0005-first.md").exists()
    assert (root / "decisions/accepted/security/0006-second.md").exists()


def test_the_counter_stepped_over_is_not_reported_as_a_gap(root, capsys, publish_upstream):
    """The record exists — it is just not on this branch yet, and the rebase closes it."""
    behind_main(root, publish_upstream)
    place_draft(root, "QWER", "security", "new-idea")
    assert decisions.main(["promote", "QWER"], root=root) == 0
    code, out = check(root, capsys)
    assert code == 0
    assert "gap in counters" not in out.err


def test_a_counter_neither_tree_has_is_still_a_gap(root, publish_upstream):
    branch_off(root, publish_upstream)
    place(root, "0005", "architecture", "skipper")  # 0004 is in neither tree
    decisions.main(["build", "--relink"], root=root)
    assert decisions.main(["check"], root=root) == 1


def test_without_the_ref_promote_mints_the_local_next(built, capsys):
    """A fresh clone or an offline machine mints exactly as it did before any of this."""
    place_draft(built, "QWER", "security", "new-idea")
    assert decisions.main(["promote", "QWER"], root=built) == 0
    assert (built / "decisions/accepted/security/0004-new-idea.md").exists()
    assert "origin/main holds" not in capsys.readouterr().err


def test_no_note_when_origin_main_is_not_ahead(root, capsys, publish_upstream):
    branch_off(root, publish_upstream)
    place_draft(root, "QWER", "security", "new-idea")
    assert decisions.main(["promote", "QWER"], root=root) == 0
    assert (root / "decisions/accepted/security/0004-new-idea.md").exists()
    assert "origin/main holds" not in capsys.readouterr().err
