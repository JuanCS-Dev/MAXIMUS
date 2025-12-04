# REFINO FINAL INICIAL - Plano Heroico de Auditoria e Correção
## MAXIMUS 2.0 - CODE_CONSTITUTION Compliance

**Data:** 03 de Dezembro de 2025
**Arquiteto-Chefe:** Juan Carlos de Souza
**Escopo:** `/backend/services` (14 serviços, 1.807 arquivos, 356.348 LOC)

---

## 🟢 SNAPSHOT DE ESTADO ATUAL (03/12/2025 19:00)

### PROGRESSO ATUAL:
**Decomposições em reactive_fabric_core - 7 arquivos completos**

### STATUS DETALHADO DAS DECOMPOSIÇÕES:

#### ✅ 1. ethical_audit_service/api.py (2770 → 16 arquivos) - COMPLETO
```
ethical_audit_service/api/
├── __init__.py           (criado)
├── app.py                (133 linhas)
├── state.py              (51 linhas)
├── dependencies.py       (existente)
├── routes.py             (existente)
└── routers/
    ├── __init__.py       (27 linhas)
    ├── audit.py          (190 linhas)
    ├── certification.py  (404 linhas)
    ├── compliance_logs.py (50 linhas)
    ├── fairness.py       (428 linhas)
    ├── federated.py      (263 linhas)
    ├── health.py         (52 linhas)
    ├── hitl.py           (420 linhas)
    ├── metrics.py        (145 linhas)
    ├── privacy.py        (201 linhas)
    └── xai.py            (220 linhas)
```
- Original renomeado para: `api_legacy.py`
- models/__init__.py atualizado para re-exportar de models_legacy.py

#### ✅ 2. reactive_fabric_core/hitl/hitl_backend.py (942 → 7 arquivos) - COMPLETO
```
reactive_fabric_core/hitl/hitl_backend/
├── __init__.py           (48 linhas)
├── app.py                (105 linhas)
├── auth.py               (260 linhas)
├── database.py           (113 linhas)
├── decisions.py          (223 linhas)
├── models.py             (153 linhas)
└── websocket_routes.py   (103 linhas)
```
- Original renomeado para: `hitl_backend_legacy.py`

#### ✅ 3. reactive_fabric_core/hitl/hitl_engine.py (858 → 5 arquivos) - COMPLETO
```
reactive_fabric_core/hitl/hitl_engine/
├── __init__.py           (40 linhas)
├── alerts.py             (247 linhas) - AlertManagementMixin
├── decisions.py          (199 linhas) - DecisionManagementMixin
├── engine.py             (268 linhas) - HITLEngine (combina mixins)
└── models.py             (149 linhas) - Enums e Pydantic models
```
- Original renomeado para: `hitl_engine_legacy.py`

#### ✅ 4. reactive_fabric_core/response/response_orchestrator.py (809 → 6 arquivos) - COMPLETO
```
response/response_orchestrator/
├── __init__.py           (30 linhas)
├── action_handlers.py    (200 linhas) - ActionHandlersMixin
├── execution.py          (130 linhas) - ExecutionMixin
├── models.py             (140 linhas) - Enums e Pydantic models
├── orchestrator.py       (240 linhas) - ResponseOrchestrator
└── planning.py           (160 linhas) - PlanningMixin
```
- Original renomeado para: `response_orchestrator_legacy.py`

#### ✅ 5. reactive_fabric_core/collectors/threat_intelligence_collector.py (681 → 6 arquivos) - COMPLETO
```
collectors/threat_intelligence_collector/
├── __init__.py           (20 linhas)
├── checkers.py           (270 linhas) - IndicatorCheckerMixin
├── collector.py          (180 linhas) - ThreatIntelligenceCollector
├── feed_collectors.py    (120 linhas) - FeedCollectorMixin
├── models.py             (70 linhas) - Config e ThreatIndicator
└── validators.py         (80 linhas) - SourceValidatorMixin
```
- Original renomeado para: `threat_intelligence_collector_legacy.py`

#### ✅ 6. reactive_fabric_core/deception/deception_engine.py (671 → 5 arquivos) - COMPLETO
```
deception/deception_engine/
├── __init__.py           (35 linhas)
├── checkers.py           (180 linhas) - DeceptionCheckerMixin
├── engine.py             (250 linhas) - DeceptionEngine
├── generator.py          (95 linhas) - HoneytokenGenerator
└── models.py             (165 linhas) - Enums e Pydantic models
```
- Original renomeado para: `deception_engine_legacy.py`

