#!/usr/bin/env bash
#
# Build and Push Docker Images
# =============================
# 
# Builds all Maximus services and pushes to GCloud Artifact Registry.
#
# Usage:
#   ./build-and-push.sh YOUR_PROJECT_ID [REGION]

set -e

PROJECT_ID="${1:-maximus-prod}"
REGION="${2:-us-central1}"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/maximus-docker"

echo "🐳 Building and pushing Docker images..."
echo "Registry: $REGISTRY"
echo ""

# Services to build
SERVICES=(
    "hcl-planner"
    "hcl-executor"
    "meta-orchestrator"
    "metacognitive-reflector"
    "episodic-memory"
)

for SERVICE in "${SERVICES[@]}"; do
    echo "📦 Building $SERVICE..."
    
    # Build
    docker build \
        -t "${REGISTRY}/${SERVICE}:latest" \
        -t "${REGISTRY}/${SERVICE}:$(git rev-parse --short HEAD)" \
        -f "backend/services/${SERVICE//-/_}/Dockerfile" \
        "backend/services/${SERVICE//-/_}"
    
    # Push
    echo "⬆️  Pushing $SERVICE..."
    docker push "${REGISTRY}/${SERVICE}:latest"
    docker push "${REGISTRY}/${SERVICE}:$(git rev-parse --short HEAD)"
    
    echo "✅ $SERVICE pushed!"
    echo ""
done

echo "✅ All images built and pushed!"
echo ""
echo "📋 Images pushed:"
for SERVICE in "${SERVICES[@]}"; do
    echo "  - ${REGISTRY}/${SERVICE}:latest"
done
echo ""
echo "🚀 Ready to deploy: kubectl apply -f deployments/kubernetes/"
