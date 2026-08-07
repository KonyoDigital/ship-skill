# ship-skill

**A skill that makes an AI finish work properly — and get better at *your* work over time.**

Most work fails in one of three ways: it looked right and wasn't, it fixed one instance
of a problem that existed in five places, or nobody could tell afterwards whether it
actually worked. This makes each of those hard.

Every run ends in **one word**: `SHIP`, `DRAFT` or `BLOCKED`. It fails closed — anything
short of proven-good is never a SHIP with caveats attached.

### ⬇ Install

**[Download `ship-skill.skill`](https://github.com/KonyoDigital/ship-skill/raw/main/ship-skill.skill)**
— or [`.zip`](https://github.com/KonyoDigital/ship-skill/raw/main/ship-skill.zip), identical content.

In **Claude Desktop**:
1. **Settings → Capabilities →** enable *"Code execution and file creation"* (skills won't appear without it)
2. **Customize → Skills → + → Create skill → Upload a skill**
3. Pick the file, toggle it on

Free, Pro, Max, Team and Enterprise. Works in Claude Code too — drop `skill/` into
`~/.claude/skills/ship-skill/`.

**It is two markdown files. No scripts, no dependencies, nothing that runs.** Read them
before you install — that's a reasonable thing to want from anything you load into your
assistant, and it takes two minutes.

---

## What it actually does

| Stage | |
|---|---|
| **Understand** | Restate the goal, declare scope. Scope can be widened later but **never narrowed** — otherwise "out of scope" becomes a way to launder a known defect into a SHIP. |
| **Build in rounds** | One coherent theme per round, not a mega-dump. |
| **Prove each round** | Evidence, not assertion. Including: **the tests are a suspect too**, not just the instrument. |
| **Adversarial back-pass** | Four separate lenses, then honestly: *what's the strongest case this is wrong?* |
| **Fix and re-prove** | Stops for a stated reason — `PASSED`, `CEILING` or `STALLED`. |
| **Seal** | One verdict, what changed, how it was proven, **what was NOT checked**, how to undo it. |
| **Scar** | Whatever went wrong becomes a rule the next run loads. |

### The three ideas worth stealing even if you never install it

**1. Distrust a check that passes.** A green suite is not proof the code is right — it
can be *evidence pointing the wrong way* if the tests are wrong in the same direction as
the bug. In a live trial of this skill, a fresh agent was handed a pricing module with a
documented 30% discount cap that was never applied, a green 4/4 suite, and two tests
asserting the uncapped behaviour as correct. It caught the bug, corrected both lying
tests, and — unprompted — restored the old code to prove its new tests could actually
fail. Its own note afterwards: *"that one paragraph pre-loaded the correct suspicion
before I ran anything."*

**2. `CEILING` is not `STALLED`.** Both mean "not fixed" and they call for opposite
responses. CEILING — the failure kept changing — means give it another pass. STALLED —
the same failure twice running — means **stop and change the approach, don't raise the
limit.** Collapsing them into "didn't work" is how an hour disappears into the version
that cannot work.

**3. A rule without evidence is a superstition.** Every scar records what in *that run*
proved it. Skip that and a workflow slowly fills with confident restrictions nobody can
trace, refusing things for reasons that were never true.

---

## The part that compounds

`SCARS.md` ships **empty on purpose.** It has two layers:

- **FOUNDING RULES** — yours, hand-written, deliberate. Nothing learned can overwrite
  them. There are five *candidate* drafts in the file as starting shapes; they carry **no
  authority** until you rewrite the ones you believe in your own words. A rule carrying
  your name has to be one you chose.
- **LEARNED SCARS** — appended from runs that went wrong. Deliberately lower authority.

When a run goes wrong, Claude prints a six-line scar block ready to paste. When **three
scars land in the same territory**, that territory has earned its own skill: carve a
sibling folder, move the rules in as a procedure, delete them from `SCARS.md`.

That's the loop: **work produces scars → scars accumulate into a territory → the
territory becomes a skill → and the workflow is now better at *your* job, not at jobs in
general.** Nobody can hand you that version. It can only be grown.

**One honest limitation:** Claude cannot reliably write to its own skill folder, and
reading a file back proves the *write*, never that the workspace survives. So it always
prints the block, always offers the file, and always says durability is unverified.
Pasting it is your ten seconds.

---

## SOLO and MULTI

The back-pass names its own weakness in the body rather than a footnote: **a model
reviewing its own work has correlated blind spots.** You can't fix that by trying harder
in the same breath — you fix it by changing what the reviewer knows.

| Rung | What it removes |
|---|---|
| **1.** A different model family | Contamination, *and* blind spots sit elsewhere. Strongest. |
| **2.** A fresh subagent | Most contamination — but you write its prompt, so the reduction is by discipline, not mechanism. |
| **3.** A new conversation, pasted by hand | Same independence, more effort. The chat-only fallback. |
| **4.** Same conversation | Nothing. **This is SOLO — call it SOLO.** |

The seal has to say which. *"SOLO" is an honest answer; an unearned "MULTI" is not.*

---

## Verifying the package

`verify_package.py` gates the download on **27 checks** — the shape Desktop rejects, the
1024-char description limit, and that the seal still demands the mode, the stop reason and
the scar evidence. `--self-test` mutates the package **16 ways and proves every check goes
red**, because a gate nobody has seen fail is not known to be measuring anything.

```bash
python3 verify_package.py            # check the shipped package
python3 verify_package.py --self-test  # prove the checks can fail
```

---

## Want the machinery, not just the judgement?

[**agent-army**](https://github.com/KonyoDigital/agent-army) is the same shipping
standard run as a **fleet** in Claude Code: one owner per file, a lead gating every
merge, an adversarial skeptic panel, and a render gate that drives the real UI at two
viewports and looks at the pictures. Same laws, many agents, a terminal.

This skill is the judgement. That is the machine.

---

## Credits

Three rules in Step 5 came from the **loop-library** in
[alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) (MIT):
take the ceiling from the user rather than inventing one, don't manufacture a loop when
no new feedback can change the next action, and keep an acceptance gate you did not tune
against. The last is the sharpest — a check you optimised against measures how hard you
tuned, and it is invisible from the inside because everything is green.

MIT. Built with [Claude Code](https://claude.com/claude-code).
