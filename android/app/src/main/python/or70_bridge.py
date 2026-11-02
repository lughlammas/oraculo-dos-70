"""Ponte Android -> núcleo or70 (inalterado). Entradas/saídas em JSON string. Nenhuma regra nova aqui."""
import json
from or70.drawstate import DrawState, _h, LockedError
from or70.audit import ficha
from or70.cli import PLACEHOLDER

def _ok(ds): return json.dumps({"ok": True, "state": ds.get(), "data_hash": _h(ds.get()["data"])}, ensure_ascii=False)
def _err(e): return json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False)

def draw_seed(seed, k=7):
    try: return _ok(DrawState.simulated(int(seed), int(k)))
    except Exception as e: return _err(e)

def draw_physical(text):
    """Formato do CLI: "3/4,4/0,..." (topo/base, em ordem)."""
    try:
        pairs = []
        for x in text.replace(" ", "").split(","):
            a, b = x.split("/"); pairs.append((int(a), int(b)))
        return _ok(DrawState.physical(pairs))
    except Exception as e: return _err(e)

def reveal(state_json):
    """Mesmo comportamento do `or70 reveal`: leitura placeholder [D] + trava + hash."""
    try:
        ds = DrawState.from_json(state_json); ds.set_reading(PLACEHOLDER); ds.reveal(); return _ok(ds)
    except Exception as e: return _err(e)

def try_set_reading(state_json, text):
    """Usado para demonstrar a trava: em estado revelado deve falhar com LockedError."""
    try:
        ds = DrawState.from_json(state_json); ds.set_reading(text); return _ok(ds)
    except Exception as e: return _err(e)

def revise(state_json, reason):
    try: return _ok(DrawState.from_json(state_json).revise(reason))
    except Exception as e: return _err(e)

def verify(state_json):
    try:
        ds = DrawState.from_json(state_json); sim = ds.get()["data"]["generation"]["mode"] == "simulado"
        return json.dumps({"ok": True, "hash_ok": ds.verify(), "reproduz": ds.verify_simulation() if sim else "n/a (físico)",
                           "data_hash": _h(ds.get()["data"])})
    except Exception as e: return _err(e)

def report(state_json):
    try: return json.dumps({"ok": True, "text": ficha(json.loads(state_json))}, ensure_ascii=False)
    except Exception as e: return _err(e)
