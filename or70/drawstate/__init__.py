"""Contrato drawstate-v1: 3 camadas (data / correspondences / reading). reveal() fixa tudo; correção = nova versão."""
import copy, hashlib, json, uuid
from datetime import datetime, timezone
from ..domino import Draw, Engine, GEN_PROFILE, recompute, validate
from ..isopsephy import POLICY, MATRIX_DOMAIN, check_level

class LockedError(Exception): pass
NO_MATCH = "sem correspondência definida na matriz"
MATRIX_VERSION = "matrix-empty-v0"  # matriz real ainda não fornecida: nenhuma entrada

def _h(o): return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def correspondences(draw: Draw, matrix: dict | None = None) -> dict:
    matrix = matrix or {}; rows = []
    slots = [(f"s{p.position}", p.sum) for p in draw.pieces] + [("U", draw.U), ("L", draw.L), ("T", draw.T)]
    for slot, idx in slots:
        if idx not in MATRIX_DOMAIN:
            rows.append({"slot": slot, "index": idx, "status": f"fora do domínio 1..70: {NO_MATCH}", "evidence": None}); continue
        e = matrix.get(idx)
        if not e:
            rows.append({"slot": slot, "index": idx, "status": f"lacuna: {NO_MATCH}", "evidence": None}); continue
        rows.append({"slot": slot, "index": idx, "status": "mapeado", "label": e["label"], "evidence": check_level(e["evidence"]),
                     "arithmetic": e.get("arithmetic"), "documentary": e.get("documentary", "pendente"),
                     "source": e.get("source"), "pending": e.get("pending", [])})
    return {"matrix_version": MATRIX_VERSION, "isopsephy_policy": POLICY, "rows": rows}

class DrawState:
    def __init__(self, d: dict):
        object.__setattr__(self, "_d", d)
        for r in d["correspondences"]["rows"]:
            if r["evidence"] is not None: check_level(r["evidence"])
    def __setattr__(self, k, v): raise LockedError("use os métodos")
    @classmethod
    def _build(cls, draw: Draw, generation: dict, declared=None, parent=None):
        val = validate(draw, declared_count=declared.get("pieces_count") if declared else None)
        calc = recompute(draw)
        diff = {k: [declared["calculated"][k], v] for k, v in calc.items()
                if declared and declared.get("calculated", {}).get(k) not in (None, v)}
        return cls({"schema": "drawstate-v1", "draw_id": str(uuid.uuid4()), "version": 1, "parent": parent,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"), "revealed": False,
            "data": {"generation": generation, "pieces_count": len(draw.pieces),
                "pieces": [{"id": p.id, "position": p.position, "top": p.top, "bottom": p.bottom, "sum": p.sum} for p in draw.pieces],
                "calculated": calc, "input_discrepancies": diff, "validation": val},
            "correspondences": correspondences(draw), "reading": None, "audit": {"locked": False, "hash": None, "data_hash": None}})
    @classmethod
    def simulated(cls, seed: int, k: int = 7):
        return cls._build(Engine().draw(seed, k), {"mode": "simulado", "seed": seed, "k": k, **GEN_PROFILE})
    @classmethod
    def physical(cls, pairs, declared=None):
        return cls._build(Engine.manual(pairs), {"mode": "fisico", "recorded": "sequência + orientação (topo/base)"}, declared)
    def get(self): return copy.deepcopy(self._d)  # sempre cópia: estado interno não muta por fora
    @property
    def locked(self): return self._d["audit"]["locked"]
    def set_reading(self, text: str):
        if self.locked: raise LockedError("leitura fixada no reveal; use revise()")
        self._d["reading"] = {"text": text, "evidence_effect": "nenhum (camada autoral)"}
    def set_correspondences(self, c: dict):
        if self.locked: raise LockedError("correspondências imutáveis após reveal; use revise()")
        DrawState({**self._d, "correspondences": c}); self._d["correspondences"] = c
    def _payload(self): return {k: v for k, v in self._d.items() if k not in ("audit", "revealed")}
    def reveal(self):
        if self.locked: raise LockedError("já revelado")
        self._d["audit"] = {"locked": True, "hash": _h(self._payload()), "data_hash": _h(self._d["data"])}
        self._d["revealed"] = True
    def verify(self) -> bool:
        return self.locked and self._d["audit"]["hash"] == _h(self._payload()) and self._d["audit"]["data_hash"] == _h(self._d["data"])
    def verify_simulation(self) -> bool:
        g = self._d["data"]["generation"]
        return g["mode"] == "simulado" and DrawState.simulated(g["seed"], g["k"])._d["data"] == self._d["data"]
    def revise(self, reason: str, reading=None, correspondences=None):
        """Nova versão vinculada; original preservado. Dados operacionais não são revisáveis."""
        if not self.locked: raise LockedError("só se revisa versão revelada")
        if not reason: raise ValueError("motivo obrigatório")
        d = self.get(); d.update(draw_id=str(uuid.uuid4()), version=d["version"] + 1, revealed=False,
            parent={"draw_id": self._d["draw_id"], "hash": self._d["audit"]["hash"], "reason": reason},
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"), audit={"locked": False, "hash": None, "data_hash": None})
        n = DrawState(d)
        if correspondences: n.set_correspondences(correspondences)
        if reading is not None: n.set_reading(reading)
        n.reveal(); return n
    def to_json(self) -> str: return json.dumps(self._d, ensure_ascii=False, indent=2)
    @classmethod
    def from_json(cls, s: str): return cls(json.loads(s))
