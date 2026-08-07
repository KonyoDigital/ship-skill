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
    # ⚠ WHITESPACE-NORMALISED COPY, for any check on a phrase longer than a word.
    # This file is hard-wrapped at ~88 columns, so a phrase can be split by a newline
    # and `"a b c" in md` fails on text that is present and correct. That has now cost
    # three false failures in one session — "PASSED, CEILING or STALLED", "SOLO or
    # MULTI (Step 4b)", and "not independently verified". A gate that fails correct
    # work is worse than no gate: it teaches you to ignore it.
    # Strip markdown continuation markers BEFORE flattening: a phrase wrapped inside a
    # blockquote keeps its "> " at the line break, so a plain whitespace join yields
    # "It was > already like that" and the check fails on text that is present. Fourth
    # variant of this same class in one session — the fix is normalising the markup,
    # not rewording the file to suit the checker.
    flat = " ".join(re.sub(r"^\s*>\s?", "", md, flags=re.M).split())
    # lowercased too: a sentence-initial capital is not a rule change, and three checks
    # failed a compression that kept every rule because of exactly that.
    low = flat.lower()
    seal_all = (md[md.index("## Step 6"):md.index("## Step 7")]
                if "## Step 6" in md and "## Step 7" in md else "")

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
    want("cannot be narrowed" in flat and "surprised the verdict was SHIP" in flat,
         "the scope-boundary rule ships — Rule 0 forbids SHIP-with-caveats while the "
         "seal requires 'what was NOT checked', and without a pinned scope those "
         "contradict; without the no-narrowing clause 'out of scope' launders a known "
         "defect into a SHIP")
    want("low-stakes change" in flat and "Small is not the same as cheap to get wrong" in flat,
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
    want("also a suspect, not only the instrument" in flat and "count the artifacts" in flat,
         "tests are treated as a SUSPECT artifact, not only the instrument of proof — "
         "the live trial's difficulty was two tests asserting the bug as correct, where "
         "a green suite is evidence pointing the wrong way")
    want("if anything" in md,
         "the embarrassment lens asks what, IF ANYTHING — without it the lens obliges "
         "an objection into existence, contradicting the rule four lines below it "
         "forbidding a manufactured problem")
    want("If you cannot ask" in flat and "narrower" in flat,
         "Step 1 has a no-channel fallback — a subagent or scheduled run cannot ask, "
         "and a question answered by assumption looks identical to one never asked")
    want("is the problem in the work, or in the proof" in flat,
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
    want("do not invent one" in md,
         "the ceiling comes from the PERSON, not from thin air — a made-up 'three "
         "passes' cuts off a run that needed four as confidently as it bounds one that "
         "needed none (loop-library, alirezarezvani/claude-skills, MIT)")
    want("manufacture a loop" in md,
         "it refuses to LOOP at all when no new feedback can change the next action — "
         "iterating without new information produces the same answer at rising cost and "
         "looks like diligence")
    want("tune against the check" in flat and "not independently verified" in flat,
         "tuning against the check that judges you is named — the check then measures "
         "how hard you tuned, and it is invisible from inside because everything is green")
    want("burndown chart with extra steps" in low and "retract" in low,
         "a sealed verdict is RETRACTABLE — a system that can only promote is a "
         "burndown chart with extra steps, and a one-way SHIP means 'nobody has "
         "objected yet' rather than 'this was proven' (Granite0x's test: can your "
         "system take done back?)")
    want("persuasion, not enforcement" in low,
         "the skill states its own boundary up front — it cannot stop anyone claiming "
         "a check passed without running it, and a green report is a CLAIM not a proof")
    want("Stop` hook" in md or "Stop hook" in flat,
         "…and it points at a real gate outside the model for when being wrong is "
         "expensive, rather than implying the text is enforcement")
    want("MULTI indicated; unavailable" in flat,
         "the ladder has a row for MULTI being RIGHT and unreachable — a subagent "
         "cannot spawn subagents, and quietly declaring SOLO hides the difference "
         "between choosing it and having nothing else available")
    want("refutes this" in flat and "Unsupported is an absence" in flat,
         "unsupported (DRAFT) is split from refuted (BLOCKED) — they arrive in the same "
         "sentence, and treating a refuted claim as merely unsupported ships a wrong "
         "statement with a caveat instead of fixing it")
    want("It was already like that" in flat,
         "…and the verdict does not depend on who caused the defect — an inherited one "
         "is judged on the artifact's state at the seal")
    want("EVERY granularity" in flat and "sentence, clause" in flat,
         "no-drive-by applies below the file — the real failure is dropping a clause "
         "inside a sentence you had cause to touch")
    # rindex, not index: the pins repeat this rule ABOVE Step 3 on purpose, so the
    # first occurrence is the pin. What must hold is that it ALSO appears in Step 3.
    want("read what a source says about itself" in low
         and low.rindex("read what a source says about itself") > low.index("## step 3"),
         "a source's own prose counts, AND it sits inside Step 3 — two independent trial "
         "agents credited it with the hardest catch and both said it was buried in a "
         "subsection about test suites, where nobody doing document work would look")
    want((HERE / "GATE_RULES.md").is_file(),
         "the carved gate rules ship — four scars landed in one territory and moved out "
         "of scattered comments into their own file, which is the graduation this skill "
         "prescribes, applied to itself")
    want("UNFIXABLE" in seal_all,
         "the SEAL can report all FOUR stop reasons — a fourth reason the seal cannot "
         "express is a rule that silently never fires")
    want("DEFECT" in flat and "wider blast radius" in flat,
         "sweep vs no-drive-by is resolved by DEFECT CLASS — same defect everywhere is "
         "finishing the ask, a different defect noticed on the way is a drive-by")
    want("four labelled blocks" in flat,
         "the four lenses require four labelled blocks — merged into one paragraph, "
         "'I considered all four' is unfalsifiable and is what a run produces when it "
         "did not do them separately")
    want("Nothing \"loads itself.\"" in md,
         "the scar mechanism does not claim to load itself — it is Step 0 discipline, "
         "and claiming more would be the unearned promise this skill exists to catch")
    # ⚠ THE SWEEP CHECK. The ceiling rule was changed in ONE place and left in three
    # others, so CEILING was still defined as "hit the limit" — unfireable when nobody
    # set a limit, quietly turning a four-way stop into a three-way. That is this
    # skill's own "kill the stale claim" failing on its own text, and no single-phrase
    # check would have caught it: the new text was present and correct.
    want("the ceiling you set" not in flat and "set a new ceiling" not in flat,
         "the ceiling edit is SWEPT — no surviving text tells the reader to invent or "
         "re-grant a limit the person never gave")
    want("nothing to report" in flat,
         "the four-lens output shape and 'say nothing if nothing' compose explicitly — a "
         "block reading 'nothing to report' satisfies both, and without saying so they "
         "read as opposites")
    want("## The pins" in md and low.index("## the pins") < low.index("## rule 0"),
         "the PINS open the file — five trials reported uniform emphasis ('two dozen "
         "warning markers; when everything is flagged, nothing is') and named the same "
         "handful of rules as load-bearing. They now sit first, with the rest as reasoning")
    want("does these names exist" in low or "do these names exist" in low,
         "the Syntax check knows a parse is not a load — agent-army passed every gate "
         "for five commits and died at 'process is not defined' before spawning an agent")
    want("whether the correction" in low and "survives without it" in low,
         "the clause-level rule distinguishes a COMPELLED deletion from a tidy one — "
         "'feels tidy' fails when the correction cannot be expressed with the clause "
         "still there, which is structurally forced rather than optional")
    want("permission bounds the sweep" in low,
         "permission bounds the sweep, not just scope — the same defect in six sibling "
         "files is a reason to REPORT five, never a licence to edit them")
    want("do not invent it" in low and "looks checked" in low,
         "when a fix needs data you do not have, the EDIT decision is covered and not "
         "only the verdict: leave the wrong claim and flag it, because a substituted "
         "plausible number is a new error that looks checked")

    # ⚠ STRUCTURAL: three garbled passages shipped from splices in one round, and two
    # independent readers hit all of them live. Markdown that does not close is not a
    # style issue here — one of them detached the DRAFT/BLOCKED table from the paragraph
    # that explains it, which both agents called the sharpest thing in the file.
    # ⚠ COUNT PER PARAGRAPH, NOT PER LINE. Bold legitimately wraps across lines in a
    # hard-wrapped file — a per-line count flags 40 correct paragraphs. The property is
    # that each blank-line-separated block opens and closes its own markers; that is
    # what catches a splice leaving a stray closer, which is the defect that shipped.
    _bad = [b.split("\n")[0][:44] for b in re.split(r"\n\s*\n", md)
            if b.count("**") % 2 and not b.lstrip().startswith("```")]
    want(not _bad,
         f"every paragraph opens and closes its own bold markers ({_bad[:3] or 'none'}) "
         f"— three garbled passages shipped from splices in one round and two independent "
         f"readers hit all three; one detached the DRAFT/BLOCKED table from the paragraph "
         f"explaining it, which both called the sharpest thing in the file")

    want("Ratifying your founding rules" in scars and "must not write these for you" in scars,
         "SCARS.md carries the ratification conversation — the candidates are shapes and "
         "the loop cannot compound until a real user replaces them, so the file has to "
         "say HOW, and has to forbid Claude inventing the answers")
    # ⚠ STRUCTURAL: a paragraph pasted BETWEEN table rows splits one table into two and
    # orphans every row after it from its header. It happened in Rule 0 — the section that
    # decides every verdict — and no wording check can see it, because both the table and
    # the paragraph are individually correct.
    _split = [b.split(chr(10))[0][:44] for b in re.split(r"\n\s*\n", md)
              if b.lstrip().startswith("|") and re.search(r"^\|.*\n(?!\||\s*$)", b, re.M)]
    want(not _split,
         f"no table has prose spliced between its rows ({_split[:2] or 'none'}) — that "
         f"orphans every row below from its header, and it happened in the verdict table")
    want("belong to a different tool" not in flat,
         "the stale note claiming tiny/lean/max 'control nothing here' is gone — a Meter "
         "routing section eleven lines below explains how to route them, and two passages "
         "giving opposite answers about the same three words is the stale-claim class")
    # ⚠ THE PUBLIC PACKAGE MUST SHIP ZERO REAL SCARS. One leaked — a real failure from
    # the author's own trading-console work, published in a stranger's clean start, while
    # the file three lines above still said "none yet". A scar file that contradicts
    # itself is bad; one that ships someone else's real failures is worse.
    _real = [b for b in re.findall(r"^WHAT BROKE.*$", scars, re.M)
             if "the summary quoted a figure that was not in the source" not in b]
    want(not _real,
         f"the public package ships NO real scars ({[b[:44] for b in _real] or 'none'}) — "
         f"only the labelled EXAMPLE. The first user's scar must be their own, and the "
         f"file says 'none yet', which has to be true")
    want("The ordinary happy path is SHIP" in flat,
         "the happy path is stated — errors found, all fixed, fixes proven, boundary "
         "stated is SHIP. Without it the file specifies every route INTO DRAFT and "
         "BLOCKED and almost none into the verdict most runs should reach")
    want("also a false report" in flat and "never to feel safer" in flat,
         "the DRAFT bias is named — the file warns at length against a wrong SHIP and "
         "the asymmetry is itself a thumb on the scale; a defensive DRAFT on clean work "
         "is also a false report")
    want('"A question I now always ask" is a real guard' in flat,
         "GUARD's usable escape hatch is FIRST, not third in a parenthetical — an agent "
         "auditing someone else's repo cannot add a test to it, and editing this skill "
         "to install a guard is itself a drive-by, so it is often the only option")
    want("+ EXCEPTION" in md and md.count("+ EXCEPTION") >= 4,
         f"the repetition convention ships and is USED ({md.count('+ EXCEPTION')} "
         f"passages) — the file had no way to signal 'this repeats and adds an exception' "
         f"versus 'this is emphasis', and two readers skimmed exactly those paragraphs")
    want("never that it was saved" in md,
         "the seal says scar durability is UNVERIFIED and never claims it was saved — "
         "reading a file back proves the write, never that the workspace survives")

    # STRUCTURAL, so it catches the CLASS. A sentence promising N things followed by a
    # different number of things is a defect no wording check finds: "the last two make
    # it a defence" sat above THREE bullets, a compression casualty that read as correct
    # to two reviewers.
    _w = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}

    # ⚠ SAME CLASS, DIFFERENT SHAPE. "exactly three reasons" sat above a FOUR-row
    # table the moment UNFIXABLE HERE was added — a promise-vs-count mismatch that no
    # wording check finds, exactly like "the last two" over three bullets. Counting
    # table rows as well as bullets is what makes this catch the class rather than the
    # one instance that happened to be noticed.
    for _m in re.finditer(r"exactly (two|three|four|five|six) reasons", md):
        _seg = md[_m.end():_m.end() + 1600]
        _rows = len(re.findall(r"^\| \*\*[A-Z]", _seg, re.M))
        if _rows and _rows != _w[_m.group(1)]:
            _bad_rows = True
            want(False, f"'exactly {_m.group(1)} reasons' is followed by {_rows} table "
                        f"rows — a promise that does not match its own count")
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
    want("STALLED" in flat and "Silence is not evidence" in flat,
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
        ("the ceiling goes back to an invented number",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("do not invent one", "pick three")}),
        ("the overfitting rule is dropped",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("tune against the check", "x")}),
        ("a verdict count stops matching its table",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("exactly four reasons", "exactly three reasons")}),
        ("retraction is dropped — the system can only promote",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("burndown chart with extra steps", "x")}),
        ("the persuasion-not-enforcement boundary is hidden",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("Persuasion, not enforcement", "x").replace("persuasion, not enforcement", "x")}),
        ("the unavailable-MULTI row is dropped",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("MULTI indicated; unavailable", "x")}),
        ("refuted collapses back into unsupported",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("Unsupported is an absence", "x")}),
        ("no-drive-by stops applying below the file",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("EVERY granularity", "files")}),
        # mutate the LOCATION too: the finding was that this rule was filed in the
        # wrong section, so moving it back out must turn the gate red.
        ("source prose stops counting as source",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("Read what a source says about itself", "x")}),
        ("the pins are demoted below Rule 0",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("## The pins", "## Appendix")}),
        ("a splice leaves an unbalanced bold marker",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("**Compelled**", "**Compelled", 1)}),
        ("permission stops bounding the sweep",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("permission bounds the sweep", "x")}),
        ("the ratification conversation is dropped",
         lambda f: {**f, "ship-skill/SCARS.md":
                    f["ship-skill/SCARS.md"].decode().replace("Ratifying your founding rules", "x").encode()}),
        ("prose is spliced back into the verdict table",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace(
             "| A **required** in-scope check you could not run |",
             "**Some prose.**\n\n| A **required** in-scope check you could not run |", 1)}),
        ("a real scar leaks into the public package",
         lambda f: {**f, "ship-skill/SCARS.md":
                    (f["ship-skill/SCARS.md"].decode() +
                     "\nWHAT BROKE   a real failure from somebody else's work\n").encode()}),
        ("the happy path is dropped",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("The ordinary happy path is SHIP", "x")}),
        ("the DRAFT bias goes unnamed again",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("also a false report", "x")}),
        ("the exception convention is unused",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("+ EXCEPTION", "")}),
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
