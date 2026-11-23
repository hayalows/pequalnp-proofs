"""Decisive probe for L-pcx-093/094.

For each formula and each width k, compute the closure S_k of the clause set
under resolution restricted to clauses of card <= k.  Then:
  least width <= k  iff  empty clause in S_k.
Also, if the empty clause is reached, extract a concrete resolution derivation
(a list of clauses, atomic first) by BFS with parents, so a Lean witness can be
written down.
Prints counts so we can size the Lean formalization.
"""
import sys
from collections import deque
sys.path.insert(0, r"C:\Users\USER\pnp\research\pcx94")
from probe import build_F1, build_F21, is_resolvent


def closure_with_parents(F, k):
    """S = all derivable clauses of card <= k. parents[R] = (C,D,pivot) for a
    one-step derivation, or None for axioms.  Returns (S, parents, found_empty)."""
    S = set()
    parents = {}
    for c in F:
        if len(c) <= k:
            S.add(c)
            parents.setdefault(c, None)
    empty = frozenset()
    if empty in S:
        return S, parents, True
    changed = True
    while changed:
        changed = False
        lst = list(S)
        for i in range(len(lst)):
            for j in range(i, len(lst)):
                for R in is_resolvent(lst[i], lst[j]):
                    if len(R) <= k and R not in S:
                        S.add(R)
                        parents[R] = (lst[i], lst[j])
                        changed = True
                        if len(R) == 0:
                            return S, parents, True
    return S, parents, False


def derivation_of(empty, parents):
    """Return a topological (children-before-parents) list ending source-first,
    i.e. a valid IsDerivation order (newest first is [empty, ...axioms])."""
    order = []
    seen = set()

    def visit(c):
        if c in seen:
            return
        seen.add(c)
        p = parents.get(c)
        if p is not None:
            visit(p[0]); visit(p[1])
        order.append(c)

    visit(empty)
    # IsDerivation is newest-first: axioms last.  order is axioms-first.
    return list(reversed(order))


def report(name, F, ks):
    print("=" * 70)
    print(name, "axioms", len(F), "width dist",
          {w: sum(1 for c in F if len(c) == w) for w in sorted(set(len(c) for c in F))})
    for k in ks:
        S, par, e = closure_with_parents(F, k)
        print(f"  width<={k}: closure size {len(S)}  empty={e}")
        if e:
            d = derivation_of(frozenset(), par)
            widths = sorted(set(len(c) for c in d))
            print(f"     refutation length {len(d)}  clause widths present {widths}")
            print(f"     first clause {sorted(d[0])}  ... last clause {sorted(d[-1])}")
    sys.stdout.flush()


if __name__ == "__main__":
    report("F1 (5-cycle, 3 labels)", build_F1(), [2, 3])
    report("F21 (two triangles, 4 labels)", build_F21(), [3, 4])
