"""Isopséfia grega + classificação A/B/C/D. Aritmética e documental são resultados independentes."""
import unicodedata

POLICY = {"id": "iso-policy-v1", "normalization": "NFD; marcas combinantes descartadas e listadas",
    "diacritics": "acentos, espíritos, trema ignorados", "iota_subscript": "ignorado (não soma ι)",
    "sigma": "σ e ς = 200", "numeral_signs": "ϛ/ϝ=6, ϟ/ϙ=90, ϡ/ͳ=900; keraia ʹ e ͵ = erro (não suportado)"}
LEVELS = ("A", "B", "C", "D")
MATRIX_DOMAIN = range(1, 71)
_V = dict(zip("αβγδεϛζηθικλμνξοπϟρστυφχψωϡ",
    [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900]))
_V.update({"ς": 200, "ϝ": 6, "ϙ": 90, "ͳ": 900})

def analyze(word: str) -> dict:
    total, ignored, unknown = 0, [], []
    for ch in unicodedata.normalize("NFD", word.lower()):
        if ch in _V: total += _V[ch]
        elif unicodedata.combining(ch): ignored.append(unicodedata.name(ch, hex(ord(ch))))
        else: unknown.append(ch)
    return {"sum": None if unknown else total, "ignored_marks": ignored, "unknown": unknown, "policy": POLICY["id"]}

def isopsephy(word: str) -> int:
    r = analyze(word)
    if r["unknown"]: raise ValueError(f"caracteres não reconhecidos: {r['unknown']}")
    return r["sum"]

def check_level(level: str) -> str:
    if level not in LEVELS: raise ValueError(f"evidência inválida: {level!r}")
    return level

def classify(e: dict) -> dict:
    """Nível = suporte verificado. Citação preenchida != pertinência: sem revisor identificado, fica pendente e não promove."""
    idx, pend = e.get("index"), []
    def arith(form):
        if not form: return None
        r = analyze(form); return r["sum"] == idx if r["sum"] is not None else None
    reviewed = bool(e.get("reviewed_by"))
    a_ok = arith(e.get("greek_term")); b_ok = arith(e.get("inflected_form"))
    if a_ok and e.get("ref_lexical"):
        if reviewed and e.get("meaning_pertinent"): return {"level": "A", "arithmetic": True, "documentary": "aprovado", "pending": []}
        pend.append("A candidata: revisão documental (existência/sentido) pendente")
    if b_ok and e.get("grammatical_type"):
        if reviewed and e.get("morphology_verified"): return {"level": "B", "arithmetic": True, "documentary": "aprovado", "pending": pend}
        pend.append("B candidata: análise morfológica não verificada")
    if e.get("historical_source"):
        if reviewed: return {"level": "C", "arithmetic": a_ok, "documentary": "aprovado", "pending": pend}
        pend.append("C candidata: fonte histórica não revisada")
    return {"level": "D", "arithmetic": a_ok if a_ok is not None else b_ok,
            "documentary": "pendente" if pend else "n/a", "pending": pend}

def composition(levels: list[str], total: int = 70) -> dict:
    """Composição da matriz (não é nota de qualidade)."""
    c = {l: levels.count(l) for l in LEVELS}; pct = lambda x: round(100 * x / total, 2)
    return {"counts": c, "total": total,
        "lexical_exact_AB_pct": pct(c["A"] + c["B"]), "historical_arithmological_C_pct": pct(c["C"]),
        "documentary_coverage_ABC_pct": pct(c["A"] + c["B"] + c["C"]), "authorial_D_pct": pct(c["D"]),
        "missing": total - sum(c.values())}