#### ✅ 7. reactive_fabric_core/orchestration/orchestration_engine.py (613 → 6 arquivos) - COMPLETO
```
orchestration/orchestration_engine/
├── __init__.py           (35 linhas)
├── correlator.py         (75 linhas) - EventCorrelator
├── engine.py             (230 linhas) - OrchestrationEngine
├── models.py             (115 linhas) - Enums e Pydantic models
├── pattern_detector.py   (90 linhas) - PatternDetector
└── threat_scorer.py      (85 linhas) - ThreatScorer
```
- Original renomeado para: `orchestration_engine_legacy.py`

#### ✅ 8. reactive_fabric_core/candi/attribution_engine.py (581 → 5 arquivos) - COMPLETO
```
candi/attribution_engine/
├── __init__.py           (20 linhas)
├── database.py           (160 linhas) - Threat actor databases
├── engine.py             (145 linhas) - AttributionEngine
├── models.py             (40 linhas) - AttributionResult
└── scorers.py            (200 linhas) - AttributionScorerMixin
```
- Original renomeado para: `attribution_engine_legacy.py`

### ARQUIVOS RESTANTES >500 LINHAS EM reactive_fabric_core:
| Arquivo | Linhas | Status |
|---------|--------|--------|
| candi/forensic_analyzer.py | 577 | ⏳ PENDENTE |
| candi/threat_intelligence.py | 570 | ⏳ PENDENTE |
| honeypots/honeytoken_manager.py | 556 | ⏳ PENDENTE |
| collectors/log_aggregation_collector.py | 551 | ⏳ PENDENTE |
| candi/candi_core.py | 533 | ⏳ PENDENTE |
| honeypots/postgres_honeypot.py | 525 | ⏳ PENDENTE |
| honeypots/cowrie_ssh.py | 517 | ⏳ PENDENTE |
| isolation/kill_switch.py | 513 | ⏳ PENDENTE |

### COMANDO PARA RETOMAR:
```bash
# Verificar estado atual
ls -la backend/services/reactive_fabric_core/response/response_orchestrator/
ls -la backend/services/reactive_fabric_core/hitl/hitl_engine/
ls -la backend/services/reactive_fabric_core/hitl/hitl_backend/
ls -la backend/services/ethical_audit_service/api/routers/
```

---

## SUMÁRIO EXECUTIVO

### Status Atual vs Meta

| Métrica | Atual | Meta | Gap |
|---------|-------|------|-----|
| Arquivos >500 linhas | **49** | 0 | -49 |
| Missing `from __future__` | **46** | 0 | -46 |
| TODO/FIXME/HACK | **45** | 0 | -45 |
| Pylint <9.0 | **7 serviços** | 0 | -7 |
| Import desordenado | **42** | 0 | -42 |

### Violação Crítica Principal
**`ethical_audit_service/api.py` - 2.770 linhas** (5.5x o limite!)

---

## MAPA COMPLETO DOS 14 SERVIÇOS

| # | Serviço | Arquivos | LOC | >500L | Pylint | Status |
|---|---------|----------|-----|-------|--------|--------|
| 1 | api_gateway | 8 | 186 | 0 | 10.00 | ✅ EXCELENTE |
| 2 | digital_thalamus_service | 31 | 2,830 | 1 | 7.44 | ❌ CRÍTICO |
| 3 | episodic_memory | 16 | 1,701 | 1 | 8.55 | ⚠️ ABAIXO |
| 4 | ethical_audit_service | 31 | 6,036 | **2** | **6.09** | ❌ CRÍTICO |
| 5 | hcl_analyzer_service | 25 | 2,323 | 1 | 8.24 | ⚠️ ABAIXO |
| 6 | hcl_executor_service | 17 | 973 | 1 | 9.80 | ✅ PASS |
| 7 | hcl_monitor_service | 22 | 1,816 | 1 | 9.87 | ✅ PASS |
| 8 | hcl_planner_service | 19 | 1,692 | 1 | 7.72 | ❌ CRÍTICO |
| 9 | **maximus_core_service** | **1,444** | **109,699** | **27** | ~8.5 | ⚠️ MAIOR |
| 10 | metacognitive_reflector | 49 | 8,002 | 1 | 9.70 | ✅ PASS |
| 11 | meta_orchestrator | 22 | 2,847 | 1 | 8.59 | ⚠️ ABAIXO |
| 12 | prefrontal_cortex_service | 30 | 2,675 | 1 | 7.56 | ❌ CRÍTICO |
| 13 | **reactive_fabric_core** | **91** | **18,291** | **16** | 8.48 | ⚠️ ABAIXO |
| 14 | shared | 1 | 398 | 0 | - | ✅ OK |

