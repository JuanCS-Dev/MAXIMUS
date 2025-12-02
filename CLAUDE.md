# MAXIMUS 2.0 - Claude Code Guidelines

> **Data Atual**: 01 de Dezembro de 2025
> **Arquiteto-Chefe**: Juan Carlos de Souza

## Verificações Obrigatórias

### Data e Contexto Temporal
- **SEMPRE** verificar a data atual antes de pesquisar documentação
- A data de hoje é **01/12/2025** (Dezembro de 2025)
- Ao pesquisar APIs e bibliotecas, usar versões de 2025

### Versões Atuais (Dezembro 2025)

| Tecnologia | Versão | Notas |
|------------|--------|-------|
| **Gemini** | **3 Pro** (`gemini-3-pro-preview`) | 1M tokens, thinking_level, thought_signatures |
| Python | 3.12+ | Type hints obrigatórios |
| FastAPI | 0.115+ | Async by default |
| Pydantic | 2.5+ | Model validation |
| pytest | 8.0+ | asyncio_mode="auto" |

### Gemini 3 Pro - Parâmetros Importantes

```python
# Configuração correta para Gemini 3 Pro
config = GeminiConfig(
    api_key="...",
    model="gemini-3-pro-preview",
    thinking_level="high",  # "low" ou "high"
    max_output_tokens=8192,
    use_thought_signatures=True
)
```

**Novos recursos do Gemini 3:**
- `thinking_level`: Controla profundidade de raciocínio (low/high)
- `thought_signatures`: Mantém contexto entre turnos
- `media_resolution`: Controla tokens por imagem/vídeo
- Janela de contexto de 1M tokens
- `responseMimeType: "application/json"` para saídas estruturadas

## Estrutura do Projeto

```
backend/services/
├── metacognitive_reflector/  # Tribunal de Juízes (VERITAS, SOPHIA, DIKĒ)
├── meta_orchestrator/         # World Model (SimuRA + Dyna-Think)
├── hcl_analyzer_service/      # Anomaly Detection (SARIMA + IsolationForest)
├── hcl_executor_service/      # Kubernetes executor
└── episodic_memory/           # Memory service
```

## Padrões de Código

### Imports
```python
from __future__ import annotations
from typing import Any, Dict, List, Optional
```

### Docstrings
```python
"""
Descrição breve.

Args:
    param: Descrição

Returns:
    Descrição do retorno
"""
```

### Testes
- Usar `pytest.mark.asyncio` para testes async
- Mockar chamadas HTTP externas
- Coverage target: 90%+

## Comandos Úteis

```bash
# Rodar testes
PYTHONPATH=. python -m pytest tests/ -v

# Coverage
PYTHONPATH=. python -m pytest tests/ --cov=. --cov-report=term-missing

# Pylint
python -m pylint **/*.py
```

## CODE CONSTITUTION (4 Pilares)

1. **Clarity Over Cleverness** - Código óbvio, bem documentado
2. **Consistency is King** - Padrões uniformes
3. **Simplicity at Scale** - YAGNI aplicado
4. **Safety First** - Type hints 100%, validação de input
