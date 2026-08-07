#!/usr/bin/env python3
"""Verify ship-skill.zip is a package Claude Desktop will actually accept.

Run before publishing: `python3 verify_package.py`

⚠ WHY THIS EXISTS AS A SCRIPT AND NOT A CHECKLIST. Every failure it checks for is
SILENT at authoring time — the zip builds fine, the markdown renders fine, and the
package is rejected (or worse, accepted and subtly broken) only at upload:

  · files loose in the zip root, or an extra wrapping folder -> rejected
  · a description over 1024 chars                            -> rejected
  · SKILL.md referencing SCARS.md while the zip omits it     -> accepted, and the
    skill then tells its user to read a file that is not there

`--self-test` proves each check can FAIL. A gate nobody has seen go red is not
known to be measuring anything.
"""
from __future__ import annotations
import io, re, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMIT = 1024


def check(zf: zipfile.ZipFile) -> list[str]:
    fails, names = [], zf.namelist()
    md = zf.read("ship-skill/SKILL.md").decode()

    def want(cond, label):
        print(("  ok   · " if cond else "  FAIL · ") + label)
        if not cond:
            fails.append(label)

    roots = sorted({n.split("/")[0] for n in names})
    want(roots == ["ship-skill"],
         f"one root folder {roots} — loose files and double wrappers are the two "
         f"shapes Desktop rejects")
    want("ship-skill/SCARS.md" in names,
         "SCARS.md ships inside the package — the skill reads it before Step 1, so "
         "shipping the reference without the file is the 'guard names a missing "
         "file' bug this workflow exists to prevent")

    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    want(bool(m), "frontmatter delimiters parse")
    fm = m.group(1) if m else ""
    nm = re.search(r"^name:\s*(.+)$", fm, re.M)
    ds = re.search(r"^description:\s*(.+)$", fm, re.M)
    want(bool(nm and ds), "frontmatter carries name and description")
    want(bool(nm) and re.fullmatch(r"[a-z0-9-]{1,64}", nm.group(1).strip()),
         f"name {nm.group(1).strip() if nm else None!r} is lowercase-hyphen, <=64 chars")
    d = ds.group(1).strip() if ds else ""
    want(len(d) <= LIMIT,
         f"description is {len(d)} chars (limit {LIMIT}) — over-long is rejected at "
         f"upload, never truncated")

    scars = zf.read("ship-skill/SCARS.md").decode() if \
        "ship-skill/SCARS.md" in names else ""
    want("grok" not in md.lower() and "grok" not in scars.lower(),
         "zero mentions of any second vendor — this build stands alone on Claude")
    want("Step 4b" in md and "MULTI" in md, "the SOLO/MULTI section is present")
    want("Step 7" in md and "SCARS" in md, "the scar / skill-carving step is present")

    # The two new steps are worthless if the seal does not demand them.
    if "## Step 6" in md and "## Step 7" in md:
        seal = md[md.index("## Step 6"):md.index("## Step 7")]
        want("SOLO or MULTI" in seal,
             "the SEAL requires naming the mode — describing modes elsewhere does "
             "not make anyone state which one they ran")
        want("scar" in seal.lower(),
             "the SEAL requires answering whether a scar was produced — without "
             "this the learning loop is skipped silently and forever")
        want("EVIDENCE" in seal,
             "the SEAL requires the scar's EVIDENCE line — a scar without it is a "
             "superstition, and superstitions accumulate into a workflow that "
             "refuses things for reasons that were never true")
        # ⚠ CHECK THE PROPERTY, NOT THE PHRASING. This first read
        # `"PASSED, CEILING or STALLED" in seal` and failed a rewrite that said
        # `PASSED / CEILING / STALLED` — same requirement, different punctuation.
        # A gate matching prose measures the author's wording, not the rule, and
        # blocks correct work while a genuine removal using the blessed phrase
        # would sail through.
        want(all(w in seal for w in ("PASSED", "CEILING", "STALLED")),
             "the SEAL names all three stop reasons in some phrasing — 'didn't "
             "work' collapses CEILING (keep going) and STALLED (change approach), "
             "which call for opposite responses")
    want("FOUNDING RULES" in scars and "LEARNED" in scars,
         "SCARS.md ships the founding/learned split — a rule from one bad "
         "afternoon must never sit at the same authority as a rule chosen while "
         "thinking clearly, and nothing learned may overwrite a founding rule")
    want("SCARS.prev.md" in md or "SCARS.prev.md" in scars,
         "…and the undo step ships: without a previous copy a WRONG scar is "
         "permanent, which is a strange property for a file whose whole job is "
         "recording that we got something wrong")
    want("cannot be narrowed" in md and "surprised the verdict was SHIP" in md,
         "the scope-boundary rule ships — Rule 0 forbids SHIP-with-caveats while the "
         "seal requires 'what was NOT checked', and without a pinned scope those "
         "contradict; without the no-narrowing clause 'out of scope' launders a known "
         "defect into a SHIP")
    want("low-stakes change" in md and "Small is not the same as cheap to get wrong" in md,
         "Step 1's short path requires small AND low-stakes — a one-line production "
         "config change is small and expensive, and an earlier compression dropped the "
         "stakes half, licensing one round on exactly that")
    # ⚠ IGNORE QUOTED OCCURRENCES. A sentence explaining why a phrasing is wrong
    # contains that phrasing, so a naive `not in md` fails the fix that removed it —
    # the same shape as grepping for a bug and matching the comment describing it.
    # Only an UNQUOTED occurrence is the instruction actually saying it.
    _unquoted = re.sub(r'"[^"]*"', '""', md)
    want("waiting on RATIFICATION" in md and "waiting to be filled in" not in _unquoted,
         "CANDIDATES is described as awaiting RATIFICATION, not as awaiting being "
         "written — the drafts are already there, and 'waiting to be filled in' names "
         "the wrong gap and invites Claude to fill it, which is exactly what must not "
         "happen to a rule that will carry the user's authority")
    want("LOWEST-NUMBERED rung" in md and "highest rung available" not in md,
         "the ladder says LOWEST-NUMBERED, matching its own numbering (1 strongest, "
         "4 none) — 'highest rung available' read literally selects rung 4, which is "
         "no review at all")
    want("A **required** in-scope check you could not run" in md,
         "an unrunnable REQUIRED in-scope check is DRAFT — otherwise the "
         "could-not-verify row contradicts 'missing evidence is not a pass' and lets a "
         "check become optional by being unrunnable")
    want("free to **name** and never free to **act on**" in md,
         "widening scope is free to NAME, not to ACT on — otherwise it licenses exactly "
         "the changes-nobody-asked-for that Step 2 forbids")
    want("also a suspect, not only the instrument" in md and "count the artifacts" in md,
         "tests are treated as a SUSPECT artifact, not only the instrument of proof — "
         "the live trial's difficulty was two tests asserting the bug as correct, where "
         "a green suite is evidence pointing the wrong way")
    want("if anything" in md,
         "the embarrassment lens asks what, IF ANYTHING — without it the lens obliges "
         "an objection into existence, contradicting the rule four lines below it "
         "forbidding a manufactured problem")
    want("If you cannot ask" in md and "narrower" in md,
         "Step 1 has a no-channel fallback — a subagent or scheduled run cannot ask, "
         "and a question answered by assumption looks identical to one never asked")
    want("is the problem in the work, or in the proof" in md,
         "DRAFT vs BLOCKED is PINNED — work wrong is BLOCKED, proof short is DRAFT, "
         "both is BLOCKED; two careful readers reached different words from identical "
         "facts without it")
    want("UNFIXABLE HERE" in md,
         "there is a verdict for 'checked thoroughly, found defects I cannot fix' — "
         "the other three assume a check you can RETRY, and looping on an unfixable "
         "defect just produces the same answer more expensively")
    want("At most ONE scar per run" in md and "no scar" in md,
         "scar triage ships — one careful pass over a 25-line document produced THREE "
         "scars with genuine evidence, which is how the file becomes the unread thing "
         "it warns about")
    want("Once it has entries" in scars,
         "SCARS.md carries the SAME hedge as SKILL.md — 'the only file written by "
         "experience' was fixed in one place and left unhedged in the other")
    want("never that it was saved" in md,
         "the seal says scar durability is UNVERIFIED and never claims it was saved — "
         "reading a file back proves the write, never that the workspace survives")

    # STRUCTURAL, so it catches the CLASS. A sentence promising N things followed by a
    # different number of things is a defect no wording check finds: "the last two make
    # it a defence" sat above THREE bullets, a compression casualty that read as correct
    # to two reviewers.
    _w = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    _bad = []
    for _m in re.finditer(r"[Tt]he last (two|three|four|five|six)[^.\n]*:", md):
        _after = md[_m.end():_m.end() + 2000]
        _stop = re.search(r"\n\n(?!- )", _after)
        _n = len(re.findall(r"^- \*\*", _after[:_stop.start() if _stop else 2000], re.M))
        if _n and _n != _w[_m.group(1)]:
            _bad.append((_m.group(0)[:44], _w[_m.group(1)], _n))
    want(not _bad,
         f"every 'the last N...:' promise is followed by exactly N bullets "
         f"(mismatched: {_bad or 'none'})")
    want("STALLED" in md and "Silence is not evidence" in md,
         "the stopping rule ships, including the silent-check trap — a check that "
         "prints nothing on failure looks identical whether you are converging or "
         "stuck, so a stall cannot be read off it")
    return fails


