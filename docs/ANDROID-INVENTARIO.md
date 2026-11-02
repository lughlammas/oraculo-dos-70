# Android — Inventário e contrato (v0, 02/11/2026)

## Insumos verificados (evidência = arquivo no repo)
| Item | Estado | Evidência |
|---|---|---|
| Motor `or70` 0.1.0, só stdlib | Verificado | `pyproject.toml`, imports em `or70/` |
| Catálogo/matriz dos 70 | **AUSENTE** — `matrix-empty-v0` (0 entradas) | `or70/drawstate/__init__.py` `MATRIX_VERSION` |
| Classes A–D | Verificado (regras de `classify`, sem dados) | `or70/isopsephy` |
| Bloqueio pós-reveal | Verificado | `DrawState.reveal/LockedError/revise` |
| Testes | 19 pytest (17 núcleo + 2 ponte Android) | `tests/` |
| Exemplos E/S | CLI `draw/reveal/verify` | `README.md` |

**Relação 28 ↔ 70 (como está no código):** 28 peças = duplo-seis. Cada consulta gera índices s_i (soma da peça, 0..12), U (soma topos), L (soma bases), T=U+L. Domínio editorial da matriz: 1..70. Físico com 7 peças distintas: 15 ≤ T ≤ 69. Índice 0 ou fora de 1..70 = "sem correspondência definida na matriz" (sem remapeamento). 8+ peças = modalidade expandida declarada (aviso).

**Relação A–D × bloqueio:** independentes. A–D é atributo de cada entrada da matriz; bloqueio é estado da consulta. Nenhuma regra no núcleo liga um ao outro.

## Lacunas — pedir definição ao Gui
1. Matriz dos 70 (termo grego, rótulo, fontes, revisor) — sem ela toda linha sai "lacuna".
2. Texto interpretativo — hoje placeholder `[D]` do CLI.
3. Tiragem fisicamente inválida (duplicada, face>6): núcleo **registra com erro** e não impede reveal. Bloquear ou não? (decisão)
4. Regra para índice 0.
5. Política de compatibilidade quando chegar matriz v1 (consultas v0 continuam ligadas à v0; nada é substituído em silêncio — já é o comportamento: versão gravada no JSON).

## Ambiente (box)
JDK Temurin 17.0.21 · Gradle 8.7 (wrapper) · AGP 8.5.2 · Kotlin 1.9.24 · Chaquopy 16.0.0 (Python 3.13 embarcado; host 3.13.5) · SDK platform 34, build-tools 34.0.0 · emulador + system-image android-34 x86_64 · /dev/kvm (permissão ajustada na box) · 98 GB livres.

## Caminho escolhido: Kotlin + Chaquopy
Núcleo é Python puro sem deps → Chaquopy roda o **mesmo código** (copiado de `../or70` no build, sem fork). Port Kotlin exigiria provar equivalência de isopséfia/hash — desnecessário. PWA/TWA descartados (não é APK do núcleo real; TWA exigiria site + Digital Asset Links).
UI: Views Kotlin (não Compose — pendência, ver relatório).

## Contrato determinístico (`drawstate-v1`, inalterado)
- Influencia resultado: peças em ordem de posição com orientação (topo/base); `generation` (simulado: seed, k, prng=splitmix64 v1, ordem inicial lexicográfica, Fisher-Yates parcial com rejeição, regra de orientação `below(2)==1` troca); `matrix_version`; `isopsephy_policy` (iso-policy-v1).
- Serialização do hash: `json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False)` → UTF-8 → SHA-256. Sem normalização Unicode extra.
- `audit.data_hash` = hash de `data` (determinístico; base da equivalência).
- `audit.hash` = hash do documento inteiro **exceto** `audit` e `revealed` (inclui draw_id uuid4 e timestamp → muda a cada consulta).
- Reprodução = entradas completas + versões motor/catálogo; `verify_simulation` regenera `data` pela seed.
- Integridade ≠ autenticidade: hash mostra que o conteúdo bate com a referência gravada; **não** prova autoria, origem, nem fundamentação histórica. Não é assinatura nem backup.

## Travas
- Aciona: `reveal()`. Impede: `set_reading`, `set_correspondences`, novo `reveal` (LockedError).
- Liberação: não existe; `revise(motivo)` cria v+1 com `parent={draw_id, hash, motivo}`; original intacto.
- Persistência: app grava o JSON em `filesDir/current_drawstate.json` a cada mudança; ao reabrir, a trava vem do próprio JSON (`audit.locked`) e é reconferida por `verify`. Editar o arquivo à mão quebra `hash_ok`.
