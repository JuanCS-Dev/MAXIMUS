# PLANO DE REFATORAÇÃO MAXIMUS 2.0
## Auditoria de Qualidade - Dezembro 2025

---

## SUMÁRIO EXECUTIVO

| Prioridade | Tarefa | Escopo | Esforço |
|------------|--------|--------|---------|
| **ALTA** | Substituir print por logging | 204 arquivos, ~4.500 prints | Alto |
| **ALTA** | Decompor arquivos >500 linhas | 31 arquivos | Alto |
| **ALTA** | Adicionar future annotations | 37 arquivos | Baixo |
| **MÉDIA** | Refatorar funções complexas | 15 funções | Médio |
| **MÉDIA** | Criar CHANGELOG.md | 12 serviços | Baixo |
| **MÉDIA** | Aumentar type hints | ~1.134 funções | Médio |
| **BAIXA** | Padronizar Pydantic/dataclass | Auditoria | Baixo |
| **BAIXA** | Criar Dockerfiles | 3 serviços | Baixo |

---

## FASE 1: SUBSTITUIR PRINT POR LOGGING

### 1.1 Escopo Total
- **204 arquivos** com print statements
- **~4.500+ prints** a migrar
- **11 serviços** afetados

### 1.2 Distribuição por Serviço

| Serviço | Arquivos | Prints | Prioridade |
|---------|----------|--------|------------|
| maximus_core_service | 173 | ~3.100 | CRÍTICA |
| reactive_fabric_core | 6 | ~200 | ALTA |
| metacognitive_reflector | 5 | ~150 | MÉDIA |
| hcl_planner_service | 5 | ~120 | MÉDIA |
| prefrontal_cortex_service | 4 | ~100 | MÉDIA |
| digital_thalamus_service | 4 | ~80 | BAIXA |
| hcl_analyzer_service | 2 | ~50 | BAIXA |
| ethical_audit_service | 2 | ~40 | BAIXA |
| outros | 3 | ~20 | BAIXA |

### 1.3 Arquivos Prioritários (TOP 10)

1. `maximus_core_service/examples/02_autonomous_training_workflow.py` - 143 prints
2. `maximus_core_service/_demonstration/example_neuromodulation.py` - 143 prints
3. `maximus_core_service/_demonstration/example_neuromodulation_standalone.py` - 135 prints
4. `maximus_core_service/examples/03_performance_optimization_pipeline.py` - 131 prints
5. `maximus_core_service/test_osint_workflows.py` - 130 prints
6. `maximus_core_service/test_maximus_ethical_integration.py` - 129 prints
7. `maximus_core_service/tests/integration/consciousness/test_performance_optimization.py` - 117 prints
8. `maximus_core_service/_demonstration/example_predictive_coding_usage.py` - 117 prints
9. `maximus_core_service/compliance/example_usage.py` - 117 prints
10. `maximus_core_service/_demonstration/demo_ethical_ai_complete.py` - 114 prints

### 1.4 Mapeamento Print → Logging Level

| Padrão de Print | Logging Level | Exemplo |
|-----------------|---------------|---------|
| `print("=" * 80)` (separadores) | `logger.info` | Cabeçalhos de seção |
| `print(f"✅ ...")` (sucesso) | `logger.info` | Status de conclusão |
| `print(f"❌ ERROR: ...")` | `logger.error` | Erros e falhas |
| `print(f"⚠️ ...")` | `logger.warning` | Avisos |
| `print(f"Value: {x}")` (debug) | `logger.debug` | Valores diagnósticos |
| `print(f"Step {n}: ...")` | `logger.info` | Progresso de workflow |

### 1.5 Arquivos com Logger já Configurado (GANHOS RÁPIDOS)

Estes 15 arquivos JÁ têm logger mas ainda usam print:

1. `test_maximus_ethical_integration.py` - 129 prints
2. `examples/01_ethical_decision_pipeline.py` - 88 prints
3. `autonomic_core/test_hcl_integration.py` - 53 prints
4. `attention_system/test_attention_integration.py` - 51 prints
5. `scripts/coverage_commander.py` - 31 prints
6. `training/evaluator.py` - 20 prints
7. `performance/profiler.py` - 18 prints
8. `performance/benchmark_suite/suite.py` - 18 prints
9. `performance/pruner.py` - 16 prints
10. `performance/onnx_exporter.py` - 16 prints

