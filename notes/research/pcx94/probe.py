"""L-pcx-094 probe: build the two CNFs (F1: 5-cycle, 3 labels; F21: two
triangles, 4 labels), and decide satisfiability and *least resolution width*.

Resolution width = max Finset.card over the refutation's clauses.  Resolvents
never grow: |R| <= max(|C|,|D|).  So a width-<=k refutation exists iff closing
F under resolution restricted to width <=k produces the empty clause
(any width-<=k derivation uses only width-<=k clauses, and every resolvent it
needs is present in the closure).  This is exact.
"""
from itertools import combinations, product

# ---- variable encodings -------------------------------------------------
# F1: V = (Fin5 x Fin3) + Fin5.  inl(v,t) = v*3+t (0..14); inr(e) = 15+e.
def f1_var_inl(v, t): return v * 3 + t
def f1_var_inr(e): return 15 + e

# F21: V = (Fin6 x Fin4) + Fin6. inl(v,t) = v*4+t (0..23); inr(e)=24+e.
def f21_var_inl(v, t): return v * 4 + t
def f21_var_inr(e): return 24 + e


def lit(var, sign):  # sign True=positive
    return (var, sign)


def build_F1():
    C = []
    # clause1: each vertex has a colour: {(inl(v,t),true) : t}
    for v in range(5):
        C.append(frozenset(lit(f1_var_inl(v, t), True) for t in range(3)))
    # clause2: non-adjacent ordered (u,v), f:Fin3->Bool
    def adj(a, b):
        return b == (a + 1) % 5 or a == (b + 1) % 5
    for u in range(5):
        for v in range(5):
            if u == v or adj(u, v):
                continue
            for f in product([False, True], repeat=3):
                cl = []
                for t in range(3):
                    w = v if f[t] else u
                    cl.append(lit(f1_var_inl(w, t), True))
                C.append(frozenset(cl))
    # clause3: edge e, colour t: {(inr e,false),(inl(e,t),false),(inl(e+1,t),false)}
    for e in range(5):
        for t in range(3):
            C.append(frozenset([
                lit(f1_var_inr(e), False),
                lit(f1_var_inl(e, t), False),
                lit(f1_var_inl((e + 1) % 5, t), False),
            ]))
    # clause4: S subset Fin5 with card 2: {(inr e,true) : e not in S, e+1 not in S}
    for S in combinations(range(5), 2):
        S = set(S)
        cl = [lit(f1_var_inr(e), True) for e in range(5)
              if e not in S and (e + 1) % 5 not in S]
        C.append(frozenset(cl))
    return C


def build_F21():
    C = []
    for v in range(6):
        C.append(frozenset(lit(f21_var_inl(v, t), True) for t in range(4)))
    edges_tri = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]
    for u in range(6):
        for v in range(6):
            same_tri = (u != v) and (u // 3 == v // 3)
            if same_tri:
                continue
            for f in product([False, True], repeat=4):
                cl = []
                for t in range(4):
                    w = v if f[t] else u
                    cl.append(lit(f21_var_inl(w, t), True))
                C.append(frozenset(cl))
    for (a, b) in edges_tri:
        for t in range(4):
            C.append(frozenset([
                lit(f21_var_inr(edges_tri.index((a, b))), False),
                lit(f21_var_inl(a, t), False),
                lit(f21_var_inl(b, t), False),
            ]))
    for S in combinations(range(6), 3):
        S = set(S)
        cl = [lit(f21_var_inr(i), True) for i, (a, b) in enumerate(edges_tri)
              if a not in S and b not in S]
        C.append(frozenset(cl))
    return C


def is_resolvent(C, D):
    """Yield resolvents of C,D on any pivot variable."""
    for (v, s) in C:
        if s:  # v positive in C; need v negative in D
            if (v, False) in D:
                R = (C - {(v, True)}) | (D - {(v, False)})
                yield R


def close_width(F, k):
    """Close clause set F under resolution, keeping clauses of card <= k.
    Return (closure, empty_reached)."""
    S = set()
    for c in F:
        if len(c) <= k:
            S.add(c)
    changed = True
    empty = frozenset() in S
    while changed:
        changed = False
        lst = list(S)
        for i in range(len(lst)):
            for j in range(i, len(lst)):
                for R in is_resolvent(lst[i], lst[j]):
                    if len(R) <= k and R not in S:
                        if len(R) == 0:
                            return S | {R}, True
                        S.add(R)
                        changed = True
        if empty:
            break
    return S, (frozenset() in S)


def by_clause_width(F):
    from collections import Counter
    return Counter(len(c) for c in F)


if __name__ == "__main__":
    F1 = build_F1()
    print("F1: clauses", len(F1), "width dist", dict(sorted(by_clause_width(F1).items())))
    S3, e3 = close_width(F1, 3)
    print("F1 width<=3 closure size", len(S3), "empty?", e3)
    S2, e2 = close_width(F1, 2)
    print("F1 width<=2 closure size", len(S2), "empty?", e2)
    print()
    F21 = build_F21()
    print("F21: clauses", len(F21), "width dist", dict(sorted(by_clause_width(F21).items())))
    S4, e4 = close_width(F21, 4)
    print("F21 width<=4 closure size", len(S4), "empty?", e4)
    S3b, e3b = close_width(F21, 3)
    print("F21 width<=3 closure size", len(S3b), "empty?", e3b)
