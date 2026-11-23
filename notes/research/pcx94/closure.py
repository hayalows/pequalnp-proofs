"""Indexed resolution closure, width-bounded, with parent tracking.
Exact: least width <= k iff empty clause in closure of clauses of card<=k.
"""
import sys
from collections import defaultdict
sys.path.insert(0, r"C:\Users\USER\pnp\research\pcx94")
from probe import build_F1, build_F21


def resolvents_pairs(C, D):
    for (v, s) in C:
        if s and (v, False) in D:
            yield (C - {(v, True)}) | (D - {(v, False)})


def closure(F, k, verbose=True):
    S = set()
    parents = {}
    idx = defaultdict(set)  # (var,sign) -> clauses of S containing that literal
    lim = 0
    for c in F:
        if len(c) <= k:
            S.add(c); parents.setdefault(c, None)
            for l in c:
                idx[l].add(c)
    if frozenset() in S:
        return S, parents, True
    frontier = list(S)
    while frontier:
        new = []
        for C in frontier:
            for (v, s) in list(C):
                if not s:
                    continue
                for D in list(idx.get((v, False), ())):
                    for R in resolvents_pairs(C, D):
                        if len(R) <= k and R not in S:
                            S.add(R); parents[R] = (C, D); new.append(R)
                            for l in R:
                                idx[l].add(R)
                            if len(R) == 0:
                                return S, parents, True
        frontier = new
        if verbose and len(S) > lim + 200000:
            lim = len(S); print("    ...closure size", len(S)); sys.stdout.flush()
    return S, parents, False


def derivation_of(empty, parents):
    order, seen = [], set()
    def visit(c):
        if c in seen: return
        seen.add(c)
        p = parents.get(c)
        if p is not None:
            visit(p[0]); visit(p[1])
        order.append(c)
    visit(empty)
    return list(reversed(order))   # axioms first


def report(name, F, ks):
    print("=" * 70)
    ws = sorted(set(len(c) for c in F))
    print(name, "axioms", len(F), "width dist", {w: sum(1 for c in F if len(c) == w) for w in ws})
    sys.stdout.flush()
    for k in ks:
        print(f"  width<={k}:")
        sys.stdout.flush()
        S, par, e = closure(F, k)
        print(f"     closure size {len(S)}  empty={e}")
        if e:
            d = derivation_of(frozenset(), par)
            print(f"     refutation length {len(d)}  widths {sorted(set(len(c) for c in d))}")
        sys.stdout.flush()


if __name__ == "__main__":
    which = sys.argv[1:] or ["F1", "F21"]
    if "F1" in which:
        report("F1 (5-cycle,3 labels)", build_F1(), [2, 3])
    if "F21" in which:
        report("F21 (two triangles,4 labels)", build_F21(), [3, 4])
