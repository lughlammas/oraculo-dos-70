import json, pytest
from or70.domino import Engine, SplitMix64, validate, full_set
from or70.drawstate import DrawState, LockedError
from or70.isopsephy import isopsephy, classify, check_level, rigor
from or70.cli import main

def test_set_28(): assert len(full_set()) == 28
def test_splitmix_vetor():  # vetor de referência SplitMix64 seed 0
    assert SplitMix64(0).next() == 0xE220A8397B1DCDAF
def test_determinismo():
    e = Engine(); assert e.draw(70) == e.draw(70) and e.draw(70) != e.draw(71)
def test_sem_duplicatas():
    for s in range(300):
        d = Engine().draw(s); assert len({p.id for p in d.pieces}) == 7
def test_somas_exemplo_spec():
    d = Engine.manual([(3,4),(4,0),(5,2),(4,2),(5,1),(5,4),(5,5)])
    assert (d.U, d.L, d.T) == (31, 18, 49) and validate(d) == []
def test_duplicata_detectada():
    assert "peça duplicada" in validate(Engine.manual([(1,2),(2,1)]))
def test_isopsefia():
    assert isopsephy("ἀγάπη") == 93 and isopsephy("θέλημα") == 93
    assert isopsephy("λόγος") == 373 and isopsephy("ᾠδή") == 812
    with pytest.raises(ValueError): isopsephy("abc")
def test_classify():
    assert classify({"index": 93, "greek_term": "ἀγάπη", "ref_lexical": "LSJ"}) == "A"
    assert classify({"index": 93, "greek_term": "ἀγάπη"}) == "D"
    assert classify({"index": 5, "historical_source": "x"}) == "C"
def test_evidencia_so_abcd():
    with pytest.raises(ValueError): check_level("E")
    ds = DrawState.new(Engine().draw(1))
    with pytest.raises(ValueError): ds.set("terms", [{"id":"x","label":"x","evidence":"Z","source":"","note":""}])
def test_rigor_spec():
    r = rigor(["A"]*13+["B"]*14+["C"]*6+["D"]*37)
    assert r["authorial_pct"] == 52.86 and r["rigor_pct"] == 38.57
def test_lock_impede_mutacao():
    ds = DrawState.new(Engine().draw(70), seed=70); ds.reveal()
    for k in ("pieces", "terms", "seed"):
        with pytest.raises(LockedError): ds.set(k, [])
    ds["pieces"][0]["top"] = 99; ds["terms"].clear()
    assert ds.verify()
    with pytest.raises(LockedError): ds.reveal()
def test_narrativa_nao_muda_hash():
    ds = DrawState.new(Engine().draw(70), seed=70)
    with pytest.raises(LockedError): ds.attach_narrative("x")
    ds.reveal(); h = ds["audit"]["hash"]; ds.attach_narrative("texto")
    assert ds.canonical_hash() == h and ds.verify()
def test_hash_estavel_roundtrip():
    ds = DrawState.new(Engine().draw(70), seed=70); ds.reveal()
    ds2 = DrawState.from_json(ds.to_json()); assert ds2.verify()
    d = json.loads(ds.to_json()); d["pieces"][0]["top"] = 0
    assert not DrawState(d).verify()
def test_cli(capsys, tmp_path):
    main(["draw", "--seed", "70"]); d = json.loads(capsys.readouterr().out)
    assert d["schema"] == "drawstate-v0" and len(d["pieces"]) == 7 and d["audit"]["locked"] is False
    f = tmp_path/"d.json"; f.write_text(json.dumps(d), encoding="utf-8")
    main(["reveal", "--file", str(f)]); r = json.loads(capsys.readouterr().out)
    assert r["revealed"] and r["audit"]["locked"] and len(r["audit"]["hash"]) == 64
