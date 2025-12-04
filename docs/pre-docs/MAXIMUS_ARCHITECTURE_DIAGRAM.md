# Maximus 2.0 - Complete Architecture Diagram
> Baseado em auditoria completa do código fonte (não README)
> Data: 2025-12-01

## Sistema Completo

```mermaid
graph TB
    %% External Entry Point
    CLIENT[("🌐 External Client")]
    
    %% === LAYER 1: GATEWAY ===
    subgraph GATEWAY["🚪 Gateway Layer"]
        API_GW["API Gateway<br/>Port: 8000<br/>─────<br/>Routes: /{service}/{path}"]
        THALAMUS["Digital Thalamus<br/>Port: 8003<br/>─────<br/>RequestRouter<br/>ServiceProxy"]
    end
    
    %% === LAYER 2: COGNITIVE CORE ===
    subgraph COGNITIVE["🧠 Cognitive Core"]
        MAXIMUS_CORE["Maximus Core Service<br/>Port: 8000<br/>─────<br/>System Coordination"]
        PREFRONTAL["Prefrontal Cortex<br/>Port: 8004<br/>─────<br/>Executive Functions"]
        META_ORCH["Meta Orchestrator<br/>Port: 8100<br/>─────<br/>POST /v1/missions<br/>GET /v1/agents<br/>GET /v1/agents/health/all<br/>─────<br/>AgenticOrchestrator<br/>AgentRegistry<br/>TaskDecomposer"]
    end
    
    %% === LAYER 3: HCL HOMEOSTATIC LOOP ===
    subgraph HCL["⚡ HCL - Homeostatic Control Loop"]
        HCL_MONITOR["HCL Monitor<br/>Port: 8001<br/>─────<br/>GET /health<br/>GET /metrics<br/>GET /metrics/latest<br/>POST /collect/trigger<br/>─────<br/>CollectorManager<br/>psutil/pynvml"]
        HCL_ANALYZER["HCL Analyzer<br/>Port: 8002<br/>─────<br/>POST /train/sarima/{metric}<br/>GET /predict/sarima/{metric}<br/>POST /train/isolation_forest<br/>GET /models/status<br/>─────<br/>SARIMA/IsolationForest/XGBoost<br/>AnalysisEngine"]
        HCL_PLANNER["HCL Planner<br/>Port: 8000<br/>─────<br/>POST /plan<br/>GET /health<br/>GET /metrics<br/>─────<br/>AgenticPlanner<br/>GeminiClient<br/>ActionCatalog"]
        HCL_EXECUTOR["HCL Executor<br/>Port: 8001<br/>─────<br/>POST /v1/execute<br/>GET /v1/status<br/>─────<br/>ActionExecutor<br/>KubernetesController"]
    end
    
    %% === LAYER 4: MEMORY & REFLECTION ===
    subgraph MEMORY["💾 Memory & Meta-Cognition"]
        EPISODIC["Episodic Memory<br/>Port: 8005<br/>─────<br/>POST /v1/memories<br/>POST /v1/memories/search<br/>GET /v1/memories/{id}<br/>DELETE /v1/memories/{id}<br/>─────<br/>Vector DB (ChromaDB)<br/>Embeddings"]
        REFLECTOR["Metacognitive Reflector<br/>Port: 8002<br/>─────<br/>POST /v1/reflect<br/>GET /health<br/>─────<br/>Reflector (Triad)<br/>MemoryClient<br/>PunishmentProtocol"]
    end
    
    %% === LAYER 5: SECURITY & MONITORING ===
    subgraph SECURITY["🛡️ Security & Ethics"]
        ETHICAL["Ethical Audit<br/>Port: 8006<br/>─────<br/>Ethics Validation"]
        REACTIVE["Reactive Fabric<br/>Port: 8600<br/>─────<br/>GET /api/v1/honeypots<br/>GET /api/v1/attacks/recent<br/>GET /api/v1/ttps/top<br/>POST /api/v1/honeypots/{id}/restart<br/>─────<br/>PostgreSQL<br/>Kafka<br/>Docker API"]
    end
    
    %% === LAYER 6: SHARED INFRASTRUCTURE ===
    subgraph INFRA["🔧 Shared Infrastructure"]
        SHARED_CLIENT["ReflectorClient<br/>─────<br/>submit_log()<br/>handle_punishment()"]
    end
    
    %% === CLIENT CONNECTIONS ===
    CLIENT --> API_GW
    CLIENT --> THALAMUS
    
    %% === GATEWAY ROUTING ===
    API_GW -."{service}/{path}".-> MAXIMUS_CORE
    API_GW -."{service}/{path}".-> META_ORCH
    
    THALAMUS -."Route: /v1/core".-> MAXIMUS_CORE
    THALAMUS -."Route: /v1/hcl/planner".-> HCL_PLANNER
    THALAMUS -."Route: /v1/hcl/executor".-> HCL_EXECUTOR
    THALAMUS -."Route: /v1/hcl/analyzer".-> HCL_ANALYZER
    THALAMUS -."Route: /v1/hcl/monitor".-> HCL_MONITOR
    
    %% === COGNITIVE ORCHESTRATION ===
    META_ORCH -->|"execute_mission()<br/>ROMA decomposition"| HCL_PLANNER
    META_ORCH -->|"execute_mission()"| HCL_EXECUTOR
    META_ORCH -->|"Health checks"| HCL_MONITOR
    
    MAXIMUS_CORE <--> PREFRONTAL
    PREFRONTAL --> META_ORCH
    
    %% === HCL WORKFLOW ===
    HCL_MONITOR -->|"Metrics<br/>(15s interval)"| HCL_ANALYZER
    HCL_ANALYZER -->|"Predictions<br/>Anomalies"| HCL_PLANNER
    HCL_PLANNER -->|"Plan<br/>{plan_id, actions}"| HCL_EXECUTOR
    HCL_EXECUTOR -->|"Results<br/>ActionResult[]"| HCL_PLANNER
    HCL_EXECUTOR -.->|"K8s API<br/>(scale/update/restart)"| K8S[("☸️ Kubernetes")]
    
    %% === REFLECTION INTEGRATION (NEW) ===
    HCL_PLANNER -.->|"HTTP POST /v1/reflect<br/>ExecutionLog"| REFLECTOR
    HCL_EXECUTOR -.->|"HTTP POST /v1/reflect<br/>ExecutionLog"| REFLECTOR
    REFLECTOR -.->|"ReflectionResponse<br/>(critique + punishment)"| HCL_PLANNER
    REFLECTOR -.->|"ReflectionResponse"| HCL_EXECUTOR
    
    HCL_PLANNER --> SHARED_CLIENT
    HCL_EXECUTOR --> SHARED_CLIENT
    SHARED_CLIENT -->|"submit_log()"| REFLECTOR
    
    %% === MEMORY INTERACTIONS ===
    META_ORCH <-->|"Store/Recall<br/>Embeddings"| EPISODIC
    REFLECTOR -->|"apply_updates()<br/>MemoryUpdate[]"| EPISODIC
    
    %% === SECURITY MONITORING ===
    REACTIVE -->|"ThreatDetectedMessage<br/>(Kafka)"| MAXIMUS_CORE
    REACTIVE -->|"HoneypotStatusMessage"| HCL_MONITOR
    ETHICAL -.->|"Ethics Validation"| META_ORCH
    
    %% === DATA PERSISTENCE ===
    HCL_MONITOR -.->|"Metrics Storage"| PG_DB[("🗄️ PostgreSQL")]
    HCL_ANALYZER -.->|"Query Historical"| PG_DB
    REACTIVE -->|"Attacks/TTPs/IOCs"| PG_DB
    EPISODIC -->|"Vector Storage"| VECTOR_DB[("🔍 ChromaDB")]
    
    %% === MESSAGE QUEUES ===
    HCL_ANALYZER -.->|"Publish Predictions"| KAFKA[("📨 Kafka")]
    REACTIVE -->|"Publish Threats"| KAFKA
    HCL_MONITOR -.->|"Optional Streaming"| KAFKA
    
    %% === EXTERNAL DEPENDENCIES ===
    HCL_PLANNER -.->|"generate_plan()<br/>High Thinking Mode"| GEMINI[("🤖 Gemini 3 Pro API")]
    
    %% STYLING
    classDef gateway fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    classDef cognitive fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef hcl fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef memory fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef security fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef infra fill:#fafafa,stroke:#616161,stroke-width:2px
    classDef external fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    
    class API_GW,THALAMUS gateway
    class MAXIMUS_CORE,PREFRONTAL,META_ORCH cognitive
    class HCL_MONITOR,HCL_ANALYZER,HCL_PLANNER,HCL_EXECUTOR hcl
    class EPISODIC,REFLECTOR memory
    class ETHICAL,REACTIVE security
    class SHARED_CLIENT infra
    class CLIENT,K8S,PG_DB,VECTOR_DB,KAFKA,GEMINI external
```

