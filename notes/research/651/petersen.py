"""Petersen graph edge function: data, evaluator, independent sets."""
from itertools import combinations

# Vertices 0..9. Edges exactly as in the posted statement L-meta-651.
EDGES = [(0,1),(1,2),(2,3),(3,4),(4,0),
         (0,5),(1,6),(2,7),(3,8),(4,9),
         (5,7),(7,9),(9,6),(6,8),(8,5)]
EDGES = [tuple(sorted(e)) for e in EDGES]
ESET = set(EDGES)
N = 10


def f_from_set(S):
    """f(x)=1 iff the true-input set S contains both ends of some edge."""
    for a, b in EDGES:
        if a in S and b in S:
            return True
    return False


def f(x):
    """x: tuple/list of 10 bools."""
    S = {i for i in range(N) if x[i]}
    return f_from_set(S)


def independent(S):
    return not f_from_set(S)


def maximal_independent_sets():
    mis = []
    for k in range(N + 1):
        for c in combinations(range(N), k):
            cs = set(c)
            if independent(cs):
                # maximal if adding any other vertex breaks it
                if all(any(True for _ in [0]) for _ in []) or True:
                    if all(not independent(cs | {v}) for v in range(N) if v not in cs):
                        mis.append(frozenset(cs))
    return mis


def eval_gates(gates, x):
    """gates: list of (op, a, b) with op in 'and','or'; wire w<10 is input,
    wire 10+g is gate g. Returns output value of last gate."""
    wires = [bool(x[i]) for i in range(N)]
    for (op, a, b) in gates:
        va = wires[a]
        vb = wires[b]
        wires.append(va and vb if op == 'and' else va or vb)
    return wires[-1]


def check_circuit(gates):
    for x in range(1 << N):
        xx = tuple((x >> i) & 1 for i in range(N))
        if eval_gates(gates, xx) != f(xx):
            return False, xx
    return True, None


if __name__ == "__main__":
    mis = maximal_independent_sets()
    print("num maximal independent sets:", len(mis))
    for m in mis:
        print("  ", sorted(m))
    print("alpha (max size):", max(len(m) for m in mis))
    # sanity: brute force tau
    for k in range(N + 1):
        found = False
        for c in combinations(range(N), k):
            cs = set(c)
            if all(a in cs or b in cs for a, b in EDGES):
                found = True
                print("vertex cover number tau =", k, "example", sorted(cs))
                break
        if found:
            break