### 1.6 Template de Logger Padrão

```python
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Substituir:
# print(f"Processing {item}...")
# Por:
logger.info("Processing %s...", item)

# Substituir:
# print(f"Error: {e}")
# Por:
logger.error("Error: %s", e)

# Substituir:
# print(f"Value: {value}")
# Por:
logger.debug("Value: %s", value)
```

### 1.7 Execução por Fases

**Fase 1A: Ganhos Rápidos (15 arquivos)**
- Arquivos que já têm logger configurado
- Apenas substituir print → logger.level

**Fase 1B: Core Modules (consciousness/, safety/, governance/)**
- Configurar logger se não existir
- Migrar prints

**Fase 1C: Examples e Demonstrations**
- Converter TODOS para logging (decisão do usuário)

**Fase 1D: Restante dos Serviços**
- reactive_fabric_core, metacognitive_reflector, etc.

---

## FASE 2: DECOMPOR ARQUIVOS >500 LINHAS

### 2.1 Lista Completa (31 arquivos)

| # | Arquivo | Linhas | Classes Principais |
|---|---------|--------|-------------------|
| 1 | fairness/monitor.py | 580 | FairnessMonitor |
| 2 | governance/base.py | 576 | Policy, ERBMember, AuditLog |
| 3 | hitl/audit_trail.py | 572 | AuditTrail, AuditQuery |
| 4 | performance/pruner.py | 568 | ModelPruner |
| 5 | hitl/risk_assessor.py | 568 | RiskAssessor, RiskFactors |
| 6 | hitl/decision_framework.py | 565 | HITLDecisionFramework |
| 7 | governance/guardian/article_ii_guardian.py | 563 | ArticleIIGuardian |
| 8 | compliance/certifications.py | 561 | ISO27001Checker, SOC2Checker |
| 9 | performance/onnx_exporter.py | 557 | ONNXExporter |
| 10 | performance/batch_predictor.py | 557 | BatchPredictor |
| 11 | hitl/decision_queue.py | 553 | DecisionQueue |
| 12 | federated_learning/storage.py | 552 | Storage management |
| 13 | training/data_collection.py | 550 | DataCollector |
| 14 | compliance/gap_analyzer.py | 549 | Gap analysis |
| 15 | training/layer_trainer.py | 549 | Layer training |
| 16 | governance/audit_infrastructure.py | 545 | Audit system |
| 17 | training/dataset_builder.py | 540 | Dataset building |
| 18 | governance_sse/sse_server.py | 540 | SSE server |
| 19 | compliance/base.py | 527 | Base compliance |
| 20 | hitl/base.py | 516 | HITL data structures |
| 21 | autonomic_core/hcl_orchestrator.py | 512 | HCL orchestration |
| 22 | training/evaluator.py | 511 | Model evaluation |
| 23 | federated_learning/fl_coordinator.py | 510 | FL coordination |
| 24 | performance/distributed_trainer.py | 507 | Distributed training |
| 25 | hitl/escalation_manager.py | 506 | Escalation handling |
| 26-31 | Outros | 500-506 | Diversos |

### 2.2 Planos de Decomposição Detalhados

#### 2.2.1 fairness/monitor.py (580 linhas)

**Estrutura Proposta:**
```
fairness/monitor/
├── __init__.py          # Re-exports
├── core.py              # FairnessMonitor base (150 linhas)
├── models.py            # FairnessAlert, FairnessSnapshot (50 linhas)
├── alerts.py            # AlertManagementMixin (100 linhas)
├── trends.py            # TrendAnalysisMixin (100 linhas)
├── history.py           # HistoricalDataMixin (80 linhas)
└── evaluator.py         # ConstraintEvaluationMixin (100 linhas)
```

#### 2.2.2 governance/base.py (576 linhas)

