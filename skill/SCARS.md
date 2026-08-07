# SCARS

Two layers — FOUNDING and LEARNED — and the difference between them is **authority**. (A
third block, CANDIDATES, is temporary scaffolding with no authority at all; it is meant to be
emptied and deleted.)

**Claude reads this file first, before Step 1.** It is the only file here written by
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

## LEARNED SCARS

Lower authority than the founding rules, on purpose: a rule extracted from one bad
afternoon should not carry the same weight as one you chose while thinking clearly.

At the end of a run, Claude prints a scar block — or hands you an updated copy of this
file. Paste it below, newest first, and save the skill. **Copy this file to `SCARS.prev.md`
first — or just keep the old text somewhere for a day.** A scar drawn from one confusing
afternoon can have the wrong cause or too wide a rule; without a copy that is permanent,
with one it takes ten seconds to undo.

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

When **three or more scars land in the same territory** — three about numbers, three about
client emails, three about one system — that area is not an occasional hazard. It is a
recurring kind of work, and it has earned its own skill.

Sibling folder, own `SKILL.md`, rules rewritten as procedure rather than warnings, each
keeping a line naming the scar it came from — and **delete those entries from here.** Full
steps in `SKILL.md` Step 7.

This file is supposed to stay short. Not because things stop going wrong, but because
things keep graduating out of it.
