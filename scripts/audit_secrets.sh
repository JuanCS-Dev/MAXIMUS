#!/bin/bash
# audit_secrets.sh - Security Audit Script for MAXIMUS V2
# Usage: ./scripts/audit_secrets.sh

set -e

PROJECT_ROOT="/media/juan/DATA/projetos/PROJETO-MAXIMUS-AGENTIC"
cd "$PROJECT_ROOT"

echo "🔍 Auditoria de Segurança - MAXIMUS V2"
echo "======================================"
echo ""

# 1. Verificar .gitignore
echo "✓ Verificando .gitignore..."
if grep -q "^\.env$" .gitignore; then
    echo "  ✅ .env protegido"
else
    echo "  ⚠️  .env NÃO está no .gitignore!"
fi

if grep -q "^\*\.key$\|^\.key$\|keys/" .gitignore; then
    echo "  ✅ .key protegido"
else
    echo "  ⚠️  Adicione *.key ao .gitignore"
fi
echo ""

# 2. Verificar arquivos não trackeados
echo "✓ Arquivos não trackeados com possíveis secrets:"
UNTRACKED=$(git status --porcelain | grep "^??" | grep -E "\.env$|\.key$|\.pem$|secret" || true)
if [ -z "$UNTRACKED" ]; then
    echo "  ✅ Nenhum arquivo suspeito encontrado"
else
    echo "$UNTRACKED"
fi
echo ""

# 3. Verificar .env no histórico git
echo "✓ Verificando histórico do Git por .env..."
ENV_IN_HISTORY=$(git log --all --full-history -- "**/.env" --oneline 2>/dev/null || true)
if [ -z "$ENV_IN_HISTORY" ]; then
    echo "  ✅ .env nunca foi commitado"
else
    echo "  🚨 ALERTA: .env encontrado no histórico!"
    echo "$ENV_IN_HISTORY"
fi
echo ""

# 4. Scan de padrões de secrets no código
echo "✓ Procurando padrões de API keys hardcoded:"
HARDCODED=$(grep -r -n -E "(api_key|apikey|secret|password)\s*=\s*['\"][^'\"]{20,}['\"]" \
  --include="*.py" --include="*.js" --include="*.yaml" --include="*.yml" \
  --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir=".mypy_cache" \
  --exclude-dir="__pycache__" --exclude-dir="venv" --exclude-dir=".venv" \
  . 2>/dev/null || true)

if [ -z "$HARDCODED" ]; then
    echo "  ✅ Nenhuma key hardcoded encontrada"
else
    echo "  ⚠️  Possíveis secrets hardcoded:"
    echo "$HARDCODED" | head -10
fi
echo ""

# 5. Verificar permissões do diretório
echo "✓ Verificando permissões do diretório:"
PERMS=$(ls -ld . | awk '{print "  Permissões:", $1, "| Dono:", $3}')
echo "$PERMS"
echo ""

# 6. Verificar se .env existe localmente
echo "✓ Verificando arquivos .env locais:"
find . -name ".env" -not -path "*/node_modules/*" -not -path "*/.venv/*" 2>/dev/null | while read -r file; do
    echo "  📄 Encontrado: $file"
    if [ -r "$file" ]; then
        LINES=$(wc -l < "$file")
        echo "     ($LINES linhas)"
    fi
done
echo ""

# 7. Verificar se .env.example existe
echo "✓ Verificando templates .env.example:"
if find . -name ".env.example" -not -path "*/node_modules/*" | grep -q .; then
    echo "  ✅ Template(s) .env.example encontrado(s)"
else
    echo "  ⚠️  Nenhum .env.example encontrado (criar template)"
fi
echo ""

# Summary
echo "======================================"
echo "✅ Auditoria concluída!"
echo ""
echo "Próximos passos recomendados:"
echo "1. Revisar qualquer ⚠️  ou 🚨 acima"
echo "2. Trocar keys se houver suspeita de exposição"
echo "3. Executar 'gitleaks detect' se instalado"
echo ""
