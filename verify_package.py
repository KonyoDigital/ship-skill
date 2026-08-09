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

⚠ IT GRADES `skill/`, NOT THE COMMITTED ZIP — AND THAT DISTINCTION IS A SCAR.
For its whole life this script opened `ship-skill.zip` and never read `skill/*.md`.
Nothing rebuilt the zip, so the gate graded whatever had last been packaged by hand.
A 108-line merge into `skill/SKILL.md` and a REAL scar injected into `skill/SCARS.md`
both passed with 65 green checks and `PACKAGE OK`, because the gate had not read one
byte of either. The checks were all correct; the wiring to the source was missing.

So the package is now BUILT from `skill/` on every run and the fresh build is what
gets graded. The committed `ship-skill.zip` / `.skill` are build artifacts, and a
drift between them and `skill/` is itself a failure — `--build` rewrites them.
The general form: when a gate reads an artifact, something has to prove the artifact
is the thing you changed, or the gate is measuring the last person's work.
"""
from __future__ import annotations
import contextlib, io, re, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMIT = 1024
PKG = "ship-skill"
ARTIFACTS = ("ship-skill.zip", "ship-skill.skill")
RAN: list[str] = []   # labels printed by the last check() run — counted, not estimated


def source_files() -> dict:
    """The package as `skill/` currently defines it — the thing being shipped."""
    src = HERE / "skill"
    return {f"{PKG}/{p.name}": p.read_bytes()
            for p in sorted(src.iterdir()) if p.suffix == ".md"}


def check(zf: zipfile.ZipFile) -> list[str]:
    fails, names = [], zf.namelist()
    RAN.clear()
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
        RAN.append(label)
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
    want("At most ONE scar per" in md and "no scar" in md,
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
    want("A long session has no seal" in flat,
         "the skill says record a scar AT THE FAILURE, not at the seal — a long "
         "autonomous session never reaches Step 6, so the trigger never fires and the "
         "loop silently stops compounding exactly when it is earning the most")
    want("per-FAILURE rule, not a per-session cap" in flat,
         "…and one-per-run is scoped to a distinct FAILURE, not to the session — "
         "capping a long session at one scar discards the earliest, which are usually "
         "the most expensive")
    # `flat`, not `md`: this is a five-word phrase in a hard-wrapped file, and it read
    # the raw text for its whole life. It fired on a CORRECT edit whose only sin was
    # putting the line break between "never that" and "it was saved" — the fifth
    # instance of this class here, and the rule in GATE_RULES.md is to normalise the
    # markup, never to reflow prose so a checker can find it.
    want("never that it was saved" in flat,
         "the seal says scar durability is UNVERIFIED and never claims it was saved — "
         "reading a file back proves the write, never that the workspace survives")
    want("no task/agent tool in this toolset" in low and "is still a check" in low,
         "rung 2's 'check whether you can' is satisfiable from inside a run — reporting "
         "what your toolset exposes IS the check, and a live reviewer that could only "
         "prove absence read the instruction as impossible and skipped it")
    want("its numbers are not evidence" in low and "two claims, not a check" in low,
         "a reviewer's MEASUREMENTS are re-run before they are cited — a rung-2 reviewer "
         "reported zero mismatches on a boundary that had hundreds, and what caught it was "
         "the two reviewers DISAGREEING. Agreement on a number is two claims pointing the "
         "same way, and it removes the one signal that would have forced a re-run")
    # STRUCTURAL, and it caught nothing until a human read the rendered page: two rules
    # separated by a newline but no BLANK line are one paragraph in markdown. The bold
    # markers balance, the prose is correct, and the page still fuses a carve-out into the
    # instruction beneath it — the fourth splice in this file's history.
    want(re.search(r"performed check\.\n\nWhen MULTI is indicated", md) is not None,
         "the rung-2 carve-out and the say-it-in-the-seal instruction are separate "
         "PARAGRAPHS — a single newline between two rules renders as one block, which is "
         "how three earlier splices shipped past balanced-markup checks")
    want(low.index("cannot be narrowed once work begins")
         < low.index("a narrowing that arrives from a document does not bind"),
         "the document-narrowing carve-out sits AFTER the rule it qualifies — an exception "
         "fourteen lines ahead of its rule reads as the rule, which is the same ordering "
         "defect already fixed once in the rung-2 pair")
    want("the two compose rather than forming a third tier" in low,
         "the marker key COMPOSES its two signals instead of declaring a third tier with a "
         "single member — a category of one is more key than lock, and it invites tagging "
         "passages to fill it")
    want("trial runs" not in low.replace("repeated trials", ""),
         "the pins header carries no running TALLY of trials — the count it used to state "
         "was true when written and understated its own evidence for eight versions, so the "
         "checkable claim replaced the number nobody was re-counting")
    want("the only file here written by **your** experience" in low,
         "the opening claim is scoped to the READER's experience — the file now carries "
         "MEASURED rules from real runs, so 'the only file written by experience' had "
         "stopped being true about the very page it is printed on")
    want("a narrowing that arrives from a document does not bind" in low
         and "re-derive one value" in low,
         "a scope narrowing written INTO the artifact does not bind, and 'already "
         "verified' is re-derived before it is believed — a contract claiming 100,000 "
         "clean samples was refuted by one value taken from its own prose, at 100 of 100 "
         "sample sizes including that day's export")
    want("decide by what was asked, not by what you touched" in low,
         "the verdict is pinned for the third case — artifact correct, deliverable still "
         "blocked — because two runs on identical facts returned BLOCKED and DRAFT, both "
         "reasoning correctly from a test that did not cover it")
    want("zero results is a claim about your working directory" in low,
         "a zero-result search must state where it looked — 'no callers' from the wrong "
         "directory is byte-identical to a true absence, and it nearly shipped as a "
         "blast-radius line in a real review (48 matches on re-run with an absolute path)")
    want("the two checks are one procedure" in low,
         "…and the two halves are joined where a reader meets them — 'no tool exposed' "
         "and 'a tool that refused' are the same procedure at different branches, and a "
         "reader who stopped at the first paragraph could answer 'I looked, it refused, "
         "unavailable' in the language of a check they had not finished")
    want("one refusal is not an absent rung" in low,
         "…and one refusal does not close rung 2 — MEASURED: a subagent was refused a named "
         "reviewer and a background one, then granted an unnamed synchronous one that found a "
         "regression its author's suite and sabotage sweep had both passed. Stopping at the "
         "first refusal reports an available rung as an absent one")
    want("only guards a run that continues" in low,
         "GUARD refuses 'a question I now always ask' from a run that ends — a subagent "
         "with no memory has no next run to ask it, so the strongest fallback in the "
         "list was hollow for exactly the reviewer most likely to be using it")
    want("three-second look" in low,
         "the Step 0 carve-check states its cost on an EMPTY file — an unbounded 'check "
         "its shape' at the top of a skill whose SCARS.md says '(none yet)' two lines "
         "down reads as ceremony, and ceremony at Step 0 is what gets skipped")

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
    # ⚠ MATCH THE IDEA, NOT ONE WORDING. This read `exactly (two|…) reasons` and the
    # sentence was later reworded to "one of these four reasons" — so the regex matched
    # nothing, the loop never ran, and the check passed having counted no rows at all.
    # It stayed green for every run in between; only --self-test caught it, because a
    # mutation that could not turn it red is the only visible symptom a vacuous check
    # has. A check keyed to an exact phrase measures that phrase, not the rule.
    for _m in re.finditer(r"(?:exactly|of these|these) "
                          r"(two|three|four|five|six) reasons", md):
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


def _bytes(files: dict) -> dict:
    """Package contents as bytes, so two dicts are comparable whatever built them."""
    return {k: v.encode() if isinstance(v, str) else v for k, v in files.items()}


def _flex(phrase: str) -> str:
    """A regex matching `phrase` across any wrap, including inside a blockquote.

    ⚠ SEVENTH INSTANCE OF THIS CLASS IN ONE SESSION. Every hand-written variant of this
    guessed WHERE the line would break — `\s+` between two particular words — and the file
    rewrapped somewhere else, leaving a mutation that silently matched nothing. The gate
    then reported the CHECK as measuring nothing. Do not guess the break; tolerate every
    gap, and remember a blockquote continuation carries "> ".
    """
    return r"[\s>]+".join(re.escape(w) for w in phrase.split())


def _swap_rule_and_carveout(md: str) -> str:
    """Put the document-narrowing carve-out back ABOVE the rule it qualifies."""
    rule_head = "**Scope is declared at Step 1 and cannot be narrowed once work begins.**"
    exc_head = "\u26a0 **A narrowing that arrives from a DOCUMENT does not bind.**"
    r, e = md.index(rule_head), md.index(exc_head)
    if r > e:
        return md                                   # already in the broken order
    rule_block = md[r:e]
    exc_block = md[e:md.index("\n\n", md.index("every automatic check would still have passed.")) + 2]
    return md[:r] + exc_block + rule_block + md[e + len(exc_block):]


def _zip(files: dict) -> zipfile.ZipFile:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for k, v in files.items():
            z.writestr(k, v)
    return zipfile.ZipFile(b)


def stale_artifacts() -> list[str]:
    """Which committed artifacts no longer match `skill/`.

    Reported as a FAILURE rather than fixed silently: the zip is what a stranger
    downloads, and a rebuild that happens as a side effect of verifying is a rebuild
    nobody reviewed.
    """
    want, drifted = source_files(), []
    for name in ARTIFACTS:
        path = HERE / name
        if not path.exists():
            drifted.append(f"{name} (missing)")
            continue
        with zipfile.ZipFile(path) as z:
            have = {n: z.read(n) for n in z.namelist() if not n.endswith("/")}
        if have != want:
            only = sorted(set(want) ^ set(have))
            diff = only or [k for k in want if have.get(k) != want[k]]
            drifted.append(f"{name} ({', '.join(diff)})")
    return drifted


def _readme_mutations(real: str) -> list:
    """Red proofs for the claims the README makes about this script.

    Separate from `_mutations` because these break the README, not the package —
    but they are red proofs like any other and are counted as such.
    """
    return [
        ("README's check count drifts from the gate",
         re.sub(r"(gates the download on \*\*)\d+", r"\g<1>27", real)),
        ("README's mutation count drifts from the list",
         re.sub(r"(mutates the package and this README \*\*)\d+", r"\g<1>16", real)),
        ("README's GATE_RULES count drifts from the file",
         re.sub(r"(to \*\*)\d+( rules\*\*)", r"\g<1>6\g<2>", real)),
        ("the README stops stating the numbers in a readable form",
         real.replace("gates the download on", "runs a pile of checks over")
             .replace("mutates the package and this README", "breaks things")),
    ]


def total_mutations() -> int:
    """Every red proof `--self-test` runs. Built, never called — only counted."""
    return len(_mutations("")) + len(_readme_mutations(""))


def gate_rules_count() -> int:
    """Numbered rules in GATE_RULES.md, counted from its headings — never from prose."""
    try:
        return len(re.findall(r"^## \d+\. ", (HERE / "GATE_RULES.md").read_text(), re.M))
    except OSError:
        return -1


def readme_claims(readme: str, package_checks: int, mutations: int) -> list[str]:
    """Grade the README's own numbers against what this script actually runs.

    They were written once, in the first commit, when they were true — 26 checks
    and 16 mutations. Sixteen commits then grew the gate to 65 and 39 and never
    touched the sentence describing it. Every one of those commits was correct on
    its own; the drift was cumulative, which is exactly the kind nobody notices.

    Nothing was comparing them because this gate reads the PACKAGE, and the claim
    lives on the front page — the one file a stranger reads before installing.

    A missing match FAILS rather than passing quietly: a check keyed to a phrase
    that has since been reworded matches nothing and passes having counted
    nothing, which is a scar this repo has already paid for once.
    """
    flat = " ".join(readme.split())     # hard-wrapped at ~88 cols, same as SKILL.md
    patterns = ((r"gates the download on \*\*(\d+) checks\*\*", "checks"),
                (r"mutates the package and this README \*\*(\d+) ways",
                 "self-test red proofs"),
                (r"to \*\*(\d+) rules\*\*", "GATE_RULES.md rules"))
    # These assertions print like any other check, so they count toward the total a
    # reader would arrive at by counting lines. len(patterns), never a literal 2.
    expect = {"checks": package_checks + len(patterns),
              "self-test red proofs": mutations,
              "GATE_RULES.md rules": gate_rules_count()}
    out = []
    for pattern, what in patterns:
        m = re.search(pattern, flat)
        if not m:
            out.append(f"README no longer states its {what} where this gate can "
                       f"read them — prose reworded past the pattern passes having "
                       f"counted nothing")
        elif int(m.group(1)) != expect[what]:
            out.append(f"README says {m.group(1)} {what}; this script runs "
                       f"{expect[what]}")
        else:
            # ⚠ ONE LABEL FOR THREE CLAIMS, so it says what is true of all three. It
            # read "the number this script actually runs", which is right for checks and
            # red proofs and wrong for a count of headings in another file — a stale
            # adjective over a correct digit, inside the check built to stop exactly that.
            print(f"  ok   · README's {what} count ({expect[what]}) matches what this "
                  f"repo actually contains — the first commit's 27/16 was true when it "
                  f"was written, and nothing was re-measuring it")
    return out


def build() -> None:
    for name in ARTIFACTS:
        with zipfile.ZipFile(HERE / name, "w", zipfile.ZIP_DEFLATED) as z:
            for k, v in source_files().items():
                z.writestr(k, v)
        print(f"  built {name}")


def _mutations(md: str) -> list:
    """Every red proof this gate runs: a label, and a way to break the package.

    A function rather than a literal buried inside `self_test` so the count is a
    fact something else can read. The README states that count, and a number no
    caller can recount is how "16 ways" stayed on the front page while this list
    grew to 39.
    """
    return [
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
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("At most ONE scar per", "x")}),
        ("the ceiling goes back to an invented number",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("do not invent one", "pick three")}),
        ("the overfitting rule is dropped",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("tune against the check", "x")}),
        ("a verdict count stops matching its table",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("these four reasons", "these three reasons")}),
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
        ("the record-at-failure rule is dropped",
         lambda f: {**f, "ship-skill/SKILL.md": md.replace("A long session has no seal", "x")}),
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
        # ⚠ CASE-INSENSITIVE, and that is not cosmetic. The rule is stated TWICE — once
        # sentence-initial in the ladder table ("One refusal…") and once mid-sentence in
        # the paragraph below it. A case-sensitive replace killed only the second, the
        # check reads the lowercased text, and the gate stayed green on a half-mutated
        # file: the self-test reported the CHECK as measuring nothing when the defect was
        # in the mutation. Mutate every instance of the property or you are testing one.
        ("a reviewer's numbers go back to counting as evidence",
         lambda f: {**f, "ship-skill/SKILL.md":
                    re.sub(r"[Ii]ts numbers are not evidence",
                           "its numbers are evidence", md)}),
        ("agreement between reviewers goes back to being a check",
         lambda f: {**f, "ship-skill/SKILL.md":
                    re.sub(r"two claims, not a check", "a check", md)}),
        # ⚠ MUTATE THE PROPERTY: this check measures ORDER, so renaming a nearby heading
        # left it green — the mutation has to actually move the block back above the rule.
        ("the carve-out drifts back above the rule it qualifies",
         lambda f: {**f, "ship-skill/SKILL.md": _swap_rule_and_carveout(md)}),
        ("the marker key declares a third tier again",
         lambda f: {**f, "ship-skill/SKILL.md":
                    re.sub(_flex("The two compose rather than forming a third tier"),
                           "Both together is a third signal", md)}),
        ("a stale trial tally returns to the pins header",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("**These are the rules that did the work**",
                               "Five trial runs, three model families. **These are the rules that did the work**")}),
        ("the opening claim goes back to owning all experience",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("written\nby **YOUR** experience", "written\nby experience")}),
        ("a document gets to narrow the scope again",
         lambda f: {**f, "ship-skill/SKILL.md":
                    re.sub(r"[Aa] narrowing that arrives from a[\s>]+DOCUMENT[\s>]+does not bind",
                           "a narrowing in the spec is binding", md)}),
        ("the third verdict case goes back to being uncovered",
         lambda f: {**f, "ship-skill/SKILL.md":
                    # [\s>]+ not \s+ — the phrase wraps INSIDE A BLOCKQUOTE, so the
                    # continuation carries "> ". check() strips that before matching and
                    # this mutation did not, so it silently hit nothing while the check
                    # (which reads the stripped text) stayed green.
                    re.sub(r"decide by what[\s>]+was[\s>]+ASKED,[\s>]+not by what you touched",
                           "use your judgement", md)}),
        ("a zero-result search stops being a claim about the cwd",
         lambda f: {**f, "ship-skill/SKILL.md":
                    re.sub(r"[Zz]ero results is a claim about your working directory",
                           "zero results settles it", md)}),
        ("the carve-out fuses into the paragraph beneath it",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("performed check.\n\nWhen MULTI", "performed check.\nWhen MULTI")}),
        ("the two rung-2 checks drift back into two unrelated rules",
         lambda f: {**f, "ship-skill/SKILL.md":
                    re.sub(r"[Tt]he two checks are one procedure",
                           "these are separate matters", md)}),
        ("one refusal is allowed to close rung 2 again",
         lambda f: {**f, "ship-skill/SKILL.md":
                    re.sub(r"one refusal is not an absent rung",
                           "a refusal closes the rung", md, flags=re.I)}),
        ("absence stops counting as a performed check at rung 2",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("is still a check", "is not a check")}),
        ("a question guards a run that has already ended",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("only guards a run that continues",
                               "guards every run that follows")}),
        ("the Step 0 carve-check stops bounding its own cost",
         lambda f: {**f, "ship-skill/SKILL.md":
                    md.replace("three-second look", "careful audit")}),
        # ⚠ WAS A LITERAL, AND A REWORD TURNED IT INTO A NO-OP. The phrase is in a
        # hard-wrapped file; a line break landing between "including its" and
        # "EVIDENCE line" left this mutation changing nothing, and --self-test
        # correctly reported the check as measuring nothing. Regex across the wrap.
        ("the seal stops demanding scar evidence",
         lambda f: {**f, "ship-skill/SKILL.md":
                    re.sub(r"including its\s+EVIDENCE line", "", md)}),
    ]


def self_test() -> int:
    files = source_files()
    md = files["ship-skill/SKILL.md"].decode()
    bad = 0
    for label, mutate in _mutations(md):
        print(f"\n  RED PROOF — {label}")
        # A mutation that changed nothing certifies nothing — and it reports as
        # "the gate stayed green", which sends you auditing a check that is fine.
        # Say which one it is.
        # ⚠ COMPARE THROUGH _bytes(). The first version of this guard compared the
        # dicts directly; mutations return str values while `files` holds bytes, so
        # it was never once equal and the guard was dead code that read as passing.
        # Caught by injecting a deliberately stale mutation and watching for the new
        # message — which did not appear.
        if _bytes(mutate(files)) == _bytes(files):
            print(f"  ✗✗ THE MUTATION WAS A NO-OP on {label!r} — it is stale, not the "
                  f"check. Mutate the property, not a phrase that has been reworded.")
            bad += 1
            continue
        try:
            fails = check(_zip(mutate(files)))
        except Exception as e:            # a missing member is also a failure
            fails = [f"raised {type(e).__name__}"]
            print(f"  FAIL · raised {type(e).__name__}")
        if not fails:
            print(f"  ✗✗ THE GATE STAYED GREEN on {label!r} — it is not measuring this")
            bad += 1

    # The README is not inside the package, so the loop above cannot reach the
    # claims it makes about this script. Same discipline, done separately: break
    # the claim, require a failure, and refuse a mutation that changed nothing.
    with contextlib.redirect_stdout(io.StringIO()):
        check(_zip(files))                       # silent clean run, for the real count
    real = (HERE / "README.md").read_text()
    clean, n_mut = len(RAN), total_mutations()
    for label, text in _readme_mutations(real):
        print(f"\n  RED PROOF — {label}")
        if text == real:
            print(f"  ✗✗ THE MUTATION WAS A NO-OP on {label!r} — a mutation that "
                  f"changes nothing certifies nothing")
            bad += 1
        elif not readme_claims(text, clean, n_mut):
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
    if "--build" in sys.argv:
        build()
        raise SystemExit(0)

    # Grade skill/ — the source. Never the committed zip: that is what let a 108-line
    # merge pass unread.
    print(f"skill/  ({', '.join(sorted(p.name for p in (HERE / 'skill').iterdir()))})")
    f = check(_zip(source_files()))
    for d in stale_artifacts():
        f.append(d)          # one entry per artifact, so the count matches the lines
        print(f"  FAIL · {d} no longer matches skill/ — the file a stranger "
              f"downloads is not the file that was just graded. Run --build.")
    # The README describes this script; these two grade that description.
    for d in readme_claims((HERE / "README.md").read_text(), len(RAN),
                           total_mutations()):
        f.append(d)
        print(f"  FAIL · {d}")
    print()
    print("PACKAGE OK" if not f else f"{len(f)} FAILURE(S)")
    raise SystemExit(1 if f else 0)