def _zip(files: dict) -> zipfile.ZipFile:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for k, v in files.items():
            z.writestr(k, v)
    return zipfile.ZipFile(b)


def self_test() -> int:
    good = zipfile.ZipFile(HERE / "ship-skill.zip")
    files = {n: good.read(n) for n in good.namelist() if not n.endswith("/")}
    md = files["ship-skill/SKILL.md"].decode()
    bad = 0
    for label, mutate in [
        ("description over the limit",
         lambda f: {**f, "ship-skill/SKILL.md": re.sub(
             r"^description:.*$", "description: " + "x" * 1100, md, flags=re.M)}),
        ("SCARS.md missing from the zip",
         lambda f: {k: v for k, v in f.items() if "SCARS" not in k}),
        ("a second vendor named in the skill",
         lambda f: {**f, "ship-skill/SKILL.md": md + "\nAsk Grok to review.\n"}),
        ("files loose in the zip root",
         lambda f: {k.split("/")[-1]: v for k, v in f.items()}),
        # ⚠ MUTATE THE PROPERTY, NOT A PHRASE. This first replaced the literal
        # "SOLO or MULTI (Step 4b)"; a later rewrite said "SOLO or MULTI,
        # truthfully" and the mutation became a NO-OP, so the gate stayed green
        # and --self-test correctly reported it was measuring nothing. A red
        # proof that cannot fail is worth less than no red proof, because it
        # certifies the check.
        ("the seal no longer demands the mode",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("SOLO", "x").replace("MULTI", "y")}),
        ("the seal no longer demands the stop reason",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("STALLED", "x").replace("CEILING", "y")}),
        ("the silent-check trap dropped from the stopping rule",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("Silence is not evidence", "x")}),
        ("CANDIDATES goes back to awaiting being written",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("waiting on RATIFICATION", "waiting to be filled in")
                      .replace('is "waiting to be filled in" describes', "is fine and describes")}),
        ("the ladder goes back to 'highest rung'",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("LOWEST-NUMBERED rung", "highest rung available")}),
        ("a required unrunnable check stops being DRAFT",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("A **required** in-scope check you could not run", "x")}),
        ("tests stop being treated as a suspect",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("also a suspect, not only the instrument", "x")}),
        ("the no-channel fallback is dropped",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("If you cannot ask", "x")}),
        ("DRAFT vs BLOCKED goes unpinned again",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("is the problem in the work, or in the proof", "x")}),
        ("the unfixable verdict disappears",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("UNFIXABLE HERE", "x")}),
        ("scar triage is removed",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("At most ONE scar per run", "x")}),
        ("the scope rule loses its no-narrowing clause",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("cannot be narrowed", "may be adjusted")}),
        ("Step 1's short path drops the stakes half again",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("low-stakes change", "change")}),
        ("a count promise stops matching its bullets",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("The last three are what make it a defence",
                               "The last two are what make it a defence")}),
        ("SCARS.md loses the founding/learned split",
         lambda f: {**f, "ship-skill/SCARS.md":
                    f["ship-skill/SCARS.md"].decode().replace("FOUNDING RULES", "Rules").encode()}),
        ("the seal stops demanding scar evidence",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("including its EVIDENCE line", "")}),
    ]:
        print(f"\n  RED PROOF — {label}")
        try:
            fails = check(_zip(mutate(files)))
        except Exception as e:            # a missing member is also a failure
            fails = [f"raised {type(e).__name__}"]
            print(f"  FAIL · raised {type(e).__name__}")
        if not fails:
            print(f"  ✗✗ THE GATE STAYED GREEN on {label!r} — it is not measuring this")
            bad += 1
    return bad


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        n = self_test()
        print()
        print("EVERY CHECK PROVEN RED." if not n
              else f"{n} CHECK(S) COULD NOT BE MADE TO FAIL — they measure nothing")
        raise SystemExit(1 if n else 0)
    print("ship-skill.zip")
    f = check(zipfile.ZipFile(HERE / "ship-skill.zip"))
    print()
    print("PACKAGE OK" if not f else f"{len(f)} FAILURE(S)")
    raise SystemExit(1 if f else 0)
