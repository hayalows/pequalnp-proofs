"""SAT search: monotone (AND/OR, fan-in 2) circuit of size S computing the
Petersen edge function.

Monotone g computes f iff g=1 on every edge-assignment and g=0 on every
maximal independent set.
"""
import sys
from pysat.formula import IDPool
from pysat.solvers import Solver

sys.path.insert(0, r"C:\Users\USER\pnp\research\651")
from petersen import EDGES, maximal_independent_sets, N

MIS = maximal_independent_sets()
EDGE_SETS = [frozenset(e) for e in EDGES]


def assignment_bits(S):
    return [1 if i in S else 0 for i in range(N)]


ASSIGN = [(assignment_bits(s), 1) for s in EDGE_SETS] + \
         [(assignment_bits(s), 0) for s in MIS]


def solve(S, solver_name="cadical195", time_budget=None):
    v = IDPool()
    def new():
        return v.id(("x", v.top + 1))

    # one-hot selectors and op vars
    sel1 = [[new() for _ in range(10 + i)] for i in range(S)]
    sel2 = [[new() for _ in range(10 + i)] for i in range(S)]
    op = [new() for _ in range(S)]  # True = OR, False = AND
    # V[k][a]: value of wire k under assignment a (k in 0..10+S-1)
    V = [[None] * len(ASSIGN) for _ in range(10 + S)]
    for k in range(N):
        for a, (bits, _) in enumerate(ASSIGN):
            V[k][a] = v.id(("const", k, a)) if bits[k] else None
    cl = []
    # constants: V[k][a] fixed.  represent True by a var forced true, False by None
    for k in range(N):
        for a, (bits, _) in enumerate(ASSIGN):
            if bits[k]:
                cl.append([V[k][a]])

    def add_clause(c):
        cl.append(c)

    def and_gate(a_, b_, out):
        # out <-> a_ & b_ ; None means constant false
        if a_ is None or b_ is None:
            add_clause([-out])
            return
        add_clause([-out, a_]); add_clause([-out, b_]); add_clause([out, -a_, -b_])

    def or_gate(a_, b_, out):
        if a_ is None and b_ is None:
            add_clause([-out]); return
        if a_ is None:
            # out <-> b_
            add_clause([-out, b_]); add_clause([out, -b_]); return
        if b_ is None:
            add_clause([-out, a_]); add_clause([out, -a_]); return
        add_clause([out, -a_]); add_clause([out, -b_]); add_clause([-out, a_, b_])

    for i in range(S):
        avail = 10 + i
        # one-hot
        add_clause(sel1[i])
        add_clause(sel2[i])
        for k1 in range(avail):
            for k2 in range(k1 + 1, avail):
                add_clause([-sel1[i][k1], -sel1[i][k2]])
                add_clause([-sel2[i][k1], -sel2[i][k2]])
        # per assignment values
        for a in range(len(ASSIGN)):
            p1 = new(); p2 = new()
            # p1 <-> OR_k sel1[i][k] & V[k][a]
            # build disjunction of (sel1 & V)
            terms1 = []
            for k in range(avail):
                t = new()
                and_gate(sel1[i][k], V[k][a], t)
                terms1.append(t)
            # p1 <-> OR terms1  (terms1 nonempty)
            or_chain(terms1, p1, add_clause)
            terms2 = []
            for k in range(avail):
                t = new()
                and_gate(sel2[i][k], V[k][a], t)
                terms2.append(t)
            or_chain(terms2, p2, add_clause)
            val = new()
            # val <-> op ? (p1|p2) : (p1&p2)
            o = op[i]
            # t_or = p1|p2 ; t_and = p1&p2 ; val = (o&t_or)|(~o&t_and)
            t_or = new(); t_and = new()
            or_gate(p1, p2, t_or)
            and_gate(p1, p2, t_and)
            # val <-> (o & t_or) | (~o & t_and)
            u1 = new(); and_gate(o, t_or, u1)
            u2 = new(); and_gate2_neg(o, t_and, u2, add_clause)
            or_gate(u1, u2, val)
            V[10 + i][a] = val
    # output constraint
    out = V[10 + S - 1]
    for a, (bits, want) in enumerate(ASSIGN):
        if want:
            add_clause([out[a]])
        else:
            add_clause([-out[a]])

    with Solver(name=solver_name, bootstrap_with=cl) as s:
        ok = s.solve()
        model = s.get_model() if ok else None
    if not ok:
        return None
    # decode
    gates = []
    for i in range(S):
        o = model[op[i] - 1] > 0
        k1 = next(k for k in range(10 + i) if model[sel1[i][k] - 1] > 0)
        k2 = next(k for k in range(10 + i) if model[sel2[i][k] - 1] > 0)
        gates.append(("or" if o else "and", k1, k2))
    return gates


def or_chain(terms, out, add_clause):
    # out <-> OR terms
    for t in terms:
        add_clause([out, -t])
    add_clause([-out] + terms)


def and_gate2_neg(o, b_, out, add_clause):
    # out <-> (~o) & b_
    add_clause([-out, -o]); add_clause([-out, b_]); add_clause([out, o, -b_]) if False else None
    add_clause([out, o, -b_]) if False else None
    # proper encoding: out -> ~o ; out -> b ; (~o & b) -> out
    add_clause([-out, -o])
    add_clause([-out, b_])
    add_clause([out, o, -b_])


if __name__ == "__main__":
    from petersen import check_circuit
    for S in [19, 18, 17, 16, 20]:
        print("=== trying size", S, flush=True)
        g = solve(S)
        if g is None:
            print("  UNSAT (no monotone circuit of size", S, ")")
            break
        else:
            okf, bad = check_circuit(g)
            print("  SAT circuit found, valid on full truth table:", okf, "gates:", g)
            if okf:
                print("  *** FOUND valid circuit of size", S, "***")
                break
