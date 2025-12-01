# MAXIMUS V2 - Plano de Transição e Repositório

**Data**: 2025-11-30  
**Status**: 🟢 Limpeza Completa | 🔄 Preparando Renomeação

---

## ✅ Estado Atual - LIMPO!

### CORE Services (10/10) ✅
1. `meta_orchestrator` - Coordenação de agentes (ROMA)
2. `hcl_planner_service` - Planejamento de infraestrutura
3. `hcl_executor_service` - Execução de ações
4. `hcl_analyzer_service` - Análise de métricas
5. `hcl_monitor_service` - Monitoramento contínuo
6. `maximus_core_service` - Sistema de consciência (TIG Fabric)
7. `digital_thalamus_service` - Gateway neural
8. `prefrontal_cortex_service` - Função executiva
9. `ethical_audit_service` - Compliance constitucional
10. `reactive_fabric_core` - Reflexo imune

### Serviços Migrados
- **57 serviços LEGACY** movidos para DATA disk
- **Backup**: `/media/juan/DATA/backups/maximus-legado-services-2025-11-30/`

---

## 🎯 Plano: vertice-dev → Maximus-V2

### Fase 1: Renomeação do Diretório ✅ (Pronto para executar)

```bash
# 1. Renomear diretório
sudo mv /home/juan/vertice-dev /home/juan/Maximus-V2

# 2. Criar link simbólico temporário (compatibilidade)
ln -s /home/juan/Maximus-V2 /home/juan/vertice-dev

# 3. Verificar
ls -la /home/juan/ | grep -E "Maximus|vertice"
```

### Fase 2: Estrutura do Repositório

**Nome do Repo**: `Maximus-V2`  
**Descrição**: "Constitutional Meta-Cognitive AI that Manages Agents"  
**Branch Principal**: `main`

**Estrutura ideal**:
```
Maximus-V2/
├── README.md                    # Identidade MAXIMUS 2.0
├── CODE_CONSTITUTION.md         # 4 PILARES
├── .gitignore                   # Python, Docker, etc.
├── backend/
│   └── services/                # 10 CORE services
│       ├── meta_orchestrator/
│       ├── hcl_planner_service/
│       ├── hcl_executor_service/
│       ├── hcl_analyzer_service/
│       ├── hcl_monitor_service/
│       ├── maximus_core_service/
│       ├── digital_thalamus_service/
│       ├── prefrontal_cortex_service/
│       ├── ethical_audit_service/
│       └── reactive_fabric_core/
├── docker-compose.yml           # Apenas CORE services
├── scripts/                     # Scripts de migração e setup
└── docs/                        # Documentação
    ├── MAXIMUS_2_IDENTITY.md
    ├── CORE_SERVICES_GUIDE.md
    └── MIGRATION_HISTORY.md
```

### Fase 3: Refatoração para 4 PILARES (Antes do Commit)

**NÃO fazer commit inicial até que:**

#### ✅ Pilar 1: Escalabilidade
- [ ] Todos os services com async/await onde apropriado
- [ ] APIs RESTful padronizadas
- [ ] Mensageria configurada (RabbitMQ/Redis)

#### ✅ Pilar 2: Manutenibilidade
- [ ] Todos os arquivos < 400 linhas
- [ ] Zero TODOs/FIXMEs
- [ ] 100% docstrings (Google style)
- [ ] Estrutura de pastas consistente

#### ✅ Pilar 3: Padrão Google
- [ ] `mypy --strict` passa em todos
- [ ] `pylint --fail-under=9.5` passa
- [ ] 100% type hints
- [ ] Testes unitários (coverage > 80%)

#### ✅ Pilar 4: CODE_CONSTITUTION
- [ ] Todos os services seguem arquitetura constitucional
- [ ] Guardian agent (ethical_audit) operacional
- [ ] Nenhuma violação de princípios

---

## 📋 Checklist para Primeiro Commit

### Estrutura (Semanas 1-2)
- [ ] Renomear diretório para `Maximus-V2`
- [ ] Criar novos 3 services (metacognitive_reflector, episodic_memory, api_gateway minimal)
- [ ] Refatorar 8 CORE services para compliance total
- [ ] Atualizar docker-compose.yml (apenas CORE)
- [ ] Criar .gitignore adequado
- [ ] Documentação completa (README, CODE_CONSTITUTION, etc.)

