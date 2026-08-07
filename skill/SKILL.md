---
name: ship-skill
description: Finish serious work properly - code, writing, research or analysis. Build in rounds, prove each with evidence, then adversarially try to break it. Runs SOLO (self-review) or MULTI (an independent reviewer that never saw you think). Ends in one verdict - SHIP, DRAFT or BLOCKED - and turns whatever went wrong into a durable rule, so the workflow gets better at YOUR work over time.
---

# ship-skill

A way of finishing work so that "done" means *checked*, not *finished typing*.

Work fails in three ways: it looked right and wasn't, it fixed one instance of a problem
that existed in five places, or nobody could tell afterwards whether it actually worked.
Every step below makes one of those harder.

**Shape:** read SCARS → understand → build in rounds → prove each round → adversarial
back-pass → one verdict → record the scar.

**Before Step 1, read `SCARS.md`.** Once it has entries it is the only file here
written by
experience rather than by someone guessing in advance what would go wrong.

---

## What this is

**Persuasion, not enforcement.** Nothing here can stop a model claiming a check passed
without running it, so a green report from this skill is a *claim* — the evidence it
cites is what makes it checkable. Where being wrong is expensive, put a real gate
outside the model: CI, a required reviewer, a `Stop` hook that blocks until an external
verdict is on disk. The skill makes the judgement better; the gate makes it checkable.

---

## The pins

Five trial runs, three model families. **These are the rules that did the work** — every
one of them caught something in a real run. If you read nothing else, read these; the
rest of the file is the reasoning behind them and the cases they came from.

| | |
|---|---|
| **Distrust a check that passes.** | A green suite can be evidence pointing the *wrong way* if the tests are wrong in the same direction as the bug. |
| **Read what a source says about itself.** | The load-bearing fact hides in a comment, a header, a note at the top of a CSV — where every automatic check skips it, and every total still reconciles. |
| **Unsupported is not refuted.** | "I lack data to support this" is DRAFT. "The data refutes this" is BLOCKED. Absence vs contradiction. |
| **Scope widens free, narrows never.** | Free to *name* something outside it; never free to act on it. And narrowing after you start is how a known defect launders into a SHIP. |
| **No drive-by, at every size.** | File, function, paragraph, sentence, **clause**. The tell: the deletion feels *tidy* rather than *requested*. |
| **Missing evidence is not a pass.** | A check you could not run is `N/A` with the reason, never a quiet omission. |
| **Loop on evidence, not confidence.** | If you cannot name what would end the loop before starting it, you have a habit, not a loop. |
| **Same defect = finish the sweep. Different defect = name it, don't touch it.** | Defect class is the line between thoroughness and a drive-by. |
| **Say what you did not check.** | The boundary is part of the result. It explains a SHIP; it never rescues one. |
| **A verdict is retractable.** | Anything that can only promote will eventually be wrong and stay wrong. |

Everything below is *why*, and the cases that produced each one.

**Reading this file.** A `⚠` marks something that has actually bitten. **`+ EXCEPTION`
marks a passage that repeats a rule you have already read AND changes it** — a carve-out,
a boundary, a case where the rule inverts. Those are the only repetitions you cannot
skim; anything else restating a pin is emphasis and can be skipped on a second pass. Two
readers reported skimming exactly these paragraphs and missing the sentence they needed,
because nothing distinguished the two kinds.

---

## Rule 0 — one verdict, and it fails closed

⚠ **Failing closed is a tie-break, not a thumb on the scale.** Everything below warns at
length against a wrong SHIP, and that asymmetry is itself a bias: **a defensive DRAFT on
clean work is also a false report.** It costs the reader a decision they should not have
had to make, and it costs you the one thing the verdict is for — being believed when you
say SHIP. Downgrade when a rule says to, never to feel safer.

**Every run ends with exactly one of these three words.** It fails closed *when genuinely
tied*: anything short of
proven-good reports as DRAFT or BLOCKED, never as SHIP-with-caveats.

| Verdict | Meaning |
|---|---|
| **SHIP** | Every applicable check passed *with evidence*. Safe to send, merge, publish, submit. |
| | **The ordinary happy path is SHIP:** errors found, all of them fixed, the fixes proven, the boundary stated. Finding and fixing problems is not a reason to downgrade — it is the work. |
| **DRAFT** | The work is sound but the bar was not fully met — usually missing proof, not missing quality. |
| **BLOCKED** | A real problem was found. Say what it is and what would unblock it. |

**DRAFT vs BLOCKED, pinned.** Both fit too many situations otherwise — two careful
readers reached different words from identical facts:

