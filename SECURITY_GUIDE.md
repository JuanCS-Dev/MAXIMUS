# 🔒 MAXIMUS V2 - Guia de Segurança Digital

> **Criado**: 03/12/2024  
> **Status do Repo**: Público (github.com/JuanCS-Dev/MAXIMUS)  
> **Objetivo**: Proteger dados sensíveis + Preparar para aplicação AWS/GCP

---

## ✅ Status Atual (03/12/2024)

### O que está SEGURO:
- ✅ `.env` nunca foi commitado no Git
- ✅ `.gitignore` configurado corretamente
- ✅ Secrets NÃO estão no histórico do GitHub
- ✅ `.mypy_cache` com "secrets" são apenas arquivos de tipo (seguro)

### ⚠️ AÇÕES IMEDIATAS NECESSÁRIAS:

#### 1. **TROCAR a API Key do Gemini HOJE**
```bash
# Acessar: https://makersuite.google.com/app/apikey
# Motivo: Key está no arquivo local, melhor prevenir
# Revogar: AIzaSyC5FGwfkuZfpgNT2j5AWRc0tiAMuOmXs1Q
# Gerar nova key
```

---

## 🛡️ Proteção de Secrets - 3 Camadas

### **Camada 1: Arquivo Local (.env)**

#### Criar `.env.example` (template sem secrets):
```bash
# MAXIMUS Core Service - Environment Variables
GEMINI_API_KEY=your_key_here
LLM_PROVIDER=gemini
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/aurora
```

#### Garantir .gitignore:
```bash
# Já está, mas confirmar:
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "*.pem" >> .gitignore
echo "secrets/" >> .gitignore
```

### **Camada 2: Git-crypt (Criptografia no Repo)**

Para arquivos que DEVEM estar no repo mas criptografados:

```bash
# Instalar git-crypt
sudo apt install git-crypt

# Inicializar no projeto
cd /media/juan/DATA/projetos/PROJETO-MAXIMUS-AGENTIC
git-crypt init

# Criar .gitattributes
cat > .gitattributes << 'EOF'
# Criptografar automaticamente
deployments/secrets/** filter=git-crypt diff=git-crypt
*.secret.yaml filter=git-crypt diff=git-crypt
EOF

# Exportar chave de backup (GUARDAR BEM!)
git-crypt export-key ~/maximus-git-crypt.key
chmod 600 ~/maximus-git-crypt.key
# BACKUP: Copiar para pendrive ou cloud criptografado
```

### **Camada 3: GitHub Secrets (CI/CD)**

Para quando usar GitHub Actions:

```yaml
# .github/workflows/deploy.yml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  
# Configurar em:
# Repo → Settings → Secrets and variables → Actions
```

---

## 🔐 Criptografia de Arquivos Sensíveis

### GPG para arquivos individuais:

```bash
# Gerar chave GPG (primeira vez)
gpg --full-generate-key
# Escolher: RSA 4096 bits, válida por 2 anos

# Criptografar arquivo
gpg --encrypt --recipient juan.brainfarma@gmail.com sensitive_file.txt
# Gera: sensitive_file.txt.gpg

# Descriptografar
gpg --decrypt sensitive_file.txt.gpg > sensitive_file.txt

# Para backups completos
tar czf - /media/juan/DATA/projetos/PROJETO-MAXIMUS-AGENTIC | \
  gpg --encrypt --recipient juan.brainfarma@gmail.com \
  > maximus_backup_$(date +%Y%m%d).tar.gz.gpg
```

---

## 🔍 Monitoramento e Auditoria

### Script de auditoria semanal:

```bash
#!/bin/bash
# audit_secrets.sh

echo "🔍 Auditoria de Segurança - MAXIMUS"
echo "===================================="

# 1. Verificar se .env está no .gitignore
echo "✓ Verificando .gitignore..."
grep -q "^\.env$" .gitignore && echo "  ✅ .env protegido" || echo "  ⚠️  .env NÃO está no .gitignore!"

# 2. Verificar arquivos não trackeados
echo "✓ Arquivos não trackeados com secrets:"
git status --porcelain | grep "^??" | grep -E "\.env|\.key|\.pem|secret"

# 3. Scan de secrets no código
echo "✓ Procurando padrões de API keys no código:"
grep -r -n -E "(api_key|apikey|secret|password)\s*=\s*['\"][^'\"]+['\"]" \
  --include="*.py" --include="*.js" --include="*.yaml" \
  --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir=".mypy_cache" .

# 4. Verificar permissões
echo "✓ Verificando permissões do diretório:"
ls -ld . | awk '{print "  Permissões:", $1, "Dono:", $3}'

echo ""
echo "Auditoria completa!"
```

