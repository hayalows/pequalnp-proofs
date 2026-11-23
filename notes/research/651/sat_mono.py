"""Clean SAT/Tseitin search for a monotone (AND/OR fan-in 2) circuit of
size S computing the Petersen edge function f.

f is monotone, so a monotone g computes f iff
  g(edge set)=1 for all 15 edges, and g(maximal independent set)=0.
Output may be any wire (matches HasCircuitSize with size <= S).
"""
import sys, itertools
sys.path.insert(0, r"C:\Users\USER\pnp\research\651")
from petersen import EDGES, maximal_independent_sets, check_circuit, N

MIS = maximal_independent_sets()

def assignments():
    A = []
    for e in EDGES:
        A.append((frozenset(e), 1))
    for s in MIS:
        A.append((s, 0))
    return A

ASSIGN = assignments()

class Enc:
    def __init__(self):
        self.n = 0
        self.cl = []
    def new(self):
        self.n += 1
        return self.n
    def add(self, *c):
        self.cl.append(list(c))

def build(S):
    E = Enc()
    T = E.new(); E.add(T)  # constant true; false = -T
    A = ASSIGN
    nA = len(A)
    # input value literals V[k][a]
    V = [[None]*nA for _ in range(N + S)]
    for k in range(N):
        for a,(s,w) in enumerate(A):
            V[k][a] = T if k in s else -T
    # selectors
    s1 = [[E.new() for _ in range(N+i)] for i in range(S)]
    s2 = [[E.new() for _ in range(N+i)] for i in range(S)]
    op = [E.new() for _ in range(S)]  # True=OR, False=AND
    for i in range(S):
        avail = N + i
        E.add(*s1[i]); E.add(*s2[i])
        for a_ in range(avail):
            for b_ in range(a_+1, avail):
                E.add(-s1[i][a_], -s1[i][b_])
                E.add(-s2[i][a_], -s2[i][b_])
    def land(x,y):
        if x == T: return y
        if x == -T: return -T
        if y == T: return x
        if y == -T: return -T
        z = E.new(); E.add(-z,x); E.add(-z,y); E.add(z,-x,-y); return z
    def lor(x,y):
        if x == T or y == T: return T
        if x == -T: return y
        if y == -T: return x
        z = E.new(); E.add(z,-x); E.add(z,-y); E.add(-z,x,y); return z
    def bor(terms):
        r = -T
        for t in terms:
            r = lor(r,t)
        return r
    def band(terms):
        r = T
        for t in terms:
            r = land(r,t)
        return r
    for i in range(S):
        avail = N + i
        for a in range(nA):
            in1 = bor([land(s1[i][k], V[k][a]) for k in range(avail)])
            in2 = bor([land(s2[i][k], V[k][a]) for k in range(avail)])
            v = lor(land(op[i], lor(in1,in2)), land(-op[i], land(in1,in2)))
            V[N+i][a] = v
    # output selector
    osel = [E.new() for _ in range(N+S)]
    E.add(*osel)
    for a_ in range(N+S):
        for b_ in range(a_+1, N+S):
            E.add(-osel[a_], -osel[b_])
    for a,(s,w) in enumerate(A):
        out = bor([land(osel[k], V[k][a]) for k in range(N+S)])
        if w: E.add(out)
        else: E.add(-out)
    return E, V, s1, s2, op, osel

def decode(model, E, S, s1, s2, op, osel):
    def val(v): return model[v-1] > 0
    gates = []
    for i in range(S):
        o = val(op[i])
        k1 = next(k for k in range(N+i) if val(s1[i][k]))
        k2 = next(k for k in range(N+i) if val(s2[i][k]))
        gates.append(("or" if o else "and", k1, k2))
    outw = next(k for k in range(N+S) if val(osel[k]))
    return gates, outw

def eval_out(gates, outw, x):
    wires = [bool(x[i]) for i in range(N)]
    for (op,a,b) in gates:
        wires.append((wires[a] and wires[b]) if op=='and' else (wires[a] or wires[b]))
    return wires[outw] if outw < len(wires) else False

def fully_valid(gates, outw):
    for xx in itertools.product([0,1], repeat=N):
        if eval_out(gates,outw,xx) != (1 if any(xx[a] and xx[b] for a,b in EDGES) else 0):
            return False, xx
    return True, None

def solve(S, name="cadical195"):
    from pysat.solvers import Solver
    E,V,s1,s2,op,osel = build(S)
    with Solver(name=name, bootstrap_with=E.cl) as sv:
        ok = sv.solve()
        model = sv.get_model() if ok else None
    if not ok: return None
    gates,outw = decode(model,E,S,s1,s2,op,osel)
    return gates,outw

if __name__ == "__main__":
    for S in [19]:
        print("=== monotone size",S, flush=True)
        r = solve(S)
        if r is None:
            print("  UNSAT: no monotone circuit with <= %d gates"%S, flush=True)
        else:
            gates,outw = r
            gv,bad = fully_valid(gates,outw)
            print("  SAT. fully valid:", gv, "outwire", outw)
            print("  gates:", gates)
            if not gv: print("  counterexample:", bad)
