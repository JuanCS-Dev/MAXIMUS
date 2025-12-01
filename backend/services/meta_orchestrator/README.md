# 🧠 Maximus 2.0 - Meta-Orchestrator

**Hierarchical Multi-Agent Orchestration Service**

> Google-level refactoring implementing ROMA (Recursive Open Meta-Agent) pattern with world-class code quality standards.

---

## 🎯 Overview

The Meta-Orchestrator is the **brain** of Maximus 2.0. It coordinates specialist agents (HCL, OSINT, Memory, etc.) to execute complex missions through hierarchical task decomposition and intelligent routing.

### Architecture

```
Mission (Complex Task)
  ↓
TaskDecomposer (ROMA Pattern)
  ↓
Subtasks (with dependencies)
  ↓
AgentRegistry (Routing + Load Balancing)
  ↓
Specialist Agents (HCL, OSINT, etc.)
  ↓
Results Synthesis
```

### Key Features

✅ **ROMA Pattern**: Recursive task decomposition  
✅ **Plugin System**: Dynamic agent registration  
✅ **Smart Routing**: Load-balanced task assignment  
✅ **Dependency Resolution**: Execute tasks in correct order  
✅ **Parallel Execution**: Maximize throughput  
✅ **Health Monitoring**: Continuous agent health checks  
✅ **Type-Safe**: 100% type hints  
✅ **Production-Ready**: Error handling + logging + metrics  

---

## 📦 Structure

```
meta_orchestrator/
├── api/
│   ├── routes.py              # FastAPI endpoints (< 250 lines)
│   └── __init__.py
├── core/
│   ├── orchestrator.py        # Main coordination logic (< 400 lines)
│   ├── agent_registry.py      # Plugin management (< 400 lines)
│   ├── task_decomposer.py     # ROMA decomposition (< 400 lines)
│   └── __init__.py
├── plugins/
│   ├── base.py                # AgentPlugin interface (< 300 lines)
│   └── __init__.py
├── tests/
│   └── ...
├── Dockerfile
├── requirements.txt
└── README.md (this file)
```

**File Size Compliance**: All files < 500 lines (ideal: < 400) ✅

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/juan/vertice-dev/backend/services/meta_orchestrator
pip install -r requirements.txt
```

### 2. Run Locally

```bash
# Development mode (auto-reload)
uvicorn api.routes:app --reload --port 8100

# Production mode
uvicorn api.routes:app --host 0.0.0.0 --port 8100 --workers 4
```

### 3. Docker

```bash
# Build
docker build -t maximus-meta-orchestrator:2.0 .

# Run
docker run -p 8100:8100 maximus-meta-orchestrator:2.0
```

### 4. Docker Compose

Add to `docker-compose.yml`:

```yaml
meta-orchestrator:
  build:
    context: ./backend/services/meta_orchestrator
  container_name: maximus-meta-orchestrator
  ports:
    - "8100:8100"
  environment:
    - LOG_LEVEL=INFO
  networks:
    - maximus-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8100/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

---

## 📖 Usage

### Execute a Mission

```bash
curl -X POST http://localhost:8100/v1/missions \
  -H "Content-Type: application/json" \
  -d '{
    "type": "infrastructure",
    "description": "Optimize system performance and reduce costs",
    "context": {"environment": "production"},
    "priority": "high"
  }'
```

**Response**:
```json
{
  "mission_id": "mission_1234567890",
  "status": "completed",
  "output": {
    "subtasks": {
      "mission_1234567890.1": {"metrics": "..."},
      "mission_1234567890.2": {"analysis": "..."}
    }
  },
  "reasoning": "Monitored system → Analyzed bottlenecks → Generated plan → Executed optimizations",
  "confidence": 0.92,
  "execution_time_ms": 3420,
  "errors": []
}
```

### List Agents

```bash
curl http://localhost:8100/v1/agents
```

### Check Agent Health

```bash
curl http://localhost:8100/v1/agents/hcl_planner/health
```