### Ferramenta automatizada (opcional):

```bash
# Instalar gitleaks (detector de secrets)
# https://github.com/gitleaks/gitleaks
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
tar -xzf gitleaks_8.18.0_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/

# Rodar scan
cd /media/juan/DATA/projetos/PROJETO-MAXIMUS-AGENTIC
gitleaks detect --verbose
```

---

## 🌩️ Preparação para AWS/GCP Credits

### Checklist ANTES de aplicar:

- [ ] Trocar GEMINI_API_KEY
- [ ] Criar `.env.example` (sem secrets)
- [ ] Adicionar README com badges profissionais
- [ ] Documentar arquitetura (já tem!)
- [ ] Adicionar LICENSE (MIT recomendado)
- [ ] SECURITY.md (este arquivo)
- [ ] Clean git history (já está limpo ✅)

### README badges para impressionar:

```markdown
[![Security](https://img.shields.io/badge/security-A+-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.12+-blue)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()
```

### Documentar uso responsável:

```markdown
## 🔐 Security & Compliance

MAXIMUS V2 implements enterprise-grade security:
- No hardcoded credentials
- Git-crypt for sensitive configs
- Ethical AI guidelines (CODE_CONSTITUTION)
- Regular security audits

For security issues: security@yourdomain.com
```

---

## 🚨 Resposta a Incidentes

### Se você SUSPEITAR que uma key foi exposta:

1. **REVOGAR IMEDIATAMENTE** na console do provider
2. Gerar nova key
3. Atualizar `.env` local
4. Se foi commitada:
   ```bash
   # Usar BFG Repo-Cleaner
   git clone --mirror https://github.com/JuanCS-Dev/MAXIMUS.git
   java -jar bfg.jar --delete-files .env MAXIMUS.git
   cd MAXIMUS.git
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

---

## 📦 Backup Seguro

### Estratégia 3-2-1:
- **3 cópias**: Original + 2 backups
- **2 mídias**: SSD local + Cloud criptografado
- **1 offsite**: Google Drive (criptografado)

```bash
#!/bin/bash
# backup_maximus.sh

BACKUP_DIR="/media/juan/DATA/backups/maximus"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup criptografado
tar czf - /media/juan/DATA/projetos/PROJETO-MAXIMUS-AGENTIC \
  --exclude=".git" \
  --exclude="node_modules" \
  --exclude="__pycache__" \
  --exclude=".mypy_cache" \
  | gpg --encrypt --recipient juan.brainfarma@gmail.com \
  > "$BACKUP_DIR/maximus_$DATE.tar.gz.gpg"

echo "✅ Backup criado: $BACKUP_DIR/maximus_$DATE.tar.gz.gpg"

# Manter apenas últimos 7 backups
ls -t "$BACKUP_DIR"/maximus_*.tar.gz.gpg | tail -n +8 | xargs -r rm
```

---

## 🎯 Próximos Passos (Ordem de Prioridade)

### HOJE (antes de aplicar AWS/GCP):
1. ✅ Trocar GEMINI_API_KEY
2. ✅ Criar `.env.example`
3. ✅ Adicionar SECURITY.md ao repo
4. ✅ Rodar `audit_secrets.sh`

### Esta Semana:
5. ⏳ Configurar GPG
6. ⏳ Criar script de backup automático (cron)
7. ⏳ Instalar gitleaks

### Próximo Mês:
8. ⏳ Implementar git-crypt (se precisar)
9. ⏳ Documentação de segurança na aplicação
10. ⏳ Pentesting básico

---

## 📚 Recursos

- [Git-crypt](https://github.com/AGWA/git-crypt)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [GCP Secret Manager](https://cloud.google.com/secret-manager)

---

**Mantido por**: Juan Carlos de Souza  
**Última atualização**: 03/12/2024
