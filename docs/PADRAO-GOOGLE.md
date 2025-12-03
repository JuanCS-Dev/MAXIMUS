# 🏛️ O PLANO DOS 4 PILARES: MAXIMUS 2.0
> **"Eu me recuso a criar o futuro se esse código continuar assim."** - Juan Carlos de Souza

Este documento define o **Plano Mestre de Refatoração** para alinhar o `maximus_core_service` com os 4 Pilares fundamentais. Não é uma sugestão. É a lei.

---

## 🏗️ OS 4 PILARES

### 1. 🚀 Escalabilidade (Scalability)
*O sistema deve crescer sem colapsar.*
- **Arquitetura**: Modular, desacoplada, orientada a eventos.
- **Performance**: Async-first, sem bloqueios no event loop, métricas em tempo real.
- **Regra de Ouro**: Nenhum componente pode derrubar o sistema inteiro (Circuit Breakers obrigatórios).

### 2. 🔧 Manutenibilidade (Maintainability)
*O código deve ser fácil de ler, entender e modificar.*
- **Tamanho**: Arquivos < 500 linhas. Funções < 50 linhas.
- **Clareza**: Type hints estritos (`mypy --strict`), Docstrings Google Style.
- **Regra de Ouro**: Se você precisa "explicar" o código, ele está complexo demais. Refatore.

### 3. 🎨 Padrão Google (Google Pattern)
*O código deve parecer escrito por uma única pessoa (o Google).*
- **Estilo**: PEP 8, Imports organizados, Naming conventions estritos.
- **Estrutura**: Diretórios padronizados, `__init__.py` limpos.
- **Regra de Ouro**: Consistência vence inteligência. Siga o padrão, não invente moda.

### 4. 📜 Constituição (Code Constitution)
*O código deve ser ético, seguro e honesto.*
- **Integridade**: Zero placeholders (`pass`, `TODO` sem ticket).
- **Segurança**: Validação de input obrigatória (Pydantic), Fail-fast.
- **Regra de Ouro**: A "Obrigação da Verdade". Nunca retorne sucesso falso.

---

## 📊 DIAGNÓSTICO ATUAL (Audit 02/12/2025)

| Pilar | Status | Violações Críticas |
| :--- | :--- | :--- |
| **Escalabilidade** | ⚠️ ALERTA | Monolitos identificados (`fabric/core.py`, `safety.py`). Risco de gargalo. |
| **Manutenibilidade** | ❌ CRÍTICO | **60+ arquivos > 500 linhas**. `pass` usado 296 vezes. |
| **Padrão Google** | ✅ BOM | Future annotations em 100%. Docstrings presentes. |
| **Constituição** | ⚠️ ALERTA | Typing não estrito (`disallow_untyped_defs = False`). |

---

## ⚔️ PLANO DE BATALHA: A GRANDE REFATORAÇÃO

Executaremos este plano em **4 Fases Sequenciais**. Nenhuma fase começa sem a anterior estar 100% concluída.

### FASE 1: A FUNDAÇÃO (Typing & Config)
*Objetivo: Endurecer as regras antes de mexer no código.*

1.  **Configuração Estrita**:
    - Atualizar `pyproject.toml` para `disallow_untyped_defs = true`.
    - Configurar `ruff` para impor limite de 500 linhas (aviso).
2.  **Saneamento de Tipos**:
    - Rodar `mypy` e corrigir TODOS os erros de tipagem resultantes.
    - Eliminar `Any` desnecessários.
3.  **Eliminação de Placeholders**:
    - Substituir `pass` por `...` (Ellipsis) em protocolos/ABCs.
    - Substituir `pass` por `raise NotImplementedError` em métodos não implementados.
    - Converter TODOs em Issues ou remover.

### FASE 2: O DESMEMBRAMENTO (Scalability & Maintainability)
*Objetivo: Implodir os "God Files" (>500 linhas).*

**Alvos Prioritários:**
1.  `consciousness/tig/fabric/core.py` (538 linhas)
    - ✂️ Separar: `initialization.py`, `metrics.py`, `broadcasting.py`.
2.  `training/data_validator.py` (583 linhas)
    - ✂️ Separar: `validators/`, `schemas/`.
3.  `governance_sse/api_routes.py` (841 linhas)
    - ✂️ Separar: `routes/auth.py`, `routes/stream.py`, `routes/control.py`.
4.  `performance/inference_engine.py` (620 linhas)
    - ✂️ Separar: `engine.py`, `optimization.py`.
5.  `tests/unit/consciousness/test_safety_refactored.py` (2450 linhas)
    - ✂️ Separar em diretório: `tests/unit/consciousness/safety/`.

### FASE 3: A PADRONIZAÇÃO (Google Pattern)
*Objetivo: Polimento visual e estrutural.*

1.  **Docstrings**:
    - Garantir que TODAS as funções públicas tenham docstrings Google Style.
    - Verificar `Args`, `Returns`, `Raises`.
2.  **Imports**:
    - Reordenar imports em todos os arquivos (usar `isort` profile black/google).
3.  **Nomenclatura**:
    - Renomear variáveis/funções que não seguem `snake_case` ou são ambíguas.

### FASE 4: A BLINDAGEM (Code Constitution)
*Objetivo: Garantia de qualidade final.*

1.  **Testes de Regressão**:
    - Re-executar a bateria de testes (Fases 1-6) após cada refatoração grande.
    - Garantir cobertura > 99% nos módulos refatorados.
2.  **Validação Final**:
    - Rodar novo Audit.
    - Só declarar vitória com **ZERO** arquivos > 500 linhas e **ZERO** erros de mypy.

---

## 🛡️ PROTOCOLOS DE MANUTENÇÃO

Para garantir que o caos não retorne:

1.  **Pre-commit Hook Mental**:
    - "Este arquivo tem mais de 500 linhas?" -> **NÃO COMMITA**.
    - "Esta função tem tipos?" -> **NÃO COMMITA**.
    - "Deixei um `pass` aqui?" -> **NÃO COMMITA**.

2.  **A Regra do Escoteiro**:
    - Sempre deixe o código mais limpo do que encontrou.
    - Se viu um arquivo grande, proponha a refatoração.

3.  **Revisão Constitucional**:
    - Todo PR deve ser validado contra os 4 Pilares.

---

**Status Atual**: PRONTO PARA EXECUÇÃO DA FASE 1.
**Autoridade**: Juan Carlos de Souza & Antigravity
**Data**: 02/12/2025
