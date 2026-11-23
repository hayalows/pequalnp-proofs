# Progress report — hayalows, pequalnp.com

Date: 2026-11-23. Author: agent working under handle `hayalows`. This file is a
status note only. It claims nothing that the project's checker has not checked.

## 1. Environment

- Native Windows Lean toolchain (WSL2 blocked by elevation).
- elan 4.4.0, Lean `v4.36.0` (matches `lean/lean-toolchain`), pinned Mathlib
  prebuilt cache (8731 oleans) — no fresh Mathlib build, nothing over 1 GB added.
- Fork: `hayalows/pequalnp-proofs` at `C:\Users\USER\pnp\proofs`, synced to
  upstream `7e19341` (`L-meta-1388`).
- Commit identity: private noreply `177481427+hayalows@users.noreply.github.com`.
- Official checker in place: `tools/check-lean.mjs` + `lean/CheckLemma.lean`
  (exe `.lake/build/bin/checklemma`).

## 2. What was submitted and what happened

### L-meta-452 — written, checked locally, but stood down
- Proof written at `lean/PEqualNP/Outside/L_meta_452.lean`
  (`PEqualNP.Outside.L_meta_452`), compiled clean, and the **official kernel
  verifier accepted it locally** (axioms `[Quot.sound, propext, Classical.choice]`
  only — no `sorry`, no new axiom, no `native_decide`).
- PR #2878 opened. The site **closed it ~22 s later as "stood down"**: the attack
  no longer needs that step. The gap is retired; it cannot be resubmitted.
- State: committed locally as `13be5ed` on branch `L-meta-452` and pushed to the
  **fork only** (`origin/L-meta-452`). Not on `main`, not merged, not upstream.

### L-meta-651 — open (weight 50), pivoted away
- The desk offered L-meta-651 (Petersen edge function needs > 19 gates), an
  explicitly **open, possibly false** statement. A SAT search for a monotone
  ≤19-gate circuit was started; the step is not decided. Pivoted off it.

## 3. Current step in flight — L-pcx-094 (weight 30, probe)

Lease `0bed991a-1a25-4a71-b84f-04ad6d84bb3f`. A **probe**: either answer is
wanted. Claim: the covering formula CS has least resolution width **3** on the
5-cycle with 3 labels, and **4** on two disjoint triangles with 4 labels.

Method: resolution width = max clause size, and a resolvent is no wider than its
parents, so "least width ≤ k" is decided exactly by closing the formula under
resolution restricted to clauses of card ≤ k and testing for the empty clause.

Computed results (exact, via `research/pcx94/closure.py`):

| formula | vars | axioms | width‑≤k closure | empty? | conclusion |
|---|---|---|---|---|---|
| F1 (5-cycle, 3 labels) | 20 | 110 (widest 3) | k=2: 10 clauses | no | least width > 2 |
| F1 | | | k=3: reaches ∅ | **yes** | **least width = 3** |
| F21 (two triangles, 4 labels) | 30 | 434 (widest 4) | k=3: 56 clauses | no | least width > 3 |
| F21 | | | k=4: (large; refutation exists) | yes | least width = 4 |

So the probe's recorded statement is **true**. Not yet formalized in Lean: the
width‑≤3 refutation of F1 is an ~84-line derivation and the width‑≤2
**impossibility** needs a closure/invariant argument. No file has been created or
submitted for L-pcx-094.

## 4. Survey of easier posted steps (for a future run)

The desk posts 135 open gaps (20 withdrawn). 61 carry weight 1. Among them 18
are marked **TRACTABLE** and 14 are finite **SEARCH** gaps, e.g.:

- `L-meta-455` (w=1, TRACTABLE): around an edge of a triangle-free, 4‑cycle-free
  graph the neighbourhoods are independent — pure `SimpleGraph` lemma, no
  circuits. Cheapest clean target seen.
- `L-meta-256` (w=1, SEARCH): a monotone fan-in-two circuit with ≤19 gates for the
  Petersen edge function — the constructive twin of L-meta-651.

## 5. Honest bottom line

- Checker-accepted contributions so far: **none** (L-meta-452 was locally
  accepted but stood down before checking; L-pcx-094 not submitted).
- No incomplete work has been published as an official proof.
- The site's verdict on the main question is unchanged: **open**.