---

## FASE 1: CORREÇÕES CRÍTICAS (P0)
**Prazo: 1-2 dias | Esforço: ~20 horas**

### 1.1 `ethical_audit_service/api.py` (2.770 → ~10 arquivos)

**Decomposição proposta:**
```
ethical_audit_service/api/
├── __init__.py              (~30 linhas)
├── app.py                   (~80 linhas)   # FastAPI app setup
├── models.py                (~200 linhas)  # Request/Response models
├── endpoints_audit.py       (~300 linhas)  # Core audit endpoints
├── endpoints_compliance.py  (~250 linhas)  # Compliance endpoints
├── endpoints_reports.py     (~200 linhas)  # Report generation
├── endpoints_health.py      (~80 linhas)   # Health/status
├── auth.py                  (~150 linhas)  # Authentication
├── dependencies.py          (~100 linhas)  # FastAPI dependencies
└── utils.py                 (~100 linhas)  # Utilities
```

### 1.2 `reactive_fabric_core` (16 arquivos >500 linhas)

**Arquivos a refatorar:**
| Arquivo | Linhas | Ação |
|---------|--------|------|
| hitl/hitl_backend.py | 942 | Split: backend_core.py, backend_handlers.py, backend_websocket.py |
| hitl/hitl_engine.py | 858 | Split: engine_core.py, engine_decisions.py, engine_state.py |
| response/response_orchestrator.py | 809 | Split: orchestrator.py, actions.py, strategies.py |
| collectors/threat_intelligence_collector.py | 681 | Split: collector.py, parsers.py, aggregators.py |
| deception/deception_engine.py | 671 | Split: engine.py, techniques.py, deployment.py |

### 1.3 Serviços com Pylint <8.0 (Import chain quebrado)

**digital_thalamus_service (7.44):**
- Criar: `config.py`
- Criar: `models/gateway.py`
- Fix: utils/logging_config.py imports

**prefrontal_cortex_service (7.56):**
- Criar: `config.py`
- Criar: `models/cognitive.py`
- Fix: Line lengths (>100 chars)

**hcl_planner_service (7.72):**
- Criar: `config.py`
- Refatorar: `GeminiClient` (8→7 attrs)
- Split: `generate_plan()` (muitos locals)

**ethical_audit_service (6.09):**
- Fix: auth.py exception chaining
- Add: docstrings módulo
- Fix: logging lazy format

---

## FASE 2: CORREÇÕES IMPORTANTES (P1)
**Prazo: 2-3 dias | Esforço: ~25 horas**

### 2.1 `maximus_core_service` (27 arquivos >500 linhas)

**Arquivos prioritários:**
| Arquivo | Linhas | Ação |
|---------|--------|------|
| fairness/monitor.py | 580 | Mixin pattern |
| governance/base.py | 576 | Mixin pattern |
| hitl/audit_trail.py | 572 | Package split |
| performance/pruner.py | 568 | Mixin pattern |
| hitl/risk_assessor.py | 568 | Mixin pattern |
| hitl/decision_framework.py | 565 | Package split |
| governance/guardian/article_ii_guardian.py | 562 | Package split |
| compliance/certifications.py | 561 | Mixin pattern |

### 2.2 Missing `from __future__ import annotations` (46 arquivos)

**Por serviço:**
| Serviço | Arquivos | Ação |
|---------|----------|------|
| hcl_monitor_service | 19 | Adicionar em TODOS |
| hcl_executor_service | 13 | Adicionar em TODOS |
| api_gateway | 6 | Adicionar em TODOS |
| digital_thalamus_service | 3 | Adicionar |
| prefrontal_cortex_service | 3 | Adicionar |
| hcl_analyzer_service | 1 | Adicionar |
| hcl_planner_service | 1 | Adicionar |

