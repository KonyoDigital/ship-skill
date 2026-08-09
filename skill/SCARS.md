# SCARS

Two layers — FOUNDING and LEARNED — and the difference between them is **authority**. (A
third block, CANDIDATES, is temporary scaffolding with no authority at all; it is meant to be
emptied and deleted.)

**Claude reads this file first, before Step 1.** Once it has entries it is the only
file here written by
experience rather than by someone guessing in advance what would go wrong — which is why
it is worth more per line than the rest of it.

A scar is six lines: `WHAT BROKE`, `COST`, `CAUGHT BY`, `RULE` (an instruction you can tell
whether you followed), `GUARD` (where the rule now lives — or an honest `NONE`), `EVIDENCE`
(what in that run actually proved it, which is the difference between a rule and a
superstition). Full reasoning in `SKILL.md` Step 7; not repeated here.

---

## FOUNDING RULES

**Yours. Written by hand, deliberately. Nothing learned may ever overwrite one.**

These are not lessons from a bug — they are the terms your work runs on. Write them when
you are thinking clearly, not when you are annoyed about something that just broke. Three
to six is plenty; twenty is a list nobody reads.

**(none yet)**

*This is the honest state, and it is deliberately not filled with plausible-sounding
placeholders — a founding rule Claude invented would carry your authority without your
judgement behind it, which is the exact failure the EVIDENCE line exists to prevent.*
*Until you write some, Claude runs on the LEARNED scars and this skill's own steps.*

---

## CANDIDATES — proposed, not ratified

**Authority: none. Claude must not treat these as binding.**

Yes — these were drafted by Claude, which is exactly why they sit here with no authority
instead of above with the founding rules. The section above is about *authorship*: a rule
carrying your name must be one you chose. This section is about *starting cost*: reacting to
five concrete drafts is usually faster than facing a blank heading, and a rule you rewrote
in your own words after disagreeing with a draft is still yours.

So use them as shapes, not as content. Each is the right form — an instruction you can tell
whether you followed. Move the ones you actually believe up into FOUNDING RULES **in your own
words**, delete the rest, and **delete this whole section once you have.**

1. Nothing leaves my hands that I have not read end to end myself, in the form the
   recipient will see it.
2. Every number and every quoted fact is traced to its source before it ships — the
   sentence, the cell, or the line of output it came from.
3. If I am not sure, the answer is "I'm checking" — never a confident guess.
4. I do not report a result I have not seen. No "should work", no "the tests presumably
   pass".
5. A change nobody asked for does not ship in the same batch as one they did.

---

<!-- ===== LEARNED BELOW · appended from runs that went wrong ===== -->

## Ratifying your founding rules — the conversation

The candidates above are **shapes, not content.** Until you replace them, this file has
no founding rules and every run proceeds on the skill's steps alone. That is a legitimate
state and it is also the thing stopping the loop from compounding.

**You cannot write these from first principles, and neither can Claude.** A rule invented
in advance is a guess about what will go wrong; the ones that hold come from things that
already did. So the conversation is short and it is about your past, not your intentions.

**Ask Claude to run it, or answer these yourself. Four questions:**

1. **What went out wrong in the last year — and what did it cost?** Not near-misses.
   Something that reached someone. One or two is plenty.
2. **What did you find out afterwards that you could have checked before?** This is where
   the rule lives. "I could have opened the source" is a rule. "I should have been more
   careful" is not.
3. **What do you already always do, that you would be annoyed to see skipped?** These are
   founding rules you have never written down. They are usually the strongest, because
   you have already been following them long enough to trust them.
4. **What would you refuse to do even under time pressure?** A rule that bends when you
   are busy is not founding — it is a preference, and it belongs lower.

**Then write three to six, in your own words, each with the thing that produced it.**
The evidence line is not decoration: a year from now it is the only thing that lets you
tell a rule you chose from a rule you absorbed. Three is plenty. Twenty is a list nobody
reads, which is the failure this whole file is built against.

**Delete the CANDIDATES block once you have them.** Two sets of rules with different
authority in one file is exactly the ambiguity the two-layer split exists to remove.

⚠ **Claude must not write these for you.** It can ask the questions, push back on a rule
that is not actionable, and draft wording *from answers you gave* — that is editing, and
it is welcome. Inventing the answers is not: a founding rule carries your authority, and
one you did not choose will be followed by every future run as though you had.

---

## LEARNED SCARS

Lower authority than the founding rules, on purpose: a rule extracted from one bad
afternoon should not carry the same weight as one you chose while thinking clearly.

At the end of a run, Claude prints a scar block — or hands you an updated copy of this
file. Paste it below, newest first, and save the skill. **Copy this file to `SCARS.prev.md`
before you change it — adding a scar OR removing one** — or just keep the old text somewhere
for a day. A scar drawn from one confusing afternoon can have the wrong cause or too wide a
rule; without a copy that is permanent, with one it takes ten seconds to undo.

**Deletion needs the backup more than addition does**, and the copy only goes one deep — the
next change overwrites it. The durable record of a scar is the block printed in the seal, so
when you remove one, note in that run's seal which scar went and why. Full reasoning in
`SKILL.md` Step 7.

---

### Format — this is an EXAMPLE, not real history

*Delete this block once you have a real scar. It is labelled because an example mistaken
for real history is its own bug.*

```
WHAT BROKE   the summary quoted a figure that was not in the source document
COST         it reached 40 people before anyone checked
CAUGHT BY    re-reading the source — not re-reading the summary
RULE         every figure in a summary is traced back to the sentence it came
             from, before the summary is called finished
GUARD        Step 3 checklist — "every number traced to source"
EVIDENCE     the figure appeared in my draft and in no paragraph of the source;
             I searched all 14 pages before concluding that
```

---

### Scars

*(none yet — the honest state of a skill nobody has used in anger.)*

<!-- paste scar blocks below, newest first -->

---

## When to carve a new skill

Watch for **three or more scars in the same territory** — not the same mistake three times
but the same *area*: three about numbers, three about client-email tone, three about one
system. That area is recurring work and has earned its own instructions:

1. **Write a sibling skill folder** named for the territory — `checking-figures`,
   `client-emails`, `monthly-report`.
2. **Put the rules in as procedure**, not warnings: steps, order, specific checks, the
   phrasing that worked, the trap that keeps catching you. Scars are raw material; the
   skill is the finished procedure.
3. **Name the scar each rule came from.** Recorded origins survive someone asking "do we
   still need this?"; a rule without one gets deleted by the first person tidying up, and
   then it happens again.
4. **Leave a pointer here**, so this skill loads the child in that territory.
5. **Delete those entries from `SCARS.md`.** Not housekeeping — the file stays short
   *because* things graduate out of it, and one nobody reads has failed like notes fail.

The loop: **work produces scars → scars accumulate into a territory → the territory becomes
a skill → the skill makes that work reliable → and the workflow is now better at your job
specifically, not at jobs in general.** Nobody can hand you that version; it can only be
grown.

---

