"""Mesmos casos do teste instrumentado Android, rodando a ponte no host (fonte da verdade = CLI)."""
import json, subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "android/app/src/main/python"))
import or70_bridge as b
from or70.drawstate import _h

def test_bridge_equals_cli():
    cli = json.loads(subprocess.run([sys.executable, "-m", "or70.cli", "draw", "--seed", "70"], capture_output=True, text=True, check=True).stdout)
    r = json.loads(b.draw_seed(70)); assert r["data_hash"] == _h(cli["data"]) == "74f10b287ac8c25fd47fe86e65c88cbdc894ef52f647ac0ae0b406bb34d648c5"

def test_lock_and_revise():
    s = json.dumps(json.loads(b.reveal(json.dumps(json.loads(b.draw_seed(70))["state"])))["state"])
    assert json.loads(b.try_set_reading(s, "x"))["error"].startswith("LockedError")
    assert json.loads(b.verify(s))["hash_ok"] is True
    assert json.loads(b.revise(s, "m"))["state"]["version"] == 2
