# MAXIMUS Core Service - Plano de Refatoração

## Objetivo
Refatorar `maximus_core_service` para compliance 100% com CODE_CONSTITUTION (4 Pilares)

## Diagnóstico

### Status Atual
| Métrica | Status | Detalhes |
|---------|--------|----------|
| **Arquivos >500 linhas** | ❌ **152** | 65 críticos (>700), 87 altos (500-700) |
| **Type Hints** | ✅ 100% | Perfeito |
| **Future Annotations** | ✅ 100% | Perfeito |
| **Docstrings** | ✅ 100% | Perfeito |
| **TODO/FIXME** | ✅ 0 | Limpo |

### Arquivos Críticos de Produção (>700 linhas)
1. `ethical_guardian.py` - **1.251 linhas**
2. `compliance/regulations.py` - **964 linhas**
3. `adw_router.py` - **939 linhas**
4. `governance_sse/api_routes.py` - **841 linhas**
5. `_demonstration/maximus_integrated.py` - **837 linhas**
6. `motor_integridade_processual/api.py` - **808 linhas**
7. `xai/counterfactual.py` - **802 linhas**
8. `workflows/target_profiling_adw.py` - **768 linhas**
9. `governance/guardian/article_v_guardian.py` - **705 linhas**

---

## Critérios de Sucesso
1. ✅ Código continuar funcionando (810+ testes passando)
2. ✅ Nenhum arquivo >500 linhas (ideal <400)
3. ✅ 100% Google Python Style Guide

---

## Fase 1: Arquivos Críticos (P0)

### 1.1 `ethical_guardian.py` (1.251 → 9 arquivos)

**Estrutura proposta:**
```
ethical_guardian/
├── __init__.py              (~30 linhas)  # Re-exports
├── models.py                (~200 linhas) # 9 dataclasses + EthicalDecisionType
├── guardian.py              (~250 linhas) # Main class + validate_action
├── phase0_governance.py     (~80 linhas)  # _governance_check
├── phase1_ethics.py         (~60 linhas)  # _ethics_evaluation
├── phase2_xai.py            (~60 linhas)  # _generate_explanation
├── phase3_fairness.py       (~130 linhas) # _fairness_check
├── phase4_privacy.py        (~80 linhas)  # _privacy_check + _fl_check
├── phase5_hitl.py           (~140 linhas) # _hitl_check
├── phase6_compliance.py     (~60 linhas)  # _compliance_check
└── statistics.py            (~50 linhas)  # _log_decision, get_statistics
```

### 1.2 `compliance/regulations.py` (964 → 9 arquivos)

**Estrutura proposta:**
```
compliance/regulations/
├── __init__.py              (~50 linhas)  # REGULATION_REGISTRY + get_regulation
├── eu_ai_act.py             (~150 linhas) # EU_AI_ACT
├── gdpr.py                  (~100 linhas) # GDPR
├── nist_ai_rmf.py           (~130 linhas) # NIST_AI_RMF
├── us_eo_14110.py           (~90 linhas)  # US_EO_14110
├── brazil_lgpd.py           (~100 linhas) # BRAZIL_LGPD
├── iso_27001.py             (~130 linhas) # ISO_27001
├── soc2_type_ii.py          (~120 linhas) # SOC2_TYPE_II
└── ieee_7000.py             (~110 linhas) # IEEE_7000
```

### 1.3 `adw_router.py` (939 → 7 arquivos)

**Estrutura proposta:**
```
adw/
├── __init__.py              (~30 linhas)  # Re-exports
├── router.py                (~80 linhas)  # Main router + health
├── models.py                (~120 linhas) # Request/Response models
├── endpoints_offensive.py   (~150 linhas) # Red Team
├── endpoints_defensive.py   (~180 linhas) # Blue Team
├── endpoints_purple.py      (~100 linhas) # Purple Team
├── endpoints_osint.py       (~250 linhas) # OSINT workflows
└── dependencies.py          (~80 linhas)  # Service singletons
```

### 1.4 `governance_sse/api_routes.py` (841 → 6 arquivos)