> **BLOCKED — the WORK is wrong**, or cannot proceed. A defect that makes the output
> misleading, unsafe or unusable. Something is broken and you know it.
>
> **DRAFT — the PROOF is short.** Nothing wrong with what is there; something is
> *missing*: a check you could not run, evidence you could not gather, a decision that
> is not yours to make.
>
> ⚠ **Two things arrive in the same sentence and split here:**
>
> | | |
> |---|---|
> | *"I lack the data to support this"* | **DRAFT** — unsupported. The proof is short; it may well be true. |
> | *"the data I have refutes this"* | **BLOCKED** — refuted. The work is wrong and you can show it. |
>
> Unsupported is an absence; refuted is a contradiction. Treating a refuted claim as
> merely unsupported is how a wrong statement ships with a caveat instead of being fixed.
>
> ⚠ **And this does not assume the work is yours.** A defect inherited in a handed-over
> artifact is judged on the artifact's state at the seal, not on who caused it. "It was
> already like that" changes who fixes it, never what the verdict is.
>
> **The test: is the problem in the work, or in the proof?** Work → BLOCKED. Proof →
> DRAFT. **When both, BLOCKED wins** — it is the louder word, and this fails closed.

### What counts as "in scope" — the line that decides the verdict

Rule 0 forbids SHIP-with-caveats. Step 6 requires a *"What was NOT checked"* section.
Those look contradictory and are not, but only once scope is pinned:

**Scope is declared at Step 1 and cannot be narrowed once work begins.** Widening it is
free to **name** and never free to **act on** — Step 2 still forbids changes nobody asked
for, so report what you found outside the boundary and let them decide. Narrowing it needs the person who asked — otherwise "out of scope" becomes a
way to launder a known defect into a SHIP, which is the failure this rule exists to
stop.

| Situation | Verdict |
|---|---|
| A known, unfixed defect **inside** declared scope | **DRAFT** — or BLOCKED if it is a real problem. Never SHIP. |
| Something you **could not verify**, and which is **not required** for the claim you are making | SHIP is available. The boundary goes in "What was NOT checked". |
| A **required** in-scope check you could not run | **DRAFT.** "Missing evidence is not a pass" governs — an unrunnable check does not become optional by being unrunnable. |
| Something genuinely **outside** declared scope, **and not harmful** | SHIP is available. Name it so nobody assumes it was covered. |
| Out of scope **and harmful if acted on** — misleading, unsafe, someone will decide from it | **BLOCKED**, whoever wrote it and whatever the scope said. |

**And when a fix needs data you do not have, do not invent it.** The verdict rules below
cover what to *report*; this covers what to *write*. **Leave the wrong claim standing and
flag it** — a substituted plausible number is a new error with your name on it, and it is
worse than the original because it looks checked. Delete only if leaving it would mislead
more than removing it, and say which you chose.


**+ EXCEPTION — scope decides whose job it is; HARM decides whether it can ship.** Those two rules
collide on an inherited defect that is also out of scope — that is the resolution. A
boundary that lets you stay silent about something dangerous is not a scope rule, it is
an excuse.

**The test, when the table does not settle it:** *if the reader knew this, would they
be surprised the verdict was SHIP?* If yes, it is not SHIP. That question resolves
the cases the table cannot, and it resolves them the safe way.

**Missing evidence is not a pass.** A check you could not run is `N/A` with the reason
stated. *"I can't check the numbers, I don't have the source data"* is a legitimate N/A.
*"It looks fine"* is a FAIL wearing a friendly face.

Never report SHIP to be agreeable. A wrong SHIP costs far more than an honest DRAFT.

---

## Step 1 — Understand before building

**Restate the goal in your own words** — that is what surfaces a misread of the request
itself. Include: what "done" looks like **concretely**, what is explicitly **out of
scope**, and anything **ambiguous**. Ask about the ambiguity now; a wrong assumption is cheapest to fix here.

⚠ **If you cannot ask — you are a subagent, a scheduled run, or nobody is there — do
NOT resolve the ambiguity by picking.** State the question, take the **narrower**
reading, and carry both to the seal: *"I read X as A; if you meant B, this needs
redoing."* A question answered by assumption looks identical to a question never
asked, and the narrower reading fails safe — it under-delivers visibly rather than
over-reaching invisibly.

**Say what is in scope and what is not, explicitly.** That declaration is what Rule 0's
verdict table reads later, and it cannot be narrowed once you start — so draw it now,
honestly, while you have nothing to protect.

**The short path needs BOTH conditions: small *and* low-stakes.** If the request is one
small, clearly-specified, low-stakes change, say so, keep the restatement to a single
line and run one round.

⚠ **Small is not the same as cheap to get wrong.** A one-line production config change,
a price, a permission, a published correction — each is a two-minute edit and none of
them is low-stakes. Size measures the diff; stakes measure what happens if it is wrong,
and **only stakes decide the ceremony.** When they disagree, stakes win.