## Fluxo de Dados Detalhado

### 1. HCL Loop Completo
```
Monitor (15s) → Collect Metrics → PostgreSQL
              ↓
Analyzer ← Fetch Historical → Train Models (SARIMA/IF/XGBoost)
              ↓
         Predictions → Planner (Gemini 3 Pro) → Actions
              ↓
         Executor → K8s API (scale/update/restart)
              ↓
         Results → Reflector (Triad Check)
```

### 2. Reflection Workflow (NEW Integration)
```
Planner.recommend_actions() → ExecutionLog → HTTP POST /v1/reflect
                                                      ↓
                                            Reflector.analyze_log()
                                                      ↓
                                            Triad (Truth/Wisdom/Justice)
                                                      ↓
                                            OffenseLevel → Punishment
                                                      ↓
                                            MemoryUpdates → EpisodicMemory
                                                      ↓
                                       ReflectionResponse ← HTTP 200
```

### 3. Meta-Orchestrator Mission
```
POST /v1/missions → TaskDecomposer (ROMA) → Subtasks
                                                  ↓
                                    AgentRegistry.route_task()
                                                  ↓
                          ┌─────────────┬──────────────┬────────────┐
                          ↓             ↓              ↓            ↓
                    HCL Planner   HCL Executor   HCL Monitor   Memory
                          ↓             ↓              ↓            ↓
                          └─────────────┴──────────────┴────────────┘
                                                  ↓
                                    Synthesize Results → Response
```

