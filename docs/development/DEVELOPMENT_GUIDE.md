# 💻 MAXIMUS 2.0 - Development Guide

> **Guia completo para desenvolvedores contribuindo com MAXIMUS**
> Versão: 2.0.0 | Última Atualização: Dezembro 2025

[![Code Quality](https://img.shields.io/badge/Code%20Quality-98.5%2F100-brightgreen)]()
[![Coverage](https://img.shields.io/badge/Coverage-92%25-success)]()
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)]()

---

## 📋 Pré-requisitos

### Software Obrigatório

| Software | Versão | Instalação |
|----------|--------|------------|
| **Python** | ≥3.12 | `sudo apt install python3.12` |
| **pip** | Latest | `python3 -m ensurepip` |
| **Docker** | ≥24.0 | [Install Guide](https://docs.docker.com/engine/install/) |
| **Docker Compose** | ≥2.20 | Included with Docker Desktop |
| **Git** | ≥2.40 | `sudo apt install git` |

### Software Recomendado

- **VSCode** - Editor com Python extension
- **Pydantic** - Para validação de dados
- **Black** - Auto-formatter
- **Pylint** - Linter
- **pytest** - Testing framework

---

## 🚀 Setup do Ambiente

### 1. Clone do Repositório

```bash
git clone https://github.com/vertice/maximus-agentic.git
cd maximus-agentic
```

### 2. Criar Virtual Environment

```bash
# Criar venv
python3.12 -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
# Development dependencies
pip install -r requirements-dev.txt

# Production dependencies
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar com suas credenciais
nano .env
```

**Variáveis essenciais:**
```bash
# Database
POSTGRES_URL=postgresql://user:pass@localhost:5432/maximus
REDIS_URL=redis://localhost:6379/0

# AI
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key  # Optional

# Services
API_GATEWAY_PORT=8000
MAXIMUS_CORE_PORT=8001

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 5. Iniciar Serviços (Docker)

```bash
# Start databases
docker-compose up -d postgres redis qdrant elasticsearch

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres
```

### 6. Migrar Database

```bash
# Run migrations
PYTHONPATH=. python backend/services/maximus_core_service/scripts/migrate_db.py

# Verify
psql $POSTGRES_URL -c "\dt"
```

### 7. Rodar Testes

```bash
# All tests
PYTHONPATH=. python -m pytest tests/ -v

# With coverage
PYTHONPATH=. python -m pytest tests/ --cov=backend --cov-report=html

# View coverage
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

---

## 📐 Padrões de Código

**LEITURA OBRIGATÓRIA:** [CODE_CONSTITUTION.md](./CODE_CONSTITUTION.md)

### File Structure

```python
"""
Module docstring (REQUIRED)
=========================

Brief description on first line.

Detailed explanation.
"""

# 1. Future imports
from __future__ import annotations

# 2. Standard library
import asyncio
import logging
from typing import Any, Dict, List

# 3. Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# 4. Local application
from ..core import Something
from .models import SomeModel

# 5. Constants
DEFAULT_TIMEOUT = 30

# 6. Classes and functions
class MyClass:
    pass
```

### Naming Conventions

```python
# Classes: PascalCase
class AgentPlugin:
    pass

# Functions: snake_case
def execute_mission():
    pass

# Constants: SCREAMING_SNAKE_CASE
MAX_RETRIES = 3

# Private: _leading_underscore
def _internal_helper():
    pass
```

### Type Hints (100% Required)

```python
# ❌ FORBIDDEN
def process_data(data, config):
    return something

# ✅ REQUIRED
def process_data(data: Dict[str, Any], config: Config) -> ProcessedData:
    return something

# Use from __future__ import annotations for forward refs
from __future__ import annotations

def create_agent(name: str) -> Agent:  # Agent not yet defined - OK with annotations
    ...

class Agent:
    pass
```

### Docstrings (Google Style)

```python
async def complex_function(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """
    Brief one-line description.

    Longer description with multiple paragraphs if needed.

    Args:
        param1: Description of param1
        param2: Description of param2. Use None for default.

    Returns:
        Dictionary containing:
            - key1 (str): Description
            - key2 (int): Description

    Raises:
        ValueError: If param1 is empty
        HTTPException: If external API fails

    Example:
        >>> result = await complex_function("test", param2=42)
        >>> print(result["key1"])
        "processed"
    """
    pass
```

---

## 🏗️ Workflow de Desenvolvimento

### 1. Criar Feature Branch

```bash
# From main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-awesome-feature
```

### 2. Implementar Feature

```python
# backend/services/maximus_core_service/my_module/my_feature.py

"""My awesome feature implementation."""

from __future__ import annotations

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MyFeature:
    """Implements my awesome feature."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize with config."""
        self.config = config
        logger.info("MyFeature initialized")

    async def execute(self) -> Dict[str, Any]:
        """Execute the feature."""
        try:
            result = await self._do_work()
            logger.info("Feature executed successfully")
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"Feature execution failed: {e}")
            raise

    async def _do_work(self) -> Any:
        """Internal implementation."""
        # Your code here
        pass
```

### 3. Escrever Testes

```python
# tests/unit/my_module/test_my_feature.py

import pytest
from my_module.my_feature import MyFeature


class TestMyFeature:
    """Test suite for MyFeature."""

    @pytest.fixture
    def feature(self):
        """Create feature instance."""
        return MyFeature(config={})

    @pytest.mark.asyncio
    async def test_execute_success(self, feature):
        """Test successful execution."""
        result = await feature.execute()
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_execute_with_invalid_config_fails(self):
        """Test execution with invalid config fails."""
        feature = MyFeature(config={"invalid": True})
        with pytest.raises(ValueError):
            await feature.execute()
```

### 4. Rodar Quality Checks

```bash
# Format code
black backend/services/maximus_core_service/my_module/

# Type check
mypy --strict backend/services/maximus_core_service/my_module/

# Lint
pylint backend/services/maximus_core_service/my_module/

# Test
PYTHONPATH=. python -m pytest tests/unit/my_module/ -v

# Coverage
PYTHONPATH=. python -m pytest tests/unit/my_module/ --cov=my_module --cov-fail-under=90
```

### 5. Commit Changes

```bash
# Stage changes
git add backend/services/maximus_core_service/my_module/
git add tests/unit/my_module/

# Commit with conventional commit message
git commit -m "feat(my_module): add awesome feature

Implement MyFeature class that does X, Y, Z.

Supports:
- Feature A
- Feature B

Closes #123

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 6. Push & Create PR

```bash
# Push branch
git push origin feature/my-awesome-feature

# Create PR on GitHub
gh pr create --title "feat(my_module): add awesome feature" \
             --body "$(cat <<'EOF'
## Summary
- Implements MyFeature for X, Y, Z
- Added comprehensive tests (95% coverage)
- Updated documentation

## Test plan
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed

## Checklist
- [x] Code follows CODE_CONSTITUTION.md
- [x] All files <500 lines
- [x] Type hints 100%
- [x] Docstrings complete
- [x] Tests added (coverage ≥90%)
- [x] Pylint score ≥9.0
- [x] Documentation updated

🤖 Generated with Claude Code
EOF
)"
```

---

## 🧪 Testing Strategy

### Pyramid de Testes

```
        /\
       /  \      10% - End-to-End Tests
      /────\
     /      \    30% - Integration Tests
    /────────\
   /          \  60% - Unit Tests
  /────────────\
```

### Unit Tests

**Onde:** `tests/unit/`

**Foco:** Testar funções/classes isoladamente

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_isolated_function():
    """Test function in isolation with mocks."""
    # Given
    mock_dependency = AsyncMock()
    mock_dependency.get_data.return_value = {"key": "value"}

    # When
    result = await function_under_test(mock_dependency)

    # Then
    assert result == expected_value
    mock_dependency.get_data.assert_called_once()
```

### Integration Tests

**Onde:** `tests/integration/`

**Foco:** Testar integração entre componentes

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_service_integration():
    """Test integration between services."""
    # Setup
    service_a = ServiceA(config)
    service_b = ServiceB(config)

    # Execute
    result_a = await service_a.execute()
    result_b = await service_b.process(result_a)

    # Verify
    assert result_b["status"] == "success"
```

### End-to-End Tests

**Onde:** `tests/e2e/`

**Foco:** Testar fluxos completos

```python
@pytest.mark.e2e
async def test_complete_decision_flow():
    """Test complete HITL decision flow."""
    # 1. AI makes decision
    decision = await maximus_core.make_decision(action)

    # 2. HITL evaluation
    result = await hitl.evaluate(decision)

    # 3. Operator review (simulated)
    await operator.approve(result.decision_id)

    # 4. Execution
    execution_result = await executor.execute(decision)

    # 5. Audit trail verification
    audit_events = await audit_trail.query(decision_id=result.decision_id)

    assert execution_result["status"] == "success"
    assert len(audit_events) >= 3  # queued, approved, executed
```

### Coverage Requirements

```bash
# Minimum: 80%
# Target: 90%
# Excellent: 95%+

pytest --cov=backend --cov-report=term-missing --cov-fail-under=90
```

---

## 🔧 Debugging

### Logging

```python
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed diagnostic information")
logger.info("General informational messages")
logger.warning("Warning messages for potentially harmful situations")
logger.error("Error messages for failures")
logger.critical("Critical errors that may cause shutdown")

# Use structured logging
logger.info("User action", extra={
    "user_id": "123",
    "action": "login",
    "ip_address": "192.168.1.1"
})
```

### Debug avec VSCode

**launch.json:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "backend.services.api_gateway.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ],
            "jinja": true,
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### Interactive Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()

# Common commands:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# l - list code around current line
# h - help
```

---

## 📊 Métricas & Monitoring

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Counter: monotonically increasing
requests_total = Counter(
    "maximus_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "status"]
)

# Histogram: measure distributions
request_duration = Histogram(
    "maximus_request_duration_seconds",
    "HTTP request duration",
    ["service", "endpoint"]
)

# Gauge: can go up/down
active_connections = Gauge(
    "maximus_active_connections",
    "Active WebSocket connections",
    ["service"]
)

# Usage
requests_total.labels(
    service="maximus_core",
    method="POST",
    endpoint="/api/consciousness",
    status="200"
).inc()

with request_duration.labels(service="maximus_core", endpoint="/api/consciousness").time():
    # Your code here
    pass

active_connections.labels(service="maximus_core").set(42)
```

---

## 🚀 Deployment

### Local Development

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d maximus_core

# View logs
docker-compose logs -f maximus_core

# Restart service
docker-compose restart maximus_core

# Stop all
docker-compose down
```

### Production Deployment

```bash
# Build images
docker build -t maximus/core:2.0.0 -f backend/services/maximus_core_service/Dockerfile .

# Push to registry
docker push maximus/core:2.0.0

# Deploy to Kubernetes
kubectl apply -f k8s/maximus-core-deployment.yaml

# Check rollout status
kubectl rollout status deployment/maximus-core

# View pods
kubectl get pods -l app=maximus-core

# View logs
kubectl logs -f deployment/maximus-core --tail=100
```

---

## 🤝 Contributing Checklist

Antes de submeter PR, verificar:

### Code Quality
- [ ] Código segue CODE_CONSTITUTION.md
- [ ] Todos arquivos <500 linhas
- [ ] Type hints 100%
- [ ] Docstrings completos (Google style)
- [ ] Sem TODOs/FIXMEs/HACKs

### Testing
- [ ] Testes unitários adicionados
- [ ] Coverage ≥90%
- [ ] Testes de integração (se aplicável)
- [ ] Todos os testes passam

### Linting & Formatting
- [ ] `black .` executado
- [ ] `mypy --strict` passa
- [ ] `pylint` score ≥9.0

### Documentation
- [ ] Docstrings atualizados
- [ ] README atualizado (se necessário)
- [ ] API docs atualizadas (se API mudou)
- [ ] Migration guide (se breaking change)

### Git
- [ ] Branch atualizado com main
- [ ] Commit messages seguem conventional commits
- [ ] PR description completa

---

## 📚 Recursos

### Internal Docs
- [CODE_CONSTITUTION.md](./CODE_CONSTITUTION.md) - **LEITURA OBRIGATÓRIA**
- [Architecture Overview](../architecture/OVERVIEW.md)
- [HITL Module](../modules/HITL_MODULE.md)
- [Sprint 2 Report](../sprints/SPRINT_2_DECOMPOSITION.md)

### External Resources
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 8](https://peps.python.org/pep-0008/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Pytest Docs](https://docs.pytest.org/)

---

## ❓ FAQ

**Q: Qual versão do Python devo usar?**
A: Python 3.12+ é obrigatório. Use `pyenv` para gerenciar versões.

**Q: Como rodar apenas um serviço?**
A: `python backend/services/maximus_core_service/main.py`

**Q: Como debugar testes?**
A: `pytest tests/unit/test_file.py::test_function -v -s` (-s mostra prints)

**Q: Arquivo >500 linhas, o que fazer?**
A: Decompor em pacote modular (`models.py` + `core.py` + `__init__.py`). Ver [Sprint 2 Report](../sprints/SPRINT_2_DECOMPOSITION.md).

**Q: Como adicionar nova dependência?**
A: Adicionar em `requirements.txt` ou `requirements-dev.txt` e rodar `pip install -r requirements.txt`.

---

**Mantido por:** Juan Carlos de Souza
**Última atualização:** 03 de Dezembro de 2025
**Versão:** 2.0.0
