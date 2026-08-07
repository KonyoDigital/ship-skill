# Writing a gate that measures the rule, not the wording

**This file is a carved skill.** Four scars landed in one territory, which is the
trigger the skill names, so the rules moved out of scattered comments and into their own
place. Each one below records the scar that produced it, because a rule whose origin is
lost gets deleted by the first person tidying up — and then it happens again.

Every one of these came from `verify_package.py` **failing correct work**. That is the
failure mode that matters here: a gate that cries wolf gets switched off, and then it
protects nothing. A missed finding costs one bug; a false alarm costs the gate.

---

## 1. Check the PROPERTY, never the phrasing

```python
want("PASSED, CEILING or STALLED" in md, ...)      # ✗
want(all(w in seal for w in ("PASSED","CEILING","STALLED")), ...)   # ✓
```

> **Scar.** A rewrite said `PASSED / CEILING / STALLED` — same requirement, different
> punctuation. The gate failed correct work and I nearly "fixed" the document to satisfy
> the checker.

## 2. Normalise the markup before matching prose

Hard-wrapped markdown breaks any phrase longer than a few words, and blockquotes add
`> ` at each continuation.

```python
flat = " ".join(re.sub(r"^\s*>\s?", "", md, flags=re.M).split())
```

> **Scars, two of them.** `"not independently verified"` split across a line break.
> `"It was already like that"` sat inside a blockquote and flattened to
> `"It was > already like that"`. Both present, both correct, both failed.

## 3. A mutation that no-ops certifies nothing

A red proof must target the property. If the mutation string has since been reworded,
the mutation silently does nothing, the gate stays green, and you have a check that
**certifies itself**.

```python
md.replace("SOLO or MULTI (Step 4b)", "—")     # ✗ no-op after any rewording
md.replace("SOLO","x").replace("MULTI","y")    # ✓ hits the property
```

> **Scar.** `--self-test` caught this one on its own and reported "the gate stayed
> green — it is not measuring this." A self-test that can report its own blind spot is
> worth more than one that only passes.

## 4. Ignore quoted mentions

A document explaining why a phrasing is wrong **contains that phrasing**. `"bad phrase"
not in md` then fails on the fix that removed it — the same shape as grepping for a bug
and matching the comment describing it.

```python
unquoted = re.sub(r'"[^"]*"', '""', md)
```

> **Scar.** The check for `waiting to be filled in` failed on the text that replaced it,
> because the replacement quotes the old phrasing to explain the change.

## 5. Assert your own preprocessing loses nothing

Any stripper, parser or normaliser can desynchronise, and a broken one makes every
verdict downstream meaningless. Give it an invariant and check that **first**.

> **Scar.** `ghost_scan`'s stripper hit `esc()`'s `/[&<>"']/g`, read the `"` as a string
> opener, and silently ate **365 of 1,112 lines** — then reported three *declared* names
> as undeclared. Three "bugs in the page" were one bug in the scanner.

## 6. Count promises structurally, not by reading

"the last two" above three bullets, "exactly four reasons" above a three-row table —
these read as correct to every human reviewer and to two independent AI ones.

```python
for m in re.finditer(r"[Tt]he last (two|three|four)[^.\n]*:", md): ...
for m in re.finditer(r"exactly (two|three|four) reasons", md): ...
```

> **Scars, two.** "The last two make it a defence" sat above three bullets — a
> compression casualty. Then "exactly three reasons" sat above four rows the moment
> `UNFIXABLE HERE` was added. Adding an item and not updating its count is not a typo,
> it is a *class*.

## 7. When a check keeps passing on stale data, change the SOURCE

A fresher cache-buster is not the fix. Find a source that cannot be stale.

```bash
curl .../main/FILE            # ✗ CDN-cached; returns yesterday's file
curl api.github.com/.../main  # ✗ propagation window; returns the previous SHA
git ls-remote <url> main      # ✓ git protocol — the ref the push just wrote
```

> **Scars, two, and the second was the fix for the first.** `sync.sh` fetched
> `.../main/SKILL.md`, compared the local copy against **what it had just fetched**,
> matched, and reported OK — certifying stale content. Replaced with "resolve the SHA
> from the API, fetch that immutable path", which is correct reasoning and still wrong:
> that API has a propagation window and returns the previous SHA for a while after a
> push. It then verified faithfully against a stale-but-real commit and reported OK
> again. Both a repo and a live install sat a commit behind while the guard said in sync.

**The general form: verifying "I match what I fetched" is not verifying "I match
upstream."** Whenever a check compares against something it retrieved itself, ask what
happens when the retrieval is wrong.

---

## The rule under all seven

**When a gate fails, ask whether the subject is wrong or the instrument is.** Five of
these six were the instrument. Fixing the document to satisfy a broken checker is the
worst available outcome: you damage correct work *and* keep the broken gate.
