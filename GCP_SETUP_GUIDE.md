# GCP Migration Setup Guide

Complete step-by-step guide to migrate Aperta from local storage to Google Cloud Platform.

## Prerequisites

1. GCP Project with billing enabled
2. Service account with appropriate permissions
3. GCS bucket created
4. Cloud SQL instance (PostgreSQL) created

---

## Part 1: GCP Setup

### 1.1 Create GCS Bucket

```bash
# Create bucket for ChromaDB embeddings
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://aperta-storage

# Set appropriate permissions
gsutil iam ch serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com:objectAdmin gs://aperta-storage
```

### 1.2 Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create aperta-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=YOUR_STRONG_PASSWORD

# Create database
gcloud sql databases create aperta_db --instance=aperta-db

# Get connection name
gcloud sql instances describe aperta-db --format="value(connectionName)"
# Save this! Format: project-id:region:instance-name
```

### 1.3 Create Service Account

```bash
# Create service account
gcloud iam service-accounts create aperta-backend \
    --description="Aperta backend service account" \
    --display-name="Aperta Backend"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:aperta-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:aperta-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create ./aperta-service-account.json \
    --iam-account=aperta-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Move key to backend directory
mv ./aperta-service-account.json /Users/jedrzejcader/echopear/Aperta/backend/
```

---

## Part 2: Update .env File

Add these variables to `/Users/jedrzejcader/echopear/Aperta/backend/.env`:

```bash
# ============================================================================
# GCP CONFIGURATION
# ============================================================================

# GCP Project
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1

# Google Cloud Storage (for ChromaDB embeddings)
GCP_BUCKET_NAME=aperta-storage
GCP_SERVICE_ACCOUNT_JSON=/Users/jedrzejcader/echopear/Aperta/backend/aperta-service-account.json
USE_GCS_FOR_CHROMA=true

# Cloud SQL PostgreSQL
CLOUD_SQL_INSTANCE_CONNECTION_NAME=your-project:us-central1:aperta-db
CLOUD_SQL_DATABASE_NAME=aperta_db
CLOUD_SQL_USER=postgres
CLOUD_SQL_PASSWORD=your-strong-password

# ============================================================================
# DATABASE URL (SWITCH TO CLOUD SQL)
# ============================================================================

# Comment out SQLite (for local development only)
# DATABASE_URL=sqlite+aiosqlite:///./aperta.db

# Use this for Cloud SQL (will be constructed automatically by cloud_sql.py)
# DATABASE_URL will be overridden when cloud SQL is detected
```

---

## Part 3: Install Dependencies

```bash
cd /Users/jedrzejcader/echopear/Aperta/backend

# Activate venv
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

---

## Part 4: Run Migration

```bash
# Make migration script executable
chmod +x scripts/migrate_to_gcp.py

# Run migration
python scripts/migrate_to_gcp.py
```

This will:
1. ✅ Export all data from SQLite
2. ✅ Create tables in Cloud SQL
3. ✅ Import all data to Cloud SQL
4. ✅ Sync ChromaDB embeddings to GCS
5. ✅ Backup SQLite file to GCS (for safety)

---

## Part 5: Update Database Session (Automatic)

The database session will automatically detect Cloud SQL configuration and use it.

No code changes needed! Just ensure Cloud SQL env vars are set.

---

## Part 6: Test the Migration

```bash
# Start backend with Cloud SQL
uvicorn main:app --reload --port 8000
```

Check logs for:
- ✅ "Connecting to Cloud SQL: your-project:us-central1:aperta-db"
- ✅ "Cloud SQL engine created successfully"
- ✅ "GCS client initialized for bucket: aperta-storage"

Test the app:
1. Open http://localhost:5173
2. Check conversations load
3. Ask a question
4. Create a new conversation

---

## Part 7: Verify Data

```bash
# Connect to Cloud SQL to verify data
gcloud sql connect aperta-db --user=postgres --quiet

# In psql:
\c aperta_db
\dt
SELECT COUNT(*) FROM conversations;
SELECT COUNT(*) FROM qa_interactions;
\q
```

---

## Part 8: Clean Up Local Files (After Verification)

Once everything works:

```bash
# Backup locally first (optional)
cp aperta.db aperta.db.backup
cp -r chroma_db chroma_db.backup

# Remove local files (they're now in GCP)
rm aperta.db
rm -rf chroma_db/
```

---

## Troubleshooting

### Connection Issues

```bash
# Test Cloud SQL connection
gcloud sql connect aperta-db --user=postgres

# Check service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:aperta-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com"
```

### GCS Access Issues

```bash
# Test GCS access
gsutil ls gs://aperta-storage/

# Check bucket permissions
gsutil iam get gs://aperta-storage/
```

### Migration Failed

Check the logs in `/Users/jedrzejcader/echopear/Aperta/backend/` and re-run:

```bash
python scripts/migrate_to_gcp.py
```

---

## Cost Estimation

- **Cloud SQL** (db-f1-micro): ~$7-10/month
- **GCS Storage** (Standard): ~$0.02/GB/month
- **Cloud SQL Backup**: ~$0.08/GB/month

For development: ~$10-15/month
For production: Scale up instance as needed

---

## Rollback

If you need to rollback to local storage:

1. Restore SQLite backup: `cp aperta.db.backup aperta.db`
2. Restore ChromaDB: `cp -r chroma_db.backup chroma_db`
3. Update .env: Comment out Cloud SQL vars, uncomment SQLite
4. Restart backend

---

## Environment Variables Summary

```bash
# Required for GCP Migration
GCP_PROJECT_ID=your-project-id
GCP_BUCKET_NAME=aperta-storage
GCP_SERVICE_ACCOUNT_JSON=./aperta-service-account.json
CLOUD_SQL_INSTANCE_CONNECTION_NAME=project:region:instance
CLOUD_SQL_PASSWORD=your-password
USE_GCS_FOR_CHROMA=true
```

That's it! Your Aperta backend is now running on Google Cloud Platform. 🎉
