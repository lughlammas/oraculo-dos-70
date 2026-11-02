"""Ficha de Auditoria: Dados Operacionais + Correspondências e Evidências (nível ao lado de cada termo)."""
from ..domino import Engine, validate
from ..isopsephy import rigor

def ficha(ds) -> str:
    c, ps = ds["calculated"], ds["pieces"]
    errs = validate(Engine.manual([(p["top"], p["bottom"]) for p in ps]))
    r = rigor([t["evidence"] for t in ds["terms"]])
    out = ["## Dados Operacionais", f"draw_id {ds['draw_id']}  seed {ds['seed']}  hash {ds['audit']['hash']}",
           " ".join(p["face"] for p in ps), f"U={c['upper_line_sum']} L={c['lower_line_sum']} T={c['total_sum']}",
           "validação: " + ("OK" if not errs else "; ".join(errs)),
           "## Correspondências e Evidências"]
    out += [f"[{t['evidence']}] {t['id']}: {t['label']}" for t in ds["terms"]]
    out.append(f"rigor {r['rigor_pct']}% | camada autoral declarada {r['authorial_pct']}%")
    return "\n".join(out)
