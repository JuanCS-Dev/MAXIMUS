# Maximus 2.0 - Architecture V3 (Phase 2 Optimized)
> **Date**: December 1, 2025
> **Status**: Production Ready

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#f0f4f8', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#e2e8f0'}}}%%
graph TB
    %% ================= STYLING DEFINITIONS =================
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px,color:#333,rx:5,ry:5;
    
    classDef gatewayLayer fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef gatewayNode fill:#bbdefb,stroke:#1976d2,color:#0d47a1,rx:8,ry:8;
    
    classDef cognitiveLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef cognitiveNode fill:#ffe0b2,stroke:#f57c00,color:#e65100,rx:8,ry:8;
    
    classDef hclLayer fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;
    classDef hclNode fill:#c8e6c9,stroke:#388e3c,color:#1b5e20,rx:8,ry:8;
    
    classDef memoryLayer fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px,color:#4a148c;
    classDef memoryNode fill:#e1bee7,stroke:#8e24aa,color:#4a148c,rx:8,ry:8;
    
    classDef securityLayer fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c;
    classDef securityNode fill:#ffcdd2,stroke:#d32f2f,color:#b71c1c,rx:8,ry:8;
    
    classDef infraLayer fill:#f5f5f5,stroke:#424242,stroke-width:2px,color:#212121;
    classDef infraNode fill:#e0e0e0,stroke:#616161,color:#212121,rx:8,ry:8;
    
    classDef externalNode fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,stroke-dasharray: 5 5,color:#f57f17,rx:15,ry:15;

    %% ================= EXTERNAL ENTRY =================
    CLIENT[("🌐 External Client<br/>(User/System)")]:::externalNode

    %% ================= LAYER 1: GATEWAY =================
    subgraph GATEWAY ["🚪 LAYER 1: GATEWAY & ROUTING"]
        API_GW["🐙 API Gateway<br/>(Port: 8000)<br/>Routes: /{service}/{path}"]:::gatewayNode
        THALAMUS["🔀 Digital Thalamus<br/>(Port: 8003)<br/>RequestRouter, ServiceProxy"]:::gatewayNode
    end
    class GATEWAY gatewayLayer

    %% ================= LAYER 2: COGNITIVE CORE =================
    subgraph COGNITIVE ["🧠 LAYER 2: COGNITIVE CORE"]
        MAXIMUS_CORE["👑 Maximus Core<br/>(Port: 8000)<br/>System Coordination"]:::cognitiveNode
        PREFRONTAL["🤔 Prefrontal Cortex<br/>(Port: 8004)<br/>Executive Functions"]:::cognitiveNode
        META_ORCH["🎻 Meta Orchestrator<br/>(Port: 8100)<br/>ROMA Decomposer<br/>SimuRA World Model 🆕"]:::cognitiveNode
    end
    class COGNITIVE cognitiveLayer

    %% ================= LAYER 5: SECURITY (Placed for layout balance) =================
    subgraph SECURITY ["🛡️ LAYER 5: SECURITY & ETHICS"]
        ETHICAL["⚖️ Ethical Audit<br/>(Port: 8006)<br/>Ethics Validation"]:::securityNode
        REACTIVE["🕵️ Reactive Fabric<br/>(Port: 8600)<br/>Honeypots, Threat Detection"]:::securityNode
    end
    class SECURITY securityLayer

    %% ================= MAIN LOGIC BLOCK (HCL & MEMORY) =================
    subgraph LOGIC_BLOCK ["MAIN OPERATIONAL LOGIC"]
        direction TB
        
        %% === LAYER 3: HCL HOMEOSTATIC LOOP ===
        subgraph HCL ["⚡ LAYER 3: HCL HOMEOSTATIC LOOP (The Engine)"]
            direction LR
            HCL_MONITOR["👀 HCL Monitor<br/>(Port: 8001)<br/>CollectorManager"]:::hclNode
            HCL_ANALYZER["🧙‍♂️ HCL Analyzer<br/>(Port: 8002)<br/>SARIMA/IF/XGBoost"]:::hclNode
            HCL_PLANNER["👷 HCL Planner<br/>(Port: 8000)<br/>Gemini 3 Pro (Deep Think) 🆕<br/>SimuRA Simulation 🆕"]:::hclNode
            HCL_EXECUTOR["🔧 HCL Executor<br/>(Port: 8001)<br/>ActionExecutor<br/>Knative Controller 🆕"]:::hclNode
        end
        class HCL hclLayer

        %% === LAYER 6: SHARED INFRASTRUCTURE (The Glue) ===
        subgraph INFRA ["🔧 LAYER 6: SHARED INFRASTRUCTURE"]
            SHARED_CLIENT["⚡ AsyncReflectorClient 🆕<br/>(Priority Queue)<br/>7x Faster"]:::infraNode
        end
        class INFRA infraLayer

        %% === LAYER 4: MEMORY & REFLECTION ===
        subgraph MEMORY ["💾 LAYER 4: MEMORY & META-COGNITION"]
            REFLECTOR["🧘 Metacognitive Reflector<br/>(Port: 8002)<br/>Triad (Truth/Wisdom/Justice)"]:::memoryNode
            EPISODIC["📚 Episodic Memory (MIRIX) 🆕<br/>(Port: 8005)<br/>6-Type Hierarchy<br/>L1/L2/L3 Caching"]:::memoryNode
        end
        class MEMORY memoryLayer
    end
    style LOGIC_BLOCK fill:none,stroke:none

    %% ================= EXTERNAL DEPENDENCIES =================
    subgraph EXTERNAL ["🔋 EXTERNAL DEPENDENCIES & PERSISTENCE"]
        GEMINI[("🤖 Gemini 3 Pro API<br/>(Adaptive Thinking)")]:::externalNode
        K8S[("☸️ Kubernetes / Knative<br/>(Serverless Infra)")]:::externalNode
        PG_DB[("🗄️ PostgreSQL<br/>(Metrics & Threats)")]:::externalNode
        QDRANT[("🚀 Qdrant Vector DB 🆕<br/>(30x Faster)")]:::externalNode
        KAFKA[("📨 Kafka<br/>(Streaming & Events)")]:::externalNode
    end


    %% ================= CONNECTIONS & FLOWS =================

    %% --- Inbound Traffic ---
    CLIENT ===>|"REST Requests"| API_GW
    CLIENT ===>|"Direct Access"| THALAMUS

    %% --- Gateway Routing ---
    API_GW -.- localRoutes1>|"Proxy"| MAXIMUS_CORE
    API_GW -.- localRoutes2>|"Proxy"| META_ORCH
    
    THALAMUS ===>|"Route"| MAXIMUS_CORE
    THALAMUS ===>|"Route"| HCL_MONITOR & HCL_ANALYZER & HCL_PLANNER & HCL_EXECUTOR

    %% --- Cognitive Coordination ---
    MAXIMUS_CORE <==>|"Sync"| PREFRONTAL
    PREFRONTAL ==>|"Executive Orders"| META_ORCH
    ETHICAL -.->|"Validate"| META_ORCH

    %% --- Orchestration Flows ---
    META_ORCH ==>|"1. Decompose & Simulate (SimuRA)"| HCL_PLANNER
    META_ORCH ==>|"2. Execute"| HCL_EXECUTOR
    META_ORCH <==>|"Context (MIRIX)"| EPISODIC

    %% --- HCL CONTROL LOOP ---
    HCL_MONITOR ==="1. Metrics"==> HCL_ANALYZER
    HCL_ANALYZER ==="2. Predictions"==> HCL_PLANNER
    HCL_PLANNER ==="3. Deep Plan (Gemini 3)"==> HCL_EXECUTOR
    HCL_EXECUTOR ==="4. Results"==> HCL_PLANNER
    
    %% --- HCL External Interactions ---
    HCL_PLANNER -.->|"generate_plan(thinking=high)"| GEMINI
    HCL_EXECUTOR -.->|"Scale-to-Zero"| K8S

    %% --- THE REFLECTION LOOP (Async) ---
    HCL_PLANNER --o|"Enqueue Log (Async)"| SHARED_CLIENT
    HCL_EXECUTOR --o|"Enqueue Log (Async)"| SHARED_CLIENT
    SHARED_CLIENT ==="Batch Submit"==> REFLECTOR
    REFLECTOR ==="Critique"==> HCL_PLANNER & HCL_EXECUTOR

    %% --- Memory Persistence ---
    REFLECTOR ==>|"Update MIRIX"| EPISODIC
    EPISODIC ===>|"Vector Search (<10ms)"| QDRANT

    %% --- Security & Reactive Flows ---
    REACTIVE ==="ThreatDetected"==> MAXIMUS_CORE
    REACTIVE --o|"Publish"| KAFKA

    %% --- Data Persistence ---
    HCL_MONITOR -.->|"Store"| PG_DB
    HCL_ANALYZER --o|"Publish"| KAFKA
```