**Estrutura Proposta:**
```
governance/
├── __init__.py
├── config.py            # GovernanceConfig (30 linhas)
├── enums.py             # PolicyType, ERBMemberRole, etc. (80 linhas)
├── policy/
│   ├── __init__.py
│   ├── models.py        # Policy, PolicyViolation (80 linhas)
│   └── enforcement.py   # PolicyEnforcementResult (40 linhas)
├── erb/
│   ├── __init__.py
│   └── models.py        # ERBMember, ERBMeeting, ERBDecision (100 linhas)
├── audit/
│   ├── __init__.py
│   └── models.py        # AuditLog (60 linhas)
├── whistleblower/
│   ├── __init__.py
│   └── models.py        # WhistleblowerReport (65 linhas)
└── results.py           # GovernanceResult (55 linhas)
```

#### 2.2.3 hitl/audit_trail.py (572 linhas)

**Estrutura Proposta:**
```
hitl/audit_trail/
├── __init__.py
├── core.py              # AuditTrail base (100 linhas)
├── models.py            # AuditQuery, ComplianceReport (100 linhas)
├── event_logger.py      # EventLoggingMixin (120 linhas)
├── query_engine.py      # QueryMixin (80 linhas)
├── compliance.py        # ComplianceReportingMixin (100 linhas)
├── pii.py               # PIIRedactionMixin (40 linhas)
└── storage.py           # StorageBackendMixin (30 linhas)
```

#### 2.2.4 hitl/risk_assessor.py (568 linhas)

**Estrutura Proposta:**
```
hitl/risk_assessor/
├── __init__.py
├── core.py              # RiskAssessor base (100 linhas)
├── models.py            # RiskFactors, RiskScore (140 linhas)
├── factors.py           # FactorComputationMixin (150 linhas)
├── scoring.py           # ScoreCalculationMixin (80 linhas)
├── classification.py    # ClassificationMixin (50 linhas)
├── recommendations.py   # RecommendationMixin (40 linhas)
└── constants.py         # Weights, thresholds (10 linhas)
```

#### 2.2.5 hitl/decision_framework.py (565 linhas)

**Estrutura Proposta:**
```
hitl/decision_framework/
├── __init__.py
├── core.py              # HITLDecisionFramework base (100 linhas)
├── models.py            # DecisionResult (40 linhas)
├── evaluator.py         # ActionEvaluationMixin (100 linhas)
├── automation.py        # AutomationLevelMixin (80 linhas)
├── executor.py          # ExecutionMixin (80 linhas)
├── queuing.py           # ReviewQueueingMixin (60 linhas)
├── operator.py          # OperatorIntegrationMixin (60 linhas)
└── orchestration.py     # OrchestrationMixin (45 linhas)
```

#### 2.2.6 performance/pruner.py (568 linhas)

**Estrutura Proposta:**
```
performance/pruner/
├── __init__.py
├── core.py              # ModelPruner base (80 linhas)
├── models.py            # PruningConfig, PruningResult (80 linhas)
├── strategies/
│   ├── __init__.py
│   ├── unstructured.py  # UnstructuredPruningMixin (80 linhas)
│   └── structured.py    # StructuredPruningMixin (80 linhas)
├── fine_tuning.py       # FineTuningMixin (60 linhas)
├── analysis.py          # AnalysisMixin (60 linhas)
├── persistence.py       # PersistenceMixin (40 linhas)
└── scheduling.py        # SchedulingMixin (80 linhas)
```

### 2.3 Ordem de Execução

**Batch 1: HITL (5 arquivos)**
1. hitl/audit_trail.py
2. hitl/risk_assessor.py
3. hitl/decision_framework.py
4. hitl/decision_queue.py
5. hitl/escalation_manager.py

**Batch 2: Governance (4 arquivos)**
6. governance/base.py
7. governance/guardian/article_ii_guardian.py
8. governance/audit_infrastructure.py
9. governance_sse/sse_server.py

**Batch 3: Performance (5 arquivos)**
10. performance/pruner.py
11. performance/onnx_exporter.py
12. performance/batch_predictor.py
13. performance/distributed_trainer.py

**Batch 4: Training (4 arquivos)**
14. training/data_collection.py
15. training/layer_trainer.py
16. training/dataset_builder.py
17. training/evaluator.py

