#!/bin/bash
# Deploy Aperta backend to Cloud Run

cd "$(dirname "$0")"

gcloud run deploy aperta-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --env-vars-file=env.yaml