**Script de correção:**
```bash
for f in $(find backend/services -name "*.py" -type f); do
  if [ -s "$f" ] && ! grep -q "from __future__ import annotations" "$f"; then
    sed -i '1i from __future__ import annotations\n' "$f"
  fi
done
```

### 2.3 TODO/FIXME/HACK Placeholders (45 instâncias)

**Alta prioridade (10+ instâncias):**
- `validate_regra_de_ouro.py` - 11 TODOs → Implementar ou NotImplementedError
- `article_ii_guardian.py` - 9 TODOs → Implementar ou NotImplementedError

**Média prioridade:**
- `industrial_test_generator_v*.py` - 8 TODOs (scripts, menor impacto)

---

## FASE 3: ELEVAÇÃO PYLINT ≥9.0 (P2)
**Prazo: 3-5 dias | Esforço: ~30 horas**

### 3.1 Serviços 8.0-9.0 → 9.0+

| Serviço | Score | Issues | Correções |
|---------|-------|--------|-----------|
| episodic_memory | 8.55 | Import errors | Fix models/__init__.py exports |
| reactive_fabric_core | 8.48 | Docstrings, formatting | Add docstrings, fix whitespace |
| hcl_analyzer_service | 8.24 | Duplicate code | Extract shared utilities |
| meta_orchestrator | 8.59 | Broad exceptions | Replace with specific exceptions |

### 3.2 Issues Recorrentes (Cross-Service)

**Broad Exception Handling (1.289 ocorrências):**
```python
# ❌ ANTES
except Exception:
    return {"status": "error"}

# ✅ DEPOIS
except (ValueError, KeyError) as e:
    logger.error(f"Specific error: {e}")
    raise CustomError(f"Operation failed: {e}") from e
```

**Too Many Arguments (R0913/R0917):**
```python
# ❌ ANTES
def process(a, b, c, d, e, f, g):

# ✅ DEPOIS
@dataclass
class ProcessConfig:
    a: str
    b: int
    # ...

def process(config: ProcessConfig):
```

---

## FASE 4: PADRONIZAÇÃO FINAL (P3)
**Prazo: Ongoing | Esforço: ~15 horas**

### 4.1 Import Organization (42 arquivos)

**Ordem padrão CODE_CONSTITUTION:**
```python
"""Module docstring."""

from __future__ import annotations

# Standard library
import asyncio
import logging
from typing import Any, Dict

# Third-party
from fastapi import APIRouter
from pydantic import BaseModel

# Local
from .models import MyModel
from ..shared import utils
```

### 4.2 Pre-commit Hooks

**Arquivo: `.pre-commit-config.yaml`**
```yaml
repos:
  - repo: local
    hooks:
      - id: file-size-check
        name: Check file size (<500 lines)
        entry: bash -c 'for f in $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$"); do lines=$(wc -l < "$f"); if [ "$lines" -gt 500 ]; then echo "ERROR: $f has $lines lines (max 500)"; exit 1; fi; done'
        language: system
        types: [python]

      - id: future-annotations
        name: Check future annotations
        entry: bash -c 'for f in $(git diff --cached --name-only --diff-filter=ACM | grep "\.py$"); do if ! grep -q "from __future__ import annotations" "$f"; then echo "ERROR: $f missing future annotations"; exit 1; fi; done'
        language: system
        types: [python]

      - id: pylint-check
        name: Pylint ≥9.0
        entry: pylint --fail-under=9.0
        language: system
        types: [python]
```

---

## CRONOGRAMA DE EXECUÇÃO

```
Semana 1 (Dias 1-5):
├── Dia 1-2: FASE 1 - Correções Críticas
│   ├── ethical_audit_service/api.py decomposition
│   ├── Fix import chains (4 serviços)
│   └── Pylint <8.0 → 8.5+
│
├── Dia 3-4: FASE 2 - Correções Importantes
│   ├── maximus_core_service (top 10 files)
│   ├── reactive_fabric_core (top 5 files)
│   └── Add future annotations (46 files)
│
└── Dia 5: FASE 2 cont.
    ├── Remove TODOs/FIXMEs
    └── Validation checkpoint

Semana 2 (Dias 6-10):
├── Dia 6-7: FASE 3 - Elevação Pylint
│   ├── Todos serviços → ≥9.0
│   └── Fix broad exceptions
│
├── Dia 8-9: FASE 3 cont.
│   ├── maximus_core_service remaining files
│   └── reactive_fabric_core remaining files
│
└── Dia 10: FASE 4 - Padronização
    ├── Import organization
    ├── Pre-commit hooks
    └── Final validation
```

