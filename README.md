# Oráculo dos 70 — Core Engine (build 0.2)
Núcleo determinístico: dominó duplo-seis (28 peças), contrato `drawstate-v1` em 3 camadas (dados / correspondências / leitura), isopséfia com política versionada (`iso-policy-v1`), classificação A–D sem promoção sem revisão, trava + SHA-256 no reveal, correção = nova versão vinculada. Sem dependências de runtime.

    python -m venv .venv && .venv/bin/pip install pytest && .venv/bin/python -m pytest -q
    python -m or70.cli draw --seed 70 > d.json                 # simulado
    python -m or70.cli draw --pieces 3/4,4/0,5/2,4/2,5/1,5/4,5/5 # físico (topo/base)
    python -m or70.cli reveal --file d.json [--ficha] > r.json
    python -m or70.cli verify --file r.json                     # hash + reprodução

Lacunas declaradas: matriz dos 70 vazia (`matrix-empty-v0`); leitura = placeholder [D]; índice 0 sem regra autoral.
