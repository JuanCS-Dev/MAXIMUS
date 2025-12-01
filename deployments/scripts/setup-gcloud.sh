#!/usr/bin/env bash
#
# GCloud Setup Script
# ===================
# 
# Prepares GCloud project for Maximus 2.0 deployment.
# RUN THIS FIRST before deploying.
#
# Usage:
#   ./setup-gcloud.sh YOUR_PROJECT_ID

set -e

PROJECT_ID="${1:-maximus-prod}"
REGION="${2:-us-central1}"
CLUSTER_NAME="maximus-cluster"

echo "🚀 Setting up GCloud for Maximus 2.0..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# 1. Set project
echo "1️⃣  Setting GCloud project..."
gcloud config set project "$PROJECT_ID"

# 2. Enable APIs
echo "2️⃣  Enabling required APIs..."
gcloud services enable \
    container.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    compute.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com

# 3. Create GKE Cluster
echo "3️⃣  Creating GKE cluster (this takes ~10 minutes)..."
gcloud container clusters create "$CLUSTER_NAME" \
    --region="$REGION" \
    --num-nodes=2 \
    --machine-type=e2-standard-2 \
    --disk-size=50 \
    --enable-autoscaling \
    --min-nodes=2 \
    --max-nodes=10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --release-channel=stable \
    --workload-pool="$PROJECT_ID.svc.id.goog" \
    --enable-ip-alias \
    --network="default" \
    --subnetwork="default" \
    --no-enable-basic-auth \
    --no-issue-client-certificate \
    --enable-stackdriver-kubernetes \
    --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver

echo "✅ GKE cluster created!"

# 4. Get cluster credentials
echo "4️⃣  Getting cluster credentials..."
gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"

# 5. Create Artifact Registry
echo "5️⃣  Creating Artifact Registry..."
gcloud artifacts repositories create maximus-docker \
    --repository-format=docker \
    --location="$REGION" \
    --description="Maximus 2.0 Docker images" || echo "Repository may already exist"

# 6. Configure Docker auth
echo "6️⃣  Configuring Docker authentication..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev"

# 7. Create service account
echo "7️⃣  Creating service account..."
gcloud iam service-accounts create maximus-sa \
    --display-name="Maximus 2.0 Service Account" || echo "SA may already exist"

# 8. Grant permissions
echo "8️⃣  Granting permissions..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:maximus-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:maximus-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter"

echo ""
echo "✅ GCloud setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set GEMINI_API_KEY in Kubernetes secrets"
echo "2. Build and push Docker images: ./build-and-push.sh $PROJECT_ID"
echo "3. Deploy to K8s: kubectl apply -f deployments/kubernetes/"
echo ""
echo "💰 Estimated costs:"
echo "  - GKE cluster (e2-standard-2 x2): ~$70/month"
echo "  - Persistent disk (10GB): ~$2/month"
echo "  - Total baseline: ~$72/month"
echo ""
