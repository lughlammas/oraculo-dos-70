import json, pytest
from or70.domino import Engine, SplitMix64, validate, full_set
from or70.drawstate import DrawState, LockedError
from or70.isopsephy import isopsephy, analyze, classify, check_level, composition
from or70.cli import main

EX = [(3,4),(4,0),(5,2),(4,2),(5,1),(5,4),(5,5)]
def test_set_28(): assert len(full_set()) == 28
def test_splitmix_vetor(): assert SplitMix64(0).next() == 0xE220A8397B1DCDAF
def test_determinismo_dados_completos():
    a, b = DrawState.simulated(70), DrawState.simulated(70)
    assert a.get()["data"] == b.get()["data"] and a.verify_simulation()
    assert a.get()["data"]["generation"]["prng"] == "splitmix64"
    assert DrawState.simulated(71).get()["data"] != a.get()["data"]
def test_sem_duplicatas():
    for s in range(300): assert validate(Engine().draw(s))["valid"]
def test_canonica_nao_orientada():
    assert not validate(Engine.manual([(3,4),(4,3)]))["valid"]
def test_somas_recalculadas_e_divergencia():
    ds = DrawState.physical(EX, declared={"pieces_count": 7, "calculated": {"total_sum": 50}}).get()["data"]
    assert ds["calculated"] == {"upper_line_sum": 31, "lower_line_sum": 18, "total_sum": 49}
    assert ds["input_discrepancies"] == {"total_sum": [50, 49]} and ds["validation"]["valid"]
def test_count_declarado_e_faces():
    assert not DrawState.physical(EX, declared={"pieces_count": 6}).get()["data"]["validation"]["valid"]
    assert not validate(Engine.manual([(7,1)]))["valid"]
def test_expandida_declarada():
    v = validate(Engine().draw(1, 8)); assert v["modality"] == "expandida-declarada" and v["warnings"]
def test_zero_sem_remap():
    rows = DrawState.physical([(0,0),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6)]).get()["correspondences"]["rows"]
    s1 = rows[0]; assert s1["index"] == 0 and "sem correspondência" in s1["status"] and s1["evidence"] is None
def test_isopsefia():
    assert isopsephy("ἀγάπη") == 93 and isopsephy("λόγος") == 373 and isopsephy("ᾠδή") == 812
    r = analyze("abc"); assert r["sum"] is None and r["unknown"] == list("abc")
    with pytest.raises(ValueError): isopsephy("ab")
def test_classify_nao_promove():
    e = {"index": 93, "greek_term": "ἀγάπη", "ref_lexical": "LSJ s.v."}
    r = classify(e); assert r["level"] == "D" and r["arithmetic"] and r["pending"]
    assert classify({**e, "reviewed_by": "rev", "meaning_pertinent": True})["level"] == "A"
    assert classify({"index": 5, "historical_source": "x"})["level"] == "D"
    assert classify({"index": 5, "historical_source": "x", "reviewed_by": "r"})["level"] == "C"
def test_evidencia_so_abcd():
    with pytest.raises(ValueError): check_level("E")
def test_composicao_spec():
    r = composition(["A"]*13+["B"]*14+["C"]*6+["D"]*37)
    assert (r["lexical_exact_AB_pct"], r["historical_arithmological_C_pct"], r["documentary_coverage_ABC_pct"], r["authorial_D_pct"]) == (38.57, 8.57, 47.14, 52.86)
def test_lock_impede_mutacao():
    ds = DrawState.simulated(70); ds.set_reading("x"); ds.reveal()
    with pytest.raises(LockedError): ds.set_reading("y")
    with pytest.raises(LockedError): ds.set_correspondences({"rows": []})
    with pytest.raises(LockedError): ds.reveal()
    ds.get()["data"]["pieces"].clear(); assert ds.verify()
def test_hash_estavel_e_adulteracao():
    ds = DrawState.simulated(70); ds.reveal()
    assert DrawState.from_json(ds.to_json()).verify()
    d = json.loads(ds.to_json()); d["data"]["pieces"][0]["top"] = 0; assert not DrawState(d).verify()
    d = json.loads(ds.to_json()); d["reading"] = {"text": "post-hoc"}; assert not DrawState(d).verify()
def test_revisao_versionada():
    ds = DrawState.simulated(70); ds.set_reading("v1"); ds.reveal(); h = ds.get()["audit"]["hash"]
    n = ds.revise("correção de digitação", reading="v2")
    assert n.get()["version"] == 2 and n.get()["parent"]["hash"] == h and n.verify()
    assert ds.get()["reading"]["text"] == "v1" and ds.verify()
    with pytest.raises(ValueError): ds.revise("")
def test_cli(capsys, tmp_path):
    main(["draw", "--seed", "70"]); d = json.loads(capsys.readouterr().out)
    assert d["schema"] == "drawstate-v1" and len(d["data"]["pieces"]) == 7
    f = tmp_path/"d.json"; f.write_text(json.dumps(d), encoding="utf-8")
    main(["reveal", "--file", str(f)]); r = capsys.readouterr().out
    f.write_text(r, encoding="utf-8"); assert main(["verify", "--file", str(f)]) == 0
    assert json.loads(capsys.readouterr().out) == {"hash_ok": True, "reproduz": True}
