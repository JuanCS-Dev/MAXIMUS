#!/usr/bin/env bash
"""
Start Qdrant and run migration
===============================

1. Start Qdrant container
2. Wait for health check
3. (Optional) Run migration from ChromaDB
"""

set -e

echo "🚀 Starting Qdrant Vector Database..."

# Start Qdrant container
docker compose up -d qdrant

# Wait for Qdrant to be healthy
echo "⏳ Waiting for Qdrant to be ready..."
timeout 30 bash -c 'until curl -s http://localhost:6333/health > /dev/null; do sleep 1; done'

echo "✅ Qdrant is ready!"
echo "📊 Management UI: http://localhost:6333/dashboard"

# Optional: Run migration
read -p "Run ChromaDB → Qdrant migration? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🔄 Running migration (dry-run first)..."
    python scripts/migrate_chromadb_to_qdrant.py --dry-run
    
    read -p "Proceed with actual migration? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        python scripts/migrate_chromadb_to_qdrant.py
        echo "✅ Migration complete!"
    fi
fi

echo "🎉 Qdrant setup complete!"
