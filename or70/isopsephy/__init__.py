"""Isopséfia grega (valores milesianos clássicos) + classificação de evidência A/B/C/D."""
import unicodedata

LEVELS = ("A", "B", "C", "D")
_V = dict(zip("αβγδεϛζηθικλμνξοπϟρστυφχψωϡ",
    [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900]))
_V.update({"ς": 200, "ϝ": 6, "ϙ": 90, "ͳ": 900})

def isopsephy(word: str) -> int:
    """Remove diacríticos (inclui iota subscrito) via NFD; σ/ς = 200. Erro em letra não grega."""
    total = 0
    for ch in unicodedata.normalize("NFD", word.lower()):
        if unicodedata.combining(ch) or ch.isspace(): continue
        if ch not in _V: raise ValueError(f"caractere não grego: {ch!r}")
        total += _V[ch]
    return total

def classify(entry: dict) -> str:
    """Regras do spec. D é o padrão (EDITORIAL_AUTHORIAL)."""
    idx = entry.get("index")
    if entry.get("greek_term") and entry.get("ref_lexical") and isopsephy(entry["greek_term"]) == idx: return "A"
    if entry.get("inflected_form") and entry.get("grammatical_type") and isopsephy(entry["inflected_form"]) == idx: return "B"
    if entry.get("historical_source"): return "C"
    return "D"

def check_level(level: str) -> str:
    if level not in LEVELS: raise ValueError(f"evidência inválida: {level!r}")
    return level

def rigor(levels: list[str]) -> dict:
    n = len(levels) or 1
    c = {l: levels.count(l) for l in LEVELS}
    return {"counts": c, "rigor_pct": round(100 * (c["A"] + c["B"]) / n, 2),
            "authorial_pct": round(100 * c["D"] / n, 2)}