## Endpoints Resumo (Código Real)

| Service | Port | Endpoints Principais |
|---------|------|----------------------|
| **API Gateway** | 8000 | `/{service}/{path}` (proxy), `/health` |
| **Digital Thalamus** | 8003 | Routes to all services |
| **Meta Orchestrator** | 8100 | `POST /v1/missions`, `GET /v1/agents`, `GET /v1/agents/health/all` |
| **HCL Monitor** | 8001 | `/health`, `/metrics`, `/metrics/latest`, `POST /collect/trigger` |
| **HCL Analyzer** | 8002 | `POST /train/sarima/{metric}`, `GET /predict/sarima/{metric}`, `/models/status` |
| **HCL Planner** | 8000 | `POST /plan`, `/health`, `/metrics` |
| **HCL Executor** | 8001 | `POST /v1/execute`, `GET /v1/status` |
| **Metacognitive Reflector** | 8002 | `POST /v1/reflect`, `/health` |
| **Episodic Memory** | 8005 | `POST /v1/memories`, `POST /v1/memories/search`, `GET /v1/memories/{id}`, `DELETE /v1/memories/{id}` |
| **Reactive Fabric** | 8600 | `/api/v1/honeypots`, `/api/v1/attacks/recent`, `/api/v1/ttps/top`, `POST /api/v1/honeypots/{id}/restart` |
| **Maximus Core** | 8000 | `/v1/*` (coordination) |
| **Prefrontal Cortex** | 8004 | `/v1/*` (executive functions) |
| **Ethical Audit** | 8006 | Ethics validation |

## Classes Principais (Código Real)

| Service | Core Classes |
|---------|--------------|
| **Meta Orchestrator** | `Orchestrator`, `AgentRegistry`, `TaskDecomposer` |
| **HCL Planner** | `AgenticPlanner`, `GeminiClient`, `ActionCatalog` |
| **HCL Executor** | `ActionExecutor`, `KubernetesController` |
| **HCL Analyzer** | `AnalysisEngine`, `ModelRegistry` (SARIMA, IsolationForest, XGBoost) |
| **HCL Monitor** | `CollectorManager` (psutil, pynvml) |
| **Reflector** | `Reflector`, `MemoryClient`, `PhilosophicalCheck` |
| **Digital Thalamus** | `RequestRouter`, `ServiceProxy` |
| **Episodic Memory** | Vector DB client (ChromaDB) |
| **Reactive Fabric** | Database layer (asyncpg), Kafka producer (aiokafka) |
| **Shared** | `ReflectorClient` (shared utility) |

## Dependências Externas

- **Gemini 3 Pro API**: HCL Planner (thinking mode)
- **Kubernetes API**: HCL Executor (deployments, pods, resources)
- **PostgreSQL**: HCL Monitor, Reactive Fabric
- **ChromaDB**: Episodic Memory (vectors)
- **Kafka**: HCL Analyzer, Reactive Fabric (streaming)
- **Docker API**: Reactive Fabric (honeypot health)

## Status da Integração

✅ **COMPLETO**:
- HCL Loop (Monitor → Analyzer → Planner → Executor)
- Reflection Integration (Planner + Executor → Reflector)
- Meta Orchestrator (ROMA decomposition)
- Episodic Memory (store/recall)
- Reactive Fabric (threat detection)

⏸️ **PENDENTE**:
- Gemini 3 Pro real API calls (placeholder logic exists)
- Kubernetes real deployment (mock K8s controller)
- Kafka real streaming (optional enabled)
- Full MIRIX memory integration (6 types)
