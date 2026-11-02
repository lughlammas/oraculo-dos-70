"""Contrato drawstate-v0: serialização canônica, reveal() trava e gera hash SHA-256 sem narrative."""
import hashlib, json, uuid
from datetime import datetime, timezone
from ..domino import Draw
from ..isopsephy import check_level

class LockedError(Exception): pass

# Fixture A: Liber O (fixado pelo Gui). Demais termos: placeholders [D].
LIBER_O = [("fogo", "Fogo = Leste"), ("terra", "Terra = Sul"), ("ar", "Ar = Oeste"), ("agua", "Água = Norte")]

def default_terms(draw: Draw) -> list[dict]:
    t = [{"id": f"liber_o_{k}", "label": l, "evidence": "A", "source": "Liber O (fixado pelo Gui)", "note": ""} for k, l in LIBER_O]
    for p in draw.pieces:
        t.append({"id": f"s{p.position}", "label": f"[D] arquétipo {p.sum} (placeholder)", "evidence": "D", "source": "", "note": "EDITORIAL_AUTHORIAL"})
    for k in ("U", "L", "T"):
        t.append({"id": k, "label": f"[D] arquétipo {getattr(draw, k)} (placeholder)", "evidence": "D", "source": "", "note": "EDITORIAL_AUTHORIAL"})
    return t

class DrawState:
    _FROZEN = ("pieces", "terms", "seed", "draw_id", "timestamp", "calculated", "schema")
    def __init__(self, d: dict):
        object.__setattr__(self, "_d", d)
        for t in d["terms"]: check_level(t["evidence"])
    @classmethod
    def new(cls, draw: Draw, seed=None, terms=None):
        return cls({"schema": "drawstate-v0", "draw_id": str(uuid.uuid4()), "seed": seed,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"), "revealed": False,
            "pieces": [{"id": p.id, "position": p.position, "top": p.top, "bottom": p.bottom, "value": p.sum, "face": f"{p.top}/{p.bottom}"} for p in draw.pieces],
            "calculated": {"upper_line_sum": draw.U, "lower_line_sum": draw.L, "total_sum": draw.T},
            "terms": terms if terms is not None else default_terms(draw),
            "audit": {"locked": False, "hash": None}, "narrative": None})
    def __getitem__(self, k):
        v = self._d[k]
        if self.locked and k in self._FROZEN:  # devolve cópia: mutar não afeta o estado
            return json.loads(json.dumps(v))
        return v
    def __setattr__(self, k, v): raise LockedError("use os métodos")
    @property
    def locked(self): return self._d["audit"]["locked"]
    def set(self, k, v):
        if self.locked and k != "narrative": raise LockedError(f"{k} imutável após reveal")
        if k == "terms": [check_level(t["evidence"]) for t in v]
        self._d[k] = v
    def canonical_hash(self) -> str:
        d = {k: v for k, v in self._d.items() if k not in ("narrative", "audit", "revealed")}
        return hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    def reveal(self):
        if self.locked: raise LockedError("já revelado")
        self._d["audit"] = {"locked": True, "hash": self.canonical_hash()}
        self._d["revealed"] = True
    def attach_narrative(self, text: str):
        if not self.locked: raise LockedError("narrativa só após reveal")
        self._d["narrative"] = text
    def verify(self) -> bool:
        return self.locked and self._d["audit"]["hash"] == self.canonical_hash()
    def to_json(self) -> str: return json.dumps(self._d, ensure_ascii=False, indent=2)
    @classmethod
    def from_json(cls, s: str): return cls(json.loads(s))
