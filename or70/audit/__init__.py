"""Relatório em 3 seções: Dados Operacionais / Correspondências e Evidências / Leitura Sugerida."""
def ficha(d: dict) -> str:
    dt, c, v = d["data"], d["data"]["calculated"], d["data"]["validation"]
    out = ["## Dados Operacionais", f"draw_id {d['draw_id']} v{d['version']}  hash {d['audit']['hash']}",
        "geração: " + "; ".join(f"{k}={x}" for k, x in dt["generation"].items()),
        " ".join(f"{p['top']}/{p['bottom']}" for p in dt["pieces"]) + f"  ({v['modality']})",
        f"U={c['upper_line_sum']} L={c['lower_line_sum']} T={c['total_sum']} (recalculado)",
        "validação: " + ("OK" if v["valid"] else "; ".join(v["errors"])) + "".join(f" | aviso: {w}" for w in v["warnings"])]
    if dt["input_discrepancies"]: out.append(f"divergências de entrada (ignoradas): {dt['input_discrepancies']}")
    if d.get("parent"): out.append(f"revisão de {d['parent']['draw_id']}: {d['parent']['reason']}")
    cr = d["correspondences"]
    out += ["## Correspondências e Evidências", f"matriz {cr['matrix_version']} | política {cr['isopsephy_policy']['id']}"]
    for r in cr["rows"]:
        out.append(f"[{r['evidence']}] {r['slot']}={r['index']}: {r.get('label','')} doc={r['documentary']} {r['pending']}" if r["evidence"]
                   else f"[—] {r['slot']}={r['index']}: {r['status']}")
    out += ["## Leitura Sugerida (autoral, não altera dados nem evidência)", d["reading"]["text"] if d["reading"] else "(sem leitura)"]
    return "\n".join(out)
