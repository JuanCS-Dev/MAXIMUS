#!/bin/bash
# Batch migrate all remaining files

cd /media/juan/DATA/projetos/PROJETO-MAXIMUS-AGENTIC/backend/services

total_migrated=0
total_remaining=0

echo "🔄 Migrando arquivos restantes em consciousness/ e governance/..."
echo

while IFS= read -r file; do
    result=$(python3 migrate_prints.py "$file" 2>&1)
    migrated=$(echo "$result" | grep "Prints migrated:" | awk '{print $3}')
    remaining=$(echo "$result" | grep "Prints remaining:" | awk '{print $3}')

    if [ -n "$migrated" ]; then
        total_migrated=$((total_migrated + migrated))
        total_remaining=$((total_remaining + remaining))

        if [ "$remaining" -eq 0 ]; then
            echo "✅ $(basename $file): $migrated prints"
        else
            echo "⚠️  $(basename $file): $migrated/$((migrated + remaining)) prints"
        fi
    fi
done < <(find maximus_core_service/consciousness/ maximus_core_service/governance/ -name "*.py" -type f -exec grep -l "print(" {} \; 2>/dev/null)

echo
echo "📊 Total: $total_migrated prints migrados, $total_remaining pendentes"