**Ceremony proportional to stakes** — a full workflow on a genuinely trivial fix wastes
the person's time and they will stop using this. But that cuts one way only: cheap work
gets the short path, expensive work does not get it for being short.

---

## Step 2 — Build in rounds, one theme per round

A round is a set of changes that belong together and can be judged together. An unrelated
cleanup mixed into a round makes it impossible to evaluate and impossible to undo.

**Change only what was asked for.** No drive-by improvements, renames, reformatting or
"while I was in there" tidying. If you notice something else wrong, *say so and leave it*.
An unrequested change is indistinguishable from a mistake to whoever reviews it next, and
it is why a one-line fix arrives as a forty-line diff nobody can check.

---

## Step 3 — Prove the round

**Read what a source says about itself, not only what it tabulates.** Comments,
headers, footnotes, README lines, the note at the top of a CSV — those carry meaning
and every automatic check skips them. A parser reading only the data can reconcile
every figure perfectly while the document's stated basis is inverted by one line it
never saw. **The most damaging errors are the ones where all the numbers are right.**

State what you checked **with the actual result**:

**Description is not proof.** "I updated the totals" describes. "The totals now read
4,812 and sum to the line items, which they did not before" proves.

**Give the before, not just the after.** "No errors remain" measures nothing if there were
zero errors before you started.

**Check the thing, not a proxy.** If the goal is "the link works", the proof is that the
link resolves — not that the link text looks right.

**Sweep the class.** Fixed a problem? Find the same shape everywhere and fix every
instance, or list the ones you deliberately left and why. Fixing only the one in front of
you is how the same mistake ships three times.

⚠ **Sweep and no-drive-by are not in conflict — the line between them is the DEFECT
CLASS.** Fixing the same defect everywhere it occurs is *finishing the ask*, even in
files nobody named. Fixing a *different* thing you noticed on the way is a drive-by.

> One bug reported → sweep every instance **of that bug**. One bug reported → do not
> also rename the variable, reformat the file, or fix the unrelated thing two lines down.

Same defect, wider blast radius: **do it, and say you did.** Different defect: **name
it, do not touch it.**

**+ EXCEPTION — permission bounds the sweep, not just scope.** Finding the same defect in six
sibling documents does not authorise editing six documents — the ask covered one, and
"it is the same bug" is a reason to *report* the other five, never a licence to edit
them. **Sweep the class within what you were given; list the class beyond it.** A run
that widens its own blast radius on the strength of being right is the drive-by problem
wearing a better argument.

**Finish the sweep you print.** If you list places to check, check *all* of them. A
half-worked list is worse than no list because it looks like diligence. (Real failure: a
sweep flagged fourteen files, eight got checked, and one of the six skipped was broken in
exactly the way the sweep was looking for.)

**Distrust a check that passes.** The dangerous one is not the failing check but the one
that *passes for the wrong reason* — anything written to expect the old, incorrect answer
keeps passing for as long as the mistake survives, and looks like coverage throughout. So
when two checks on the same thing disagree, do not assume the failing one is wrong.
**That contradiction is the signal** — usually one of them was written against a truth that
has since changed, and the other has been quietly holding the error in place.

**+ EXCEPTION — no-drive-by applies at EVERY granularity, and a COMPELLED deletion is not one.** It reads as being about files
and diffs; the failure that actually happens is smaller. You have legitimate cause to
touch one sentence, and while rewriting it you quietly drop a clause nobody asked about.
Same rule, one level down — **file, function, paragraph, sentence, clause.** Cause to
touch the container is not cause to change what is inside it.

**Two kinds of deletion, and only one is a drive-by:**

- **Tidy** — you removed it because it looked better gone. That is a drive-by at any
  size. Put it back.
- **Compelled** — the correction cannot be expressed with it still there. Fixing a
  sentence that wrongly says two periods matched forces out the clause *"as in Q1"*,
  because that clause asserts the thing you are correcting. **That is part of the fix,
  not a drive-by** — and it must be *named in the seal*, because a reader diffing the
  text will see a deletion nobody asked for.

The test is not how it feels, it is whether the correction **survives without it.** If
you can make the fix and keep the clause, keeping it is mandatory. If you cannot, say so. **Re-read your own
diff at the smallest unit you changed**, not at the level you were thinking in.

**Kill the stale claim.** Changed how something behaves? Correct everything that
*describes* the old behaviour — comments, instructions, a summary, a heading — in the same
round. Two places giving different answers is worse than one wrong answer, because nothing
catches it.

---

## Step 4 — The third eye: an adversarial back-pass

Stop building. Try to **break what you made.** Read it as if you had never seen it and
someone is asking you to approve it — not to admire it.