---

## 🔌 Plugin Development

### Creating a Custom Agent

```python
from meta_orchestrator.plugins import AgentPlugin, Task, TaskResult, TaskStatus

class MyCustomAgent(AgentPlugin):
    @property
    def name(self) -> str:
        return "my_custom_agent"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def capabilities(self) -> List[str]:
        return ["custom_task_type"]
    
    @property
    def description(self) -> str:
        return "My custom specialist agent"
    
    async def can_handle(self, task: Task) -> bool:
        return task.type == "custom_task_type"
    
    async def estimate_effort(self, task: Task) -> float:
        return 0.5  # Medium complexity
    
    async def execute(self, task: Task) -> TaskResult:
        # Your custom logic here
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            output={"result": "success"},
            reasoning="Task completed successfully"
        )
    
    async def health_check(self) -> Dict[str, Any]:
        return {"healthy": True, "status": "operational"}
```

### Registering Agent

```python
# In api/routes.py startup event
from my_agents import MyCustomAgent

@app.on_event("startup")
async def startup_event():
    # ... existing code ...
    
    # Register custom agent
    custom_agent = MyCustomAgent()
    await registry.register(
        agent=custom_agent,
        enabled=True,
        priority=100,
        tags=["custom", "specialist"]
    )
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=. --cov-report=html tests/
```

---

## 📊 Code Quality Standards

All code in this service adheres to **Google-level standards**:

- ✅ **Max 500 lines/file** (ideal: 400)
- ✅ **100% type hints** (all parameters, returns)
- ✅ **Docstrings** (all classes, methods)
- ✅ **Async-first** (no blocking I/O)
- ✅ **Error handling** (comprehensive try/except)
- ✅ **Logging** (structured + contextual)
- ✅ **Single responsibility** (one class, one purpose)
- ✅ **Dependency injection** (no hard-coded deps)

**Quality Gates**:
- Pylint score: ≥ 9.0/10
- MyPy strict mode: Pass
- Unit test coverage: ≥ 80%

---

## 🔬 Research Basis

This implementation is based on Nov 2025 cutting-edge research:

**Papers**:
- ROMA (Recursive Open Meta-Agent) - sentient.xyz, June 2025
- "Hierarchical Cognitive Agents" - SparkCO.ai, 2025
- Google's agent orchestration patterns

**Industry Implementations**:
- Anthropic's Claude Agent SDK
- OpenAI's multi-agent systems
- Google Gemini 3 Pro agentic features

See: `/home/juan/vertice-dev/AGI_META_AGENTS_DEEP_RESEARCH_2025.md`

---

## 🛠️ Development Roadmap

### ✅ Phase 1: Foundation (COMPLETE)
- [x] AgentPlugin base interface
- [x] AgentRegistry implementation
- [x] TaskDecomposer (ROMA pattern)
- [x] Orchestrator core
- [x] FastAPI routes
- [x] Docker support

### 🚧 Phase 2: Enhanced Intelligence (NEXT)
- [ ] Gemini 3 Pro integration for intelligent decomposition
- [ ] Episodic memory integration
- [ ] World model simulation (SimuRA)
- [ ] Metacognitive reflection layer

### 📅 Phase 3: Production Hardening
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Metrics (Prometheus)
- [ ] Rate limiting
- [ ] Circuit breakers
- [ ] Retry logic with exponential backoff

---

## 🤝 Contributing

1. Follow code quality standards (see above)
2. Max 400-500 lines per file
3. Add tests for new features
4. Update this README

---

## 📞 Support

**Documentation**: [Google-Level Refactor Plan](../../../.gemini/antigravity/brain/.../google_level_refactor_plan.md)  
**Research**: [AGI & Meta-Agents Deep Research](../../../AGI_META_AGENTS_DEEP_RESEARCH_2025.md)

---

**Status**: ✅ Foundation Complete - Ready for Plugin Development

Built with 🧠 by Maximus 2.0 Team | Nov 2025