**Batch 5: Compliance & Fairness (4 arquivos)**
18. compliance/certifications.py
19. compliance/gap_analyzer.py
20. compliance/base.py
21. fairness/monitor.py

**Batch 6: Federated Learning & HCL (3 arquivos)**
22. federated_learning/storage.py
23. federated_learning/fl_coordinator.py
24. autonomic_core/hcl_orchestrator.py

**Batch 7: Restantes (7 arquivos)**
25-31. hitl/base.py e outros

### 2.4 Checklist de Validação por Arquivo

Para cada decomposição:
- [ ] Criar diretório do pacote
- [ ] Criar `__init__.py` com re-exports
- [ ] Criar módulos separados
- [ ] Manter type hints 100%
- [ ] Manter docstrings
- [ ] Verificar imports circulares
- [ ] Renomear original para `*_legacy.py`
- [ ] Testar imports: `python -c "from package import Class"`
- [ ] Rodar pylint no pacote

---

## FASE 3: ADICIONAR FUTURE ANNOTATIONS

### 3.1 Lista de Arquivos (37 arquivos ativos)

**api_gateway/ (8 arquivos)**
```
backend/services/api_gateway/__init__.py
backend/services/api_gateway/main.py
backend/services/api_gateway/api/__init__.py
backend/services/api_gateway/api/routes.py
backend/services/api_gateway/core/__init__.py
backend/services/api_gateway/core/proxy.py
backend/services/api_gateway/tests/test_api.py
backend/services/api_gateway/tests/test_proxy.py
```

**hcl_executor_service/ (16 arquivos)**
```
backend/services/hcl_executor_service/__init__.py
backend/services/hcl_executor_service/main.py
backend/services/hcl_executor_service/config.py
backend/services/hcl_executor_service/api/__init__.py
backend/services/hcl_executor_service/api/dependencies.py
backend/services/hcl_executor_service/api/routes.py
backend/services/hcl_executor_service/core/__init__.py
backend/services/hcl_executor_service/core/executor.py
backend/services/hcl_executor_service/core/k8s.py
backend/services/hcl_executor_service/models/__init__.py
backend/services/hcl_executor_service/models/actions.py
backend/services/hcl_executor_service/utils/logging_config.py
backend/services/hcl_executor_service/tests/__init__.py
backend/services/hcl_executor_service/tests/test_api.py
backend/services/hcl_executor_service/tests/test_executor.py
backend/services/hcl_executor_service/tests/test_k8s.py
```

**hcl_monitor_service/ (13 arquivos)**
```
backend/services/hcl_monitor_service/__init__.py
backend/services/hcl_monitor_service/main.py
backend/services/hcl_monitor_service/config.py
backend/services/hcl_monitor_service/api/__init__.py
backend/services/hcl_monitor_service/api/dependencies.py
backend/services/hcl_monitor_service/api/routes.py
backend/services/hcl_monitor_service/core/__init__.py
backend/services/hcl_monitor_service/core/collector.py
backend/services/hcl_monitor_service/models/__init__.py
backend/services/hcl_monitor_service/models/metrics.py
backend/services/hcl_monitor_service/utils/__init__.py
backend/services/hcl_monitor_service/utils/logging_config.py
backend/services/hcl_monitor_service/tests/__init__.py
```

### 3.2 Comando de Execução

Para cada arquivo, adicionar na primeira linha (após shebang se houver):
```python
from __future__ import annotations
```

---

## FASE 4: REFATORAR FUNÇÕES COMPLEXAS

### 4.1 Lista das 15 Funções Mais Complexas