Four lenses, **one at a time**, because each catches what the others miss:

**Report them as four labelled blocks, or four explicit N/As with reasons.** Merged into
one paragraph, *"I considered all four"* is unfalsifiable — and merging is what a run
produces when it did not do them separately. Separate headings are the only evidence that
they were separate passes.

1. **Correctness** — is anything actually *wrong*? Numbers, logic, facts, names, dates,
   claims.
2. **Completeness** — what is *missing*? A case not handled, a question not answered, a
   section promised and never written.
3. **Blast radius** — what does this affect that nobody listed? What breaks downstream?
   How would someone undo it?
4. **The embarrassment test** — what, **if anything**, is the first thing the most
   demanding reader would object to? Name it; fixing is Step 5. **If the honest answer is nothing, the block
   says "nothing to report."** Four labelled blocks is the shape; an empty one is a
   legitimate finding. The rule below about not manufacturing a problem applies hardest
   here, because this is the lens that invites invention.

> **You are being asked for analysis, not agreement** — and equally, do **not** manufacture
> a problem to look useful. State the strongest case that this work is wrong, then the
> strongest case that it is right, and say which you believe and why. If you cannot judge
> something on the evidence available, say exactly that and **name what you would need**.
> *"I can't verify this — I'd need X"* is a real answer, worth more than a confident guess.

### ⚠ The known weakness

Run in the same conversation, this is **the same model reviewing its own work** — a
genuine limitation, not a formality. Its blind spots are *correlated*: it finds the errors
it was already equipped to notice and misses the ones built into how it approached the
problem. Better than no review, weaker than an independent one. Step 4b is the fix.

Three things make it less weak, and they are required:

- **Re-read the actual artifact** — the real text, the real numbers, the real output. Most
  self-review failures review the intention instead of the result.
- **Default to refuted when uncertain.** Treat a maybe-problem as a problem and
  investigate. Uncertainty resolved as "probably fine" is how everything ships.
- **Name what you could not check.** End the pass with an **explicit list** of what remains
  unverified. That list is the honest boundary of this workflow's confidence, and the human
  reading it can decide whether it matters.

**When it genuinely matters, ask a human — or a different AI — to look.**

---

## Step 4b — SOLO or MULTI: how independent the review was

Correlated blind spots do not yield to trying harder in the same breath. They yield to
**changing what the reviewer knows.** These modes differ in independence, not effort.

**SOLO** — Step 4 in this conversation. The default, and genuinely useful: most defects are
ordinary and a disciplined re-read finds them. Use it when being wrong is cheap **and
recoverable** — a draft, an internal note, an experiment, anything you will look at again
before it matters.

**MULTI** — the review happens somewhere that **never saw the building.** Use it when being
wrong is expensive: client-facing, published, sent to many people, spending money, or
embarrassing in public. A reviewer who watched you reason is already persuaded by your
reasoning; one that sees only the artifact has to be convinced by the artifact — the actual
test.

### The ladder — once you have chosen MULTI, use the LOWEST-NUMBERED rung available

*(Rung 1 is the strongest and rung 4 is none at all, so "highest rung" would read as doing nothing. Lower number, stronger review.)*

(Choosing between SOLO and MULTI is the paragraph above; this table is only about how to run
a MULTI you have already decided on. Having a subagent available does not make MULTI
mandatory.)

| Rung | What it removes |
|---|---|
| **1. A different model family** | Contamination, and blind spots that sit in different places. The strongest MULTI. Name the model. |
| **2. A fresh subagent / agent task** | Most of the contamination, where you can spawn one — **check, do not assume: a subagent usually cannot spawn a subagent, so this rung is often unavailable to the very run that needs it.** Two caveats even when it works: *you* write the prompt, so contamination drops by discipline rather than by mechanism; and it may run a different, often smaller model, so name what it was. |
| **3. A new conversation**, pasted by hand | The same independence as rung 2 and the same caveat — you still write what it sees — but by hand. The fallback wherever there are no subagents. |
| **4. Same conversation** | Nothing. This is SOLO — call it SOLO. |
| **— Unavailable** | MULTI was right and **the environment cannot provide it.** Not a rung: a stated fact. |

⚠ **Rung 2 is not available to a subagent** — subagents cannot spawn subagents, and the
same holds for many scheduled and embedded runs. When MULTI is indicated and nothing
above rung 4 is reachable, **do not quietly declare SOLO and hope the recommendation
gets read.** Say it in the seal:

> *"MULTI indicated; unavailable in this environment (no subagent, no second
> conversation). Reviewed SOLO. An independent look is still owed before this is relied
> on."*

"SOLO because I chose it" and "SOLO because nothing else was reachable" are different
claims about how much this was checked.

