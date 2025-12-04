# Maximus SDK (Draft de Design) 🛠️

> **Objetivo**: Tornar a criação de Agentes Meta-Cognitivos tão simples quanto criar uma rota no FastAPI.
> **Filosofia**: "Compliance by Default" (O SDK garante a constituição, você foca na lógica).

---

## 1. O Problema Atual (A "Dor")

Hoje, para criar um agente compatível com o Maximus, você precisa:
1.  Herdar de `AgentPlugin`.
2.  Implementar `health_check` manualmente.
3.  Configurar injeção de dependência.
4.  Lembrar de chamar o `Reflector` (se esquecer, quebra a constituição).
5.  Lidar com conexões Kafka/gRPC "na mão".

É muito código repetitivo ("boilerplate") e muita chance de erro.

---

## 2. A Solução: Maximus SDK (`maximus-sdk`)

O SDK inverte a responsabilidade. Em vez de você *chamar* o Maximus, o Maximus *envolve* seu código.

### A Experiência do Desenvolvedor (DX)

Imagine que você quer criar um agente que analisa logs de segurança. Com o SDK, seria assim:

```python
from maximus import Agent, Context, Task

# 1. Definição Declarativa (Metadados)
agent = Agent(
    name="SecurityAnalyst",
    description="Analisa logs em busca de anomalias",
    version="1.0.0",
    capabilities=["analyze_logs", "check_firewall"]
)

# 2. Lógica de Negócio (Decorators)
@agent.on_task("analyze_logs")
async def analyze(ctx: Context, logs: list[str]):
    """
    Analisa uma lista de logs.
    O 'ctx' já traz tudo pronto: logger, memória, ferramentas.
    """
    
    # O SDK injeta o logger estruturado automaticamente
    ctx.log.info(f"Analisando {len(logs)} logs...")
    
    # Acesso fácil à memória (sem configurar clientes)
    known_threats = await ctx.memory.semantic.search("ameaças recentes")
    
    # Lógica do agente...
    anomalies = []
    for log in logs:
        if "ERROR" in log:
            anomalies.append(log)
            
    # Retorno simples (o SDK empacota no TaskResult)
    return {"status": "completed", "anomalies": anomalies}

# 3. Inicialização Automática
if __name__ == "__main__":
    agent.run() # Sobe servidor, conecta no Kafka, registra no Maestro...
```

---

## 3. O Que o SDK Faz "Por Baixo dos Panos"?

Quando você roda `agent.run()`, o SDK assume o controle e garante os **4 Pilares** automaticamente:

1.  **Auto-Registro**: Ele chama o `Meta Orchestrator` e diz: "Oi, sou o SecurityAnalyst e sei fazer `analyze_logs`".
2.  **Health Check Automático**: Ele cria o endpoint `/health` sozinho. Se seu código travar, ele reporta.
3.  **Reflexão Forçada (Middleware)**:
    *   Antes de chamar sua função `analyze`, o SDK avisa o Reflector: "Vou começar".
    *   Depois que você retorna, o SDK envia o resultado para o Reflector: "Terminei, me julgue".
    *   **Você não consegue "esquecer" a ética. Ela é parte do framework.**
4.  **Tratamento de Erros**: Se sua função explodir, o SDK captura, formata o erro no padrão Maximus e avisa o monitoramento.

---

## 4. Estrutura Proposta do Pacote

```
maximus/
├── __init__.py      # Exports: Agent, Context, Task
├── core/
│   ├── app.py       # A classe 'Agent' (wrapper do FastAPI/Typer)
│   ├── context.py   # O objeto 'Context' (facade para serviços)
│   └── middleware.py # Onde a mágica da Reflexão acontece
├── clients/
│   ├── reflector.py # Cliente HTTP/gRPC para o Reflector
│   └── memory.py    # Cliente simplificado para o ChromaDB
└── utils/
    └── logging.py   # Logger JSON estruturado padrão Google
```

---

## 5. Comparativo

| Característica | Sem SDK (Atual) | Com SDK (Futuro) |
| :--- | :--- | :--- |
| **Linhas de Código** | ~150 (muito setup) | ~20 (só lógica) |
| **Curva de Aprendizado** | Alta (precisa ler docs de arquitetura) | Baixa (parece Flask/FastAPI) |
| **Segurança** | Manual (dev pode esquecer) | **Automática** (Middleware) |
| **Padrão** | Depende da disciplina do dev | Forçado pelo framework |

---

## 6. Próximos Passos (Roadmap do SDK)

1.  **Fase 1 (Core)**: Criar a classe `Agent` e o decorator `@on_task`.
2.  **Fase 2 (Middleware)**: Implementar a integração automática com o `Reflector`.
3.  **Fase 3 (Tools)**: Adicionar suporte fácil a ferramentas (ex: `@agent.tool`).
4.  **Fase 4 (CLI)**: Criar um `maximus create agent` que gera a estrutura de pastas.

---

> **Conclusão**: O SDK transforma o Maximus de um "sistema complexo" em uma "plataforma de desenvolvimento". O desenvolvedor só precisa se preocupar em ser inteligente; o SDK cuida de ser ético e organizado.
