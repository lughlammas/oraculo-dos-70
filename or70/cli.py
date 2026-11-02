import argparse, sys
from .domino import Engine
from .drawstate import DrawState
from .audit import ficha

def main(argv=None):
    ap = argparse.ArgumentParser(prog="or70"); sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw"); d.add_argument("--seed", type=int, required=True); d.add_argument("-k", type=int, default=7)
    r = sub.add_parser("reveal"); r.add_argument("--file", required=True); r.add_argument("--ficha", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "draw":
        print(DrawState.new(Engine().draw(a.seed, a.k), seed=a.seed).to_json())
    else:
        ds = DrawState.from_json(open(a.file, encoding="utf-8").read())
        ds.reveal(); ds.attach_narrative("[D] narrativa placeholder — camada interpretativa ainda não implementada")
        print(ficha(ds) if a.ficha else ds.to_json())

if __name__ == "__main__": sys.exit(main())
