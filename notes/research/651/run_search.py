import sys, itertools, time
sys.path.insert(0, r"C:\Users\USER\pnp\research\651")
from petersen import EDGES, maximal_independent_sets, N
from sat_mono import build, decode, eval_out, fully_valid

from pysat.solvers import Solver

def run(S, name="cadical195", budget=120):
    t0=time.time()
    E,V,s1,s2,op,osel = build(S)
    print(f"  built: {E.n} vars, {len(E.cl)} clauses  ({time.time()-t0:.1f}s)", flush=True)
    with Solver(name=name, bootstrap_with=E.cl) as sv:
        sv.set_phases([])
        ok = None
        # time-limited solve via interrupted callback not simple; use solve_limited style
        sv.conf_budget(budget*1000000) if hasattr(sv,'conf_budget') else None
        try:
            ok = sv.solve()
        except Exception as e:
            print("  solve err", e)
        model = sv.get_model() if ok else None
    dt=time.time()-t0
    if not ok:
        print(f"  UNSAT/limit after {dt:.1f}s", flush=True)
        return None
    gates,outw = decode(model,E,S,s1,s2,op,osel)
    gv,bad = fully_valid(gates,outw)
    print(f"  SAT after {dt:.1f}s  fully_valid={gv} outwire={outw}", flush=True)
    print("  gates:", gates, flush=True)
    if not gv: print("  BAD:", bad, flush=True)
    return gates if gv else None

if __name__ == "__main__":
    for S in [int(x) for x in sys.argv[1:]] or [20,19]:
        print("=== size", S, flush=True)
        run(S)
