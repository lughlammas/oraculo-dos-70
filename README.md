# Oráculo dos 70 — Core Engine (build 0.1)
Núcleo determinístico de tiragem com dominó duplo-seis (28 peças), isopséfia grega, contrato `drawstate-v0` com trava + hash SHA-256 pós-revelação e ficha de auditoria A/B/C/D. Sem UI, sem dependências.

    pip install pytest && python -m pytest -q
    python -m or70.cli draw --seed 70 > d.json
    python -m or70.cli reveal --file d.json           # JSON travado
    python -m or70.cli reveal --file d.json --ficha   # ficha de auditoria

Stubs: termos de arquétipo são placeholders `[D]`; única fixture A = Liber O (Fogo Leste, Terra Sul, Ar Oeste, Água Norte). Narrativa = placeholder.