**Rung 3 means a new conversation, not a new message.** A fresh message in this thread still
has all of the building in its context and buys nothing. And MULTI happens *after* Steps 1-3
are finished — you review an artifact, not a work in progress.

**The reviewer gets exactly four things:** the artifact, the original request, the four
lenses, and one question — *would you approve this, and what is the strongest argument that
it is wrong?* Nothing about *how you built it*: not your plan, your reasoning, "here's what I
was going for", or your verdict. Those are exactly what would contaminate it. Bring the
findings to Step 5.

**MULTI is not "SOLO with more steps."** Reviewing in the same conversation and calling it
MULTI buys the ceremony, none of the independence, and a seal that claims something untrue.

> **Say which mode in the seal. "SOLO" is an honest answer, not a confession** — the
> dishonest answer is an unearned "MULTI".

**When it really matters,** add single-lens passes: one reading only for factual
correctness, one as the least sympathetic reader you can imagine. Separate passes beat one
combined pass, because a reviewer looking for everything drifts into looking for nothing.

---

## Step 5 — Fix, then re-prove

Everything the back-pass found gets fixed and **proven again**. A fix is done when the
failure no longer happens and you have said so with evidence — not when it was applied. If
a fix touches what an earlier round proved, that proof is stale. Redo it.

**Take the ceiling from the person, not from thin air.** If they gave you a limit —
passes, time, budget — that is the ceiling. **If they did not, do not invent one**; stop
on no-progress instead. A made-up "three passes" is a number nobody chose, and it will
cut off a run that needed four exactly as confidently as it bounds one that needed none.

⚠ **And do not manufacture a loop at all when no new feedback can change the next
action.** Looping is for work where each pass *learns* something — a check that can go
red to green, a reviewer who can object. If nothing between passes could alter what you
do next, that is one-shot work: do it once, well, seal it. Iterating without new
information produces the same answer at rising cost and looks like diligence.

Then stop for one of
exactly four reasons, and **say which**:

> **Do not loop on confidence. Loop on evidence.** *"I think it's right now"* is not a
> stop condition — the tests pass, the schema validates, the citations resolve, the
> reviewer approved. If you cannot name what would end the loop before you start it,
> you do not have a loop, you have a habit.

| | |
|---|---|
| **PASSED** | The check succeeds. The only real success. |
| **CEILING** | Out of room, still failing, **and the failure kept changing.** Possibly converging. That is the limit they gave you — or, if they gave none, the point at which continuing needs someone to say so. |
| **STALLED** | The same failure **twice** running, unchanged. **Stop immediately.** |
| **UNFIXABLE HERE** | You checked thoroughly and found defects you cannot fix — missing data, missing access, someone else's call. **No number of passes touches these.** Name each and who can act on it. |

**+ EXCEPTION — UNFIXABLE HERE is neither a failure nor a stall.** The other three assume a check
you can retry; this is work that is finished as far as you can take it, and looping on
it just produces the same answer more expensively. It routes to **DRAFT** — the proof is
incomplete, the work is sound — unless a defect makes the output actively misleading,
which is BLOCKED.

**CEILING and STALLED** both mean "not fixed", and the difference is what they license. **Both stop
the loop and get reported** — the limit is the discipline, and drifting past it is
how "a few more passes" becomes an afternoon. What differs is what happens next: CEILING
means *another run is worth granting* — so a human decides. If they gave no limit in
the first place, that decision is theirs too: you do not get to grant yourself more
room on a budget nobody set. When a human does grant more, that is **a
new limit, set deliberately, with the reason stated.** STALLED means *more passes buy nothing* — change
the approach, the assumption under it, or what you are checking, then start a fresh count.

**When stalled, do not raise the ceiling.** That is the instinct and it is wrong. Collapse
these two into "didn't work" and you will reliably spend the next hour on the version that
cannot work.

> ⚠ **Invisible trap.** A check that produces *no output* on failure makes every failed
> pass look identical whether you are progressing or not. Make it say something, or judge
> progress on the work itself. **Silence is not evidence of being stuck, or of progress.**

---

## Step 6 — Seal it

Report, briefly:

- **Verdict** — SHIP / DRAFT / BLOCKED, decided by Rule 0's scope table. A known
  unfixed defect inside declared scope is **never** SHIP, however well everything else
  was proven.
- **What changed** — plain language, what a reader would notice.
- **How it was proven** — checks and results.
- **What was NOT checked** — the honest boundary: what you could not verify, and what
  sat outside the scope declared at Step 1. This section explains a SHIP; it never
  rescues one.
- **How to undo it** — if it is that kind of work.
- **Stopped because** — PASSED / CEILING / STALLED / UNFIXABLE HERE, after how many
  passes. All four, or the fourth is a rule the seal cannot report.