| # | Função | Arquivo | Complexidade | Linhas |
|---|--------|---------|--------------|--------|
| 1 | `_check_file` | governance/guardian/article_ii_guardian.py | 14 | 122 |
| 2 | `evaluate` | metacognitive_reflector/core/judges/veritas.py | 12 | 117 |
| 3 | `detect_drift` | fairness/monitor.py | 11 | 88 |
| 4 | `scan_pull_request` | governance/guardian/article_ii_guardian.py | 11 | 80 |
| 5 | `_check_authentication` | governance/guardian/article_iii_guardian/checkers.py | 10 | 59 |
| 6 | `_check_audit_trails` | governance/guardian/article_iii_guardian/checkers.py | 10 | 62 |
| 7 | `get_fairness_trends` | fairness/monitor.py | 9 | 69 |
| 8 | `_check_input_validation` | governance/guardian/article_iii_guardian/checkers.py | 9 | 58 |
| 9 | `_check_git_status` | governance/guardian/article_ii_guardian.py | 8 | 54 |
| 10 | `evaluate_fairness` | fairness/monitor.py | 7 | 66 |
| 11 | `intervene` | governance/guardian/article_ii_guardian.py | 7 | 41 |
| 12 | `analyze_violation` | governance/guardian/article_ii_guardian.py | 6 | 35 |
| 13 | `monitor` | governance/guardian/article_ii_guardian.py | 6 | 29 |
| 14 | `__init__` (EthicalAuditDatabase) | ethical_audit_service/database.py | 3 | 15 |
| 15 | `get_monitored_systems` | governance/guardian/article_ii_guardian.py | 1 | 8 |

### 4.2 Estratégias de Refatoração

#### 4.2.1 `_check_file` (article_ii_guardian.py) - Complexidade 14

**Problema:** 4 loops aninhados, múltiplos re.search(), parsing AST

**Solução:**
```python
# ANTES: Função monolítica de 122 linhas

# DEPOIS: Extrair métodos
class ArticleIIGuardian:
    async def _check_file(self, file_path: Path) -> list[ConstitutionalViolation]:
        violations = []
        content = file_path.read_text()
        lines = content.split('\n')

        violations.extend(self._check_mock_patterns(file_path, lines))
        violations.extend(self._check_placeholder_patterns(file_path, lines))
        violations.extend(self._check_implementation_errors(file_path, content))

        return violations

    def _check_mock_patterns(self, path: Path, lines: list[str]) -> list[ConstitutionalViolation]:
        # Lógica isolada para mocks
        ...

    def _check_placeholder_patterns(self, path: Path, lines: list[str]) -> list[ConstitutionalViolation]:
        # Lógica isolada para placeholders
        ...

    def _check_implementation_errors(self, path: Path, content: str) -> list[ConstitutionalViolation]:
        # Lógica AST isolada
        ...
```

#### 4.2.2 `evaluate` (veritas.py) - Complexidade 12

**Problema:** 8 branches condicionais, async/await aninhados

**Solução:**
```python
# Extrair métodos:
async def evaluate(self, claims: list[Claim]) -> Verdict:
    processed_claims = await self._process_claims(claims)
    evidence = await self._gather_evidence(processed_claims)
    results = await self._aggregate_results(evidence)
    return self._determine_verdict(results)
```

#### 4.2.3 `detect_drift` (monitor.py) - Complexidade 11

**Problema:** Comparação de janelas duplas, 4 níveis de severidade

**Solução:**
```python
# Extrair para classe dedicada
class DriftAnalyzer:
    def detect_drift(self, history: list[Snapshot], window: int) -> dict:
        recent, baseline = self._split_windows(history, window)
        drift_results = {}

        for metric in self._get_metrics(recent):
            drift = self._calculate_drift_for_metric(metric, recent, baseline)
            if drift:
                drift_results[metric] = drift

        return drift_results
```

### 4.3 Ordem de Refatoração

1. **Primeiro:** Funções em `article_ii_guardian.py` (5 funções, mesmo arquivo)
2. **Segundo:** Funções em `fairness/monitor.py` (3 funções)
3. **Terceiro:** Funções em `article_iii_guardian/checkers.py` (3 funções)
4. **Quarto:** `evaluate` em `veritas.py` (1 função)
5. **Quinto:** Restantes (3 funções)

---

## FASE 5: CRIAR CHANGELOG.md

### 5.1 Serviços Necessitando CHANGELOG (12)

1. api_gateway
2. digital_thalamus_service
3. episodic_memory
4. ethical_audit_service
5. hcl_analyzer_service
6. hcl_executor_service
7. hcl_monitor_service
8. hcl_planner_service
9. metacognitive_reflector
10. meta_orchestrator
11. prefrontal_cortex_service
12. reactive_fabric_core