### Qualidade (Semana 3)
- [ ] Passar todos os testes automatizados
- [ ] mypy --strict: 0 erros
- [ ] pylint: score ≥ 9.5 em todos os files
- [ ] Nenhum arquivo > 400 linhas
- [ ] Zero TODOs/FIXMEs
- [ ] Coverage de testes ≥ 80%

### Aprovação Final (Semana 4)
- [ ] Ethical audit service valida todos os serviços
- [ ] Review de arquitetura (Juan)
- [ ] Verificação 4 PILARES completa
- [ ] Documentação revisada

### Commit Inicial
```bash
cd /home/juan/Maximus-V2
git init
git add .
git commit -m "🎉 Initial commit - MAXIMUS 2.0

Constitutional Meta-Cognitive AI that Manages Agents

✅ 10 CORE services - 100% constitutional compliance
✅ 4 PILARES enforced rigorously
✅ Zero technical debt
✅ Production ready

Services:
- meta_orchestrator (Agent coordination - ROMA)
- 4x HCL services (Infrastructure management)
- 3x Consciousness (TIG Fabric, decision making)
- 2x Immune (Ethics, threat response)
- 3x NEW (metacognitive_reflector, episodic_memory, api_gateway)

Philosophy: Clean, Simple, Methodical, Standard.
Legacy services archived to DATA disk for future plugin integration."

# Criar repositório no GitHub/GitLab
gh repo create Maximus-V2 --public --source=. --remote=origin --push
```

---

## 🚀 Próximos Passos (Ordem)

### AGORA (Hoje)
1. ✅ Renomear `/home/juan/vertice-dev` → `/home/juan/Maximus-V2`
2. ✅ Atualizar documentação com novo caminho
3. ✅ Criar link simbólico temporário

### Semana 1 (Dez 1-7)
- Criar 3 novos CORE services
- Começar refatoração dos 8 services existentes
- Atualizar docker-compose.yml

### Semana 2 (Dez 8-14)
- Completar refatoração
- Implementar testes unitários
- Validação mypy/pylint

### Semana 3 (Dez 15-21)
- Auditoria final 4 PILARES
- Documentação completa
- Ethical audit approval

### Semana 4 (Dez 22-28)
- Review final (Juan)
- **COMMIT INICIAL** 🎉
- Push para repositório remoto
- Celebração! 🍾

---

## 📏 Métricas de Sucesso

### Antes (vertice-dev)
- 76 services
- 642MB
- ~2.3M linhas
- 2.7% constitutional compliance
- Status: 🔴 FRANKENSTEIN

### Depois (Maximus-V2) - Meta
- 13 services (10 + 3 novos)
- < 200MB
- < 20K linhas
- 100% constitutional compliance
- Status: 🟢 CONSTITUTIONAL AI

---

## 🔄 Rollback (Se Necessário)

```bash
# Reverter renomeação
sudo mv /home/juan/Maximus-V2 /home/juan/vertice-dev
rm /home/juan/vertice-dev  # Remove symbolic link if created

# Restaurar services do backup
cp -r /media/juan/DATA/backups/maximus-legado-services-2025-11-30/* \
      /home/juan/vertice-dev/backend/services/
```

---

## 📝 Princípios para Maximus-V2

> "We are not building a Frankenstein.  
> We are building a Constitutional Meta-Cognitive AI that Manages Agents.  
> Everything else is LEGADO."

**Valores**:
1. **Clarity** - Cada service tem UMA responsabilidade clara
2. **Constitutional** - TODO código segue 4 PILARES rigorosamente
3. **Minimal** - Se não é CORE, é LEGADO/Plugin
4. **Extensible** - Plugins, não bloat
5. **Maintainable** - Desenvolvedores futuros nos agradecem

**Regras de Ouro**:
- ❌ NUNCA adicionar service sem aprovação constitucional
- ❌ NUNCA criar arquivo > 400 linhas
- ❌ NUNCA fazer commit com TODOs
- ❌ NUNCA pular validação mypy/pylint
- ✅ SEMPRE documentar decisões arquitetônicas
- ✅ SEMPRE refatorar antes de estender
- ✅ SEMPRE pensar: "Isso é CORE ou Plugin?"

---

**Status**: 🟡 Pronto para renomear → Maximus-V2  
**Próxima Ação**: Executar renomeação e começar refatoração  
**Commit Inicial**: Apenas após 100% compliance (Semana 4)