- **Mode** — SOLO or MULTI, truthfully; if MULTI, which rung and what reviewed it.
- **Scars** — did an existing scar apply, and did you follow it? Did this run produce a
  new one? If yes, **print the scar block, ready to paste, including its EVIDENCE line**,
  offer the updated file, and say durability is unverified — never that it was saved. If
  no, say "no scar" — saying it out loud is what stops this step being quietly skipped
  forever.

Then stop. Do not append things you did not do and call them next steps unless asked.

### A verdict must be retractable

**A system that can only promote is a burndown chart with extra steps.** When later
evidence contradicts a sealed verdict, retract it explicitly — name the original
evidence and what beat it, and record a scar; that is the clearest case there is. You
may retract your own seal from earlier in the same run.

---

## Step 7 — SCARS: turn what went wrong into something that cannot go wrong again

Everything above improves *this* work. This step is the only one that improves the **next**
work. A conversation ends and everything it learned dies with it; notes don't help, because
nobody re-reads their notes before starting. **A scar is a mistake converted into a rule that
is re-read at the start of every run** — Step 0, from the file, not remembered from a
conversation.

⚠ Nothing "loads itself." The only mechanism is that you read `SCARS.md` before Step 1,
which is discipline — the same kind that makes notes fail. What makes it different is
that it is *one short file, in the place the work happens, read at a fixed point*, rather
than a notebook you might consult. That is a real difference and a small one, and
claiming more would be exactly the unearned promise this skill exists to catch.

### Two layers, and the difference is authority