**Estrutura proposta:**
```
governance_sse/api/
├── __init__.py              (~30 linhas)
├── models.py                (~120 linhas)
├── endpoints_streaming.py   (~180 linhas) # SSE streaming
├── endpoints_session.py     (~120 linhas) # Session management
├── endpoints_decision.py    (~250 linhas) # Decision actions
└── endpoints_stats.py       (~100 linhas) # Stats/health
```

### 1.5 `motor_integridade_processual/api.py` (808 → 6 arquivos)

**Estrutura proposta:**
```
motor_integridade_processual/api/
├── __init__.py              (~30 linhas)
├── app.py                   (~100 linhas) # FastAPI app
├── models.py                (~150 linhas) # Request/Response
├── endpoints_core.py        (~200 linhas) # /evaluate, /health
├── endpoints_precedents.py  (~150 linhas) # Precedent CRUD
└── endpoints_abtest.py      (~120 linhas) # A/B testing
```

---

## Fase 2: Arquivos Altos (P1) - 30 arquivos 500-700 linhas

Prioridade:
- `fairness/mitigation.py` (695)
- `xai/lime_cybersec.py` (693)
- `attention_system/attention_core.py` (665)
- `compliance/evidence_collector.py` (665)
- `governance/guardian/coordinator.py` (661)
- `governance/ethics_review_board.py` (640)
- `governance/guardian/base.py` (633)

---

## Fase 3: Arquivos de Teste (P2) - 52 arquivos >700 linhas

Estratégia: Split por test class, shared fixtures em `conftest.py`

---

## Processo de Execução (Por Arquivo)

1. **Criar estrutura de diretórios**
2. **Extrair código para novos arquivos** (preservar lógica exata)
3. **Criar `__init__.py`** com re-exports para backward compatibility
4. **Rodar testes específicos**: `pytest -k "nome_modulo" -v`
5. **Atualizar imports** nos arquivos dependentes
6. **Rodar suite completa**: `pytest tests/ -v`
7. **Commit granular**: um arquivo por commit

---

## Estratégia de Imports

**DECISÃO: Atualizar TODOS os imports (sem backward compatibility layer)**

Para cada arquivo refatorado:
1. Grep todos os imports do arquivo original
2. Atualizar para novo path
3. Deletar arquivo original após refatoração

```bash
# Exemplo: encontrar todos imports de ethical_guardian
grep -r "from ethical_guardian import" --include="*.py"
grep -r "import ethical_guardian" --include="*.py"
```

---

## Verificação Final

```bash
# Nenhum arquivo >500 linhas
find . -name "*.py" -exec wc -l {} \; | awk '$1>500 {print}'

# Testes passando
PYTHONPATH=. pytest tests/ -v

# Import funcionando
python -c "from maximus_core_service.ethical_guardian import EthicalGuardian"
```

---

## Escopo Completo (152 Arquivos)

**DECISÃO: Refatorar TODOS os 152 arquivos (produção + testes)**

### Fase 1 - P0 Críticos (9 arquivos >700 linhas produção)
| # | Arquivo | Linhas |
|---|---------|--------|
| 1 | `ethical_guardian.py` | 1.251 |
| 2 | `compliance/regulations.py` | 964 |
| 3 | `adw_router.py` | 939 |
| 4 | `governance_sse/api_routes.py` | 841 |
| 5 | `motor_integridade_processual/api.py` | 808 |
| 6 | `xai/counterfactual.py` | 802 |
| 7 | `workflows/target_profiling_adw.py` | 768 |
| 8 | `governance/guardian/article_v_guardian.py` | 705 |
| 9 | `_demonstration/maximus_integrated.py` | 837 |

### Fase 2 - P1 Altos (30 arquivos 500-700 linhas produção)
- `fairness/mitigation.py` (695)
- `xai/lime_cybersec.py` (693)
- `attention_system/attention_core.py` (665)
- E mais 27 arquivos...

### Fase 3 - P2 Testes (52 arquivos >700 linhas)
- Split por test class
- Shared fixtures em `conftest.py`

### Fase 4 - P3 Testes Médios (61 arquivos 500-700 linhas)
- Mesma estratégia da Fase 3

---

## Referências

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- CODE_CONSTITUTION.md (4 Pilares)
- PEP 8, PEP 257
