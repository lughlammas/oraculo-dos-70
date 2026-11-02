import argparse, json, sys
from .drawstate import DrawState
from .audit import ficha

PLACEHOLDER = "[D] leitura placeholder — camada interpretativa ainda não implementada"

def main(argv=None):
    ap = argparse.ArgumentParser(prog="or70"); sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw"); d.add_argument("--seed", type=int); d.add_argument("-k", type=int, default=7)
    d.add_argument("--pieces", help='físico: "3/4,4/0,..." (topo/base, em ordem)')
    r = sub.add_parser("reveal"); r.add_argument("--file", required=True); r.add_argument("--ficha", action="store_true")
    v = sub.add_parser("verify"); v.add_argument("--file", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "draw":
        if a.pieces: ds = DrawState.physical([tuple(map(int, x.split("/"))) for x in a.pieces.split(",")])
        elif a.seed is not None: ds = DrawState.simulated(a.seed, a.k)
        else: ap.error("--seed ou --pieces")
        print(ds.to_json()); return 0
    ds = DrawState.from_json(open(a.file, encoding="utf-8").read())
    if a.cmd == "reveal":
        ds.set_reading(PLACEHOLDER); ds.reveal()
        print(ficha(ds.get()) if a.ficha else ds.to_json()); return 0
    ok = ds.verify(); sim = ds.get()["data"]["generation"]["mode"] == "simulado"
    print(json.dumps({"hash_ok": ok, "reproduz": ds.verify_simulation() if sim else "n/a (físico)"}))
    return 0 if ok else 1

if __name__ == "__main__": sys.exit(main())