**FOUNDING RULES are yours** — written by hand, deliberately, at the top of `SCARS.md`.
Not lessons from a bug but the terms your work runs on ("never send a client a number I
haven't traced to source"). **Nothing learned may ever overwrite one.**

**LEARNED SCARS append below**, at lower authority on purpose: a rule extracted from one
bad afternoon should not weigh the same as one you chose while thinking clearly.

A fresh copy of `SCARS.md` may also carry a **CANDIDATES** block — proposed founding rules
that nobody has ratified. **It has no authority at all: not a founding rule, not a scar, and
not an "entry" for the purposes of the seal's scar question.** Ignore it when working.

**Mention once that it is waiting on RATIFICATION — not on being written.** The drafts
are already there; what has not happened is the person deciding which they believe,
rewriting those into FOUNDING RULES in their own words, and deleting the rest. Saying it
is "waiting to be filled in" describes the wrong gap and invites Claude to fill it,
which is the one thing that must not happen: a founding rule carrying someone's
authority has to be one they chose.

**Until they ratify, FOUNDING RULES is legitimately empty** and the run is proceeding on
this skill's steps alone. Say that once, plainly, rather than letting an unratified
CANDIDATES block read as though rules are in force.

### Recording one

When something went genuinely wrong — a real error, a wrong assumption, a thing that had
to be redone — write it in exactly this shape and add it to the LEARNED section:

```
WHAT BROKE   the summary quoted a number that was never in the source
COST         it went out to 40 people before anyone noticed
CAUGHT BY    re-reading the source, not re-reading my summary
RULE         every figure in a summary gets traced back to the sentence it came
             from, before the summary is finished
GUARD        Step 3's check list — added "every number traced to source"
EVIDENCE     the figure appeared in my draft and in no paragraph of the source;
             I searched all 14 pages before concluding that
```

**All six lines, every time.** The first three — WHAT BROKE, COST, CAUGHT BY — are the
diary. The last three are what make it a defence, and they are the three people skip:

- **RULE is an instruction, not a regret.** "Be more careful with numbers" is not a rule —
  nothing can follow it. "Trace every figure to the sentence it came from" is, because you
  can tell whether you did it.
- **GUARD names where the rule now lives. "A question I now always ask" is a real guard,
  and often the only one available** — if you are auditing someone else's repo you cannot
  add a test to it, and editing this skill to install a guard is itself a drive-by. Do not
  reach for `NONE` because you could not write code. Otherwise: a step here, a checklist
  line, a test, or
  **a question you now always ask, which is a real guard and not a lesser one.** If you
  edited nothing, say that; an invented "added to Step 4" is false and reads as stronger,
  which is the exact incentive to avoid. If there genuinely isn't one, write
  `GUARD: NONE` **honestly**. An honest
  NONE is a hazard you know about; an invented guard reads as protected and is worse than
  nothing.
- **EVIDENCE names what in *this run* proved it** — what happened, not why it sounds
  sensible. This is the difference between a rule and a superstition. Without it, the
  workflow fills with confident restrictions nobody can trace, refusing things for reasons
  that were never true.

### ⚠ A long session has no seal — record at the failure, not at the end

The scar block is emitted at Step 6. **A session that never reaches Step 6 never emits
one**, and long autonomous work is exactly that: dozens of turns, continuous, no natural
stopping point. The trigger is sound and it simply never fires.

That is not hypothetical. In one continuous session four scars were earned and none
written — a screenshot used as a visibility check that cost two wrong fixes, a missing
`timeout` binary misread as an empty result, a commit message describing a fix that was
not in the commit, and a feature declared broken on evidence that predated it. Every one
qualified. The seal never came.

**So when a failure costs something, write the scar THEN.** Not "at the end", because
there may not be one. The seal still asks — that question becomes "did I record the ones
I hit?" rather than "should I invent one now?"

⚠ **And this makes the one-per-run rule a per-FAILURE rule, not a per-session cap.** Four
genuine scars in one session is four, not one. The triage below is what keeps that honest:
each must have cost something, be able to recur, and produce a rule you can tell whether
you followed. A long session earns more scars because it hits more failures — capping it
at one would discard the ones that came earliest, which are usually the ones that cost the
most.

### ⚠ At most ONE scar per DISTINCT failure — and most work produces none

One careful pass over a 25-line document once produced **three scars, all with genuine
evidence.** Each was defensible and the file was worse for them, because a `SCARS.md`
nobody reads has failed exactly the way notes fail.

**A scar is about the RUN, not about you.** The trigger is not "I made a mistake", it is
"this run hit something that will happen again". Finding a trap in someone else's
document that nearly worked is a scar; you did not cause it and that is irrelevant.
Checking work you did not write is the most common real use of this skill, and a trigger
phrased as self-blame silently excludes it.

**Record one only if it clears all three:**

1. **It cost something** — rework, a wrong answer that got out, real time. "I noticed a
   thing" is not a scar.
2. **It would recur** — the same shape can happen again on different work. A one-off
   quirk of this file is not a rule.
3. **The rule is actionable** — you can tell whether a future run followed it.

If several describe the SAME failure, **write the most expensive framing.** If none do, **"no scar" is the
correct and common answer** — most good runs produce none.

### Undoing one

**Copy `SCARS.md` to `SCARS.prev.md` before adding a scar** — or just keep the old text
somewhere for a day. A lesson from one confusing afternoon can be **wrong** — wrong cause,
or rule drawn too wide — and a wrong rule is worse than no rule because you will actually
follow it. Without a copy it is permanent; with one, undoing it takes ten seconds.
**Founding rules are untouched by this**; they change only by hand.

### Getting the scar into the file

**Always do all three of these, in order. Do not try to work out which case you are in.**

Three earlier versions of this passage asked you to classify the environment first —
local files, synced-and-ephemeral, or write-fails — and pick a branch. Two independent
reviews and one live trial reached the same conclusion: **the classification is not
decidable from inside the run.** The trial agent could not tell which case it was in,
did all of it anyway, and reported that the branching had bought nothing. So the
branch is gone. Doing all three costs one short block and a sentence.

1. **Print the scar block in the seal**, formatted and ready to paste. This is the only
   version that survives if everything else about the file handling goes wrong, and it
   costs almost nothing.

2. **Write the updated `SCARS.md` and offer it as a file.** If you can write to the
   skill folder, do — and copy the old text to `SCARS.prev.md` first, so a wrong lesson
   is undoable. If you cannot, hand the updated file over.

3. **Say plainly that durability is unverified**, in one sentence, every time.

⚠ **Reading the file back proves the WRITE, never the DURABILITY** — and that is the
whole reason step 3 exists. A write into a workspace that is discarded at the end of the
session succeeds, reads back correctly, and persists nothing. There is no check
available from inside the run that distinguishes that from a real save, so the honest
report is *"written; whether it persists depends on your setup — keep a copy."*

**Never say a scar was saved.** Say it was written and printed, and that saving it is
theirs to confirm. Skipping the paste loses the scar with nothing to warn you — the run
still looks successful — which is why the seal asks about the scar at all: it makes the
loss visible now rather than three months from now.

### Carving a new skill out of scars

When **three or more scars land in the same territory**, that territory has earned its
own skill. The procedure is in `SCARS.md`, next to the scars it operates on.


## The checks — mark each PASS / FAIL / N/A-with-reason

Skip what does not apply, but **say you skipped it and why.** Silence reads as "passed".

**All work**

| Check | Question |
|---|---|
| Correct | Is it factually and logically right? |
| Complete | Does it cover everything asked, and nothing it shouldn't? |
| Evidence | Is each claim backed by something checkable? |
| Clarity | Would the intended reader understand it without you explaining? |
| Stale claims | Does anything still describe the old behaviour? |
| Reversible | Can this be undone, and is that written down? |
| Scars read | Did you read `SCARS.md` first, and did any entry apply? |
| Mode named | Does the seal say SOLO or MULTI, truthfully? |

**Code and technical work** *(mark N/A for writing, research or analysis)*

| Check | Question |
|---|---|
| Tests | Do tests exist for *this* change, and did they actually run? |
| Parses **and loads** | Does it lint clean *and start*? A syntax check answers "does this parse", never "do these names exist where this runs". |
| Security | Secrets, injection, permissions, unsafe defaults. |
| Reachability | Is every new thing actually *reached* by something? Dead code described as a feature is worse than a missing feature — nobody looks again. |
| Version + record | Version bumped, and change recorded where the project already records changes? |
| Rollback | Is the reverse path known? |

### Never tune against the check that will judge you

Adjust the work until a particular check passes and **that check now measures how hard
you tuned**, not whether the work is right — invisible from inside, because everything
is green. Keep an acceptance gate you did not touch: held-back examples, a second
reviewer, a case you never looked at. If you only had one check and you tuned against
it, say so: *"passes the check I tuned against; not independently verified."*

### The tests are also a suspect, not only the instrument

Tests are an artifact someone wrote, and they can be **wrong in the same direction as
the bug** — in which case a green suite is not weak evidence, it is evidence pointing
the wrong way. (Measured: a green 4/4 suite with two tests asserting an uncapped
discount as correct.)

**When code and its tests disagree with the documented intent, count the artifacts** —
spec, comments, naming and tests each vote; two against one usually means the one is
wrong, and a test is not exempt. Then:

1. Does the test assert the **documented** behaviour, or the current one? A test written
   from the implementation can never fail.
2. **Would it fail if the bug came back?** If you cannot say, restore the old code and
   watch. That is the only way to know a green test is load-bearing.
3. Does its **name** describe what it asserts? A name describing inverted behaviour is a
   stale claim, and correcting it **outranks no-drive-by**.

A lying test is corrected and reported, never quietly deleted.

**On tests:** "the suite is green" is not evidence that *your* tests ran — prove they
executed, with a count before and after or the new test names in the output. And a test
that cannot fail proves nothing: if you strengthened a check, make sure the case it guards
against can actually occur, or you bought confidence without coverage.

---

## Scaling

| Situation | What to do |
|---|---|
| Small, clear, low stakes | One round, prove it, brief back-pass. Minutes. |
| Normal work | Full steps, one or two rounds, SOLO. |
| High stakes / irreversible / public | Full workflow, extra single-lens passes, MULTI at the lowest-numbered rung available, and — **unless a different model family has already reviewed it at rung 1** — say out loud that an independent reviewer is recommended before it goes out. |

The person can override:

| They say | You do |
|---|---|
| "quick pass", "sanity check", "don't overthink it" | One round. Still check it, still give a verdict. |
| *(nothing)* | Judge from the stakes. |
| "be thorough", "this really matters", "go deep" | Every lens separately, artifact re-read twice with a gap, MULTI, and **state explicitly** that an independent human should look before this goes out — plus a different AI, if one has not already. |

**What "quick" may never do:** skip the verdict, hide an uncertainty, or report SHIP on
something unchecked. It reduces how *much* you examine, never how *honestly* you report
it. If a quick pass finds something serious, stop being quick and say so.

> **On `tiny`/`lean`/`max`:** if your host has orchestrated fleets, those words route
> real cost — see *Meter routing* below. What they must never do is buy *less honesty*:
> they change how much you examine and how many agents you spend, never how truthfully
> you report it. If someone asks for `max` in a host that has no fleets, read it as "go
> deep" in the table above and say that is what you did.

---

## Meter routing (when a host has lean/max/tiny fleets)

If your environment has **orchestrated multi-agent qualities** (lean / max / tiny),
those dials control **cost shape**, not thoroughness:

| Dial | Use | Avoid |
|------|-----|--------|
| lean / default | Daily multi-step ships | — |
| tiny + explicit file list | Known small edits | Open-ended diagnosis |
| max | Small high-stakes irreversible work | "Ship N versions" / whole-product arcs in one run |

**Multi-version arcs = N smaller ships**, each proven and sealed — not one max fleet
that burns the agent ceiling. Do not stack two fleets on one working tree.

*(Carved 2026-08-07 from a real multi-hour max volume run that correctly BLOCKED
hollow stamps after ceiling/render failure — gates worked; the meter choice did not.)*


## What this skill will not do

- Report success for work that was not done or not checked.
- Say SHIP when a required check has no evidence behind it.
- Hide an uncertainty to sound more confident.
- Expand the job beyond what was asked without saying so.
- Claim MULTI for a review that happened in the same conversation.

*Created by Konyo. The discipline is his. This version runs anywhere and requires no second
AI — it uses an independent reviewer when the stakes call for one and the environment has
one, and never claims that working alone is as good.*