### 5.2 Template de CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial service implementation

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [1.0.0] - 2025-12-03

### Added
- Initial release of {SERVICE_NAME}
- Core functionality implementation
- API endpoints
- Unit tests
- Integration tests
- Docker support
```

---

## FASE 6: AUMENTAR TYPE HINTS

### 6.1 Escopo

- **Atual:** 77.6% das funções com return type hints
- **Meta:** >90%
- **Funções a adicionar:** ~1.134

### 6.2 Estratégia

1. Usar `mypy --strict` para identificar funções sem hints
2. Priorizar arquivos core (não examples/tests)
3. Usar `Any` apenas quando necessário
4. Preferir tipos específicos (`list[str]` vs `List`)

### 6.3 Comando de Verificação

```bash
python -m mypy backend/services/SERVICE_NAME --ignore-missing-imports --show-error-codes | grep "missing return type"
```

---

## FASE 7: PADRONIZAR PYDANTIC VS DATACLASS

### 7.1 Contagem Atual

- **Pydantic BaseModel:** 217 classes
- **@dataclass:** 286 classes

### 7.2 Regra de Padronização

| Caso de Uso | Usar |
|-------------|------|
| API request/response | Pydantic BaseModel |
| Validação de entrada | Pydantic BaseModel |
| Configuração | Pydantic BaseSettings |
| Dados internos simples | @dataclass |
| DTOs entre módulos | @dataclass |
| Imutáveis | @dataclass(frozen=True) |

### 7.3 Ação

- **Não migrar em massa** - muito risco
- Documentar padrão no CODE_CONSTITUTION
- Aplicar em novos códigos

---

## FASE 8: CRIAR DOCKERFILES

### 8.1 Serviços Faltando (3)

1. **api_gateway**
2. **episodic_memory**
3. **metacognitive_reflector**

### 8.2 Template de Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## MODO DE EXECUÇÃO

### Decisões do Usuário
- **Ordem:** Seguir prioridade do plano (Alta → Média → Baixa)
- **Prints em examples:** Converter TODOS para logging (100%)
- **Execução:** Sprint por fase (pausar entre fases para revisão)

### Sprints de Execução

| Sprint | Fase | Escopo | Checkpoint |
|--------|------|--------|------------|
| **Sprint 1** | Fase 1 | Print→Logging (204 arquivos, ~4.500 prints) | ⏸️ Revisão |
| **Sprint 2** | Fase 2 | Decomposição (31 arquivos >500 linhas) | ⏸️ Revisão |
| **Sprint 3** | Fase 3 | Future annotations (37 arquivos) | ⏸️ Revisão |
| **Sprint 4** | Fase 4 | Funções complexas (15 funções) | ⏸️ Revisão |
| **Sprint 5** | Fase 5 | CHANGELOG.md (12 serviços) | ⏸️ Revisão |
| **Sprint 6** | Fase 6 | Type hints (+1.134 funções) | ⏸️ Revisão |
| **Sprint 7** | Fase 7 | Padronização Pydantic/dataclass | ⏸️ Revisão |
| **Sprint 8** | Fase 8 | Dockerfiles (3 serviços) | ✅ Completo |

---

## MÉTRICAS DE SUCESSO

| Métrica | Antes | Meta |
|---------|-------|------|
| Arquivos >500 linhas | 31 | 0 |
| Print statements | ~4.500 | 0 (em código de produção) |
| Future annotations | 98.3% | 100% |
| Type hints (return) | 77.6% | >90% |
| Funções complexas (>15) | 121 | <20 |
| CHANGELOG.md | 1/13 | 13/13 |
| Dockerfile | 10/13 | 13/13 |
| Pylint score | 8.07 | >9.0 |

---

## NOTAS PARA EXECUÇÃO

1. **Sempre rodar testes** após cada batch de mudanças
2. **Commitar frequentemente** com mensagens descritivas
3. **Verificar imports** após decomposições
4. **Manter backward compatibility** nos `__init__.py`
5. **Documentar decisões** em comentários quando necessário