---

## CRITÉRIOS DE SUCESSO

### Gate 1: Fim Fase 1
- [ ] 0 arquivos >1000 linhas
- [ ] Todos serviços Pylint ≥8.0
- [ ] ethical_audit_service modularizado

### Gate 2: Fim Fase 2
- [ ] <10 arquivos >500 linhas
- [ ] 0 arquivos missing future annotations
- [ ] <10 TODOs/FIXMEs

### Gate 3: Fim Fase 3
- [ ] Todos serviços Pylint ≥9.0
- [ ] <50 broad exceptions
- [ ] Type hints 100%

### Gate 4: Fim Fase 4 (FINAL)
- [ ] **0 arquivos >500 linhas**
- [ ] **0 missing future annotations**
- [ ] **0 TODOs/FIXMEs**
- [ ] **Todos serviços Pylint ≥9.0**
- [ ] **Import organization 100%**
- [ ] **Pre-commit hooks ativos**

---

## ARQUIVOS CRÍTICOS PARA MODIFICAÇÃO

### Fase 1 (Must Fix)
```
/backend/services/ethical_audit_service/api.py (2770 lines)
/backend/services/reactive_fabric_core/hitl/hitl_backend.py (942 lines)
/backend/services/reactive_fabric_core/hitl/hitl_engine.py (858 lines)
/backend/services/reactive_fabric_core/response/response_orchestrator.py (809 lines)
/backend/services/digital_thalamus_service/config.py (CRIAR)
/backend/services/prefrontal_cortex_service/config.py (CRIAR)
/backend/services/hcl_planner_service/config.py (CRIAR)
```

### Fase 2 (Important)
```
/backend/services/maximus_core_service/fairness/monitor.py (580 lines)
/backend/services/maximus_core_service/governance/base.py (576 lines)
/backend/services/maximus_core_service/hitl/audit_trail.py (572 lines)
/backend/services/maximus_core_service/validate_regra_de_ouro.py (11 TODOs)
/backend/services/maximus_core_service/governance/guardian/article_ii_guardian.py (9 TODOs)
```

### Fase 3 (Quality)
```
Todos os 14 serviços - elevação Pylint
```

---

## MÉTRICAS DE ACOMPANHAMENTO

```bash
# Script de validação (rodar diariamente)
#!/bin/bash
echo "=== CODE_CONSTITUTION COMPLIANCE ==="

echo -n "Files >500 lines: "
find backend/services -name "*.py" -exec wc -l {} \; | awk '$1>500' | wc -l

echo -n "Missing future annotations: "
find backend/services -name "*.py" -type f | while read f; do
  if [ -s "$f" ] && ! grep -q "from __future__ import annotations" "$f"; then
    echo "1"
  fi
done | wc -l

echo -n "TODOs/FIXMEs: "
grep -rn "# TODO\|# FIXME\|# HACK" backend/services --include="*.py" | wc -l

echo "=== PYLINT SCORES ==="
for svc in api_gateway digital_thalamus_service episodic_memory ethical_audit_service \
           hcl_analyzer_service hcl_executor_service hcl_monitor_service hcl_planner_service \
           maximus_core_service metacognitive_reflector meta_orchestrator \
           prefrontal_cortex_service reactive_fabric_core; do
  score=$(python -m pylint backend/services/$svc --exit-zero 2>&1 | tail -1 | grep -oP '\d+\.\d+')
  echo "$svc: $score"
done
```

---

## NOTA DE IMPLEMENTAÇÃO

Após aprovação deste plano, copiar para:
```
/media/juan/DATA/projetos/PROJETO-MAXIMUS-AGENTIC/docs/refino-final-inicial.md
```

---

**Aprovado por:** ___________________ (Juan Carlos de Souza)
**Data:** ___________________
**Status:** AGUARDANDO APROVAÇÃO

---

*"The only doctrine that shapes our architecture is the one present in CODE_CONSTITUTION."*
*- Constituição Vértice v3.0, Artigo I, Cláusula 3.6*
