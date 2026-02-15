# Supabase Setup Guide

Complete setup guide for using Supabase PostgreSQL with Aperta.

---

## What is Supabase?

**Supabase** is an open-source Firebase alternative that provides:
- ✅ PostgreSQL database (cloud-hosted)
- ✅ Real-time subscriptions
- ✅ Authentication (built-in)
- ✅ Row-level security (RLS)
- ✅ SQL editor in dashboard
- ✅ Storage (for files)
- ✅ Vector embeddings (pgvector)

**Perfect for:** Production deployments, scalability, managed database

---

## Step 1: Create Supabase Account

1. Visit https://supabase.com
2. Click **"Start your project"**
3. Sign up with email or GitHub
4. Create a new organization (or use existing)
5. Create a new project:
   - **Project name:** `aperta` (or your choice)
   - **Database password:** Create a strong password (you'll need this)
   - **Region:** Choose closest to your users
   - **Plan:** Start (free tier is perfect for development)

**Save these details:**
- Project URL: `https://xxxxx.supabase.co`
- Database password: `your-secure-password`

---

## Step 2: Get Connection Details

Once your project is created:

1. Go to **Project Settings** (gear icon, bottom left)
2. Go to **Database** tab
3. Find **Connection string** section
4. Copy the PostgreSQL connection string (for Psycopg)

Format will look like:
```
postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

**Keep this safe** - it contains your database password!

---

## Step 3: Configure Aperta

### Option A: Using Environment Variables (Recommended)

Add to your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_PASSWORD=your-secure-database-password
```

**Where to find:**
- `SUPABASE_URL`: Project Settings → API → Project URL
- `SUPABASE_KEY`: Project Settings → API → anon public
- `SUPABASE_DB_PASSWORD`: Your database password from Step 1

### Option B: Direct Connection String

If you prefer to specify the full connection string directly:

```env
DATABASE_URL=postgresql+asyncpg://postgres:your-password@db.xxxxx.supabase.co:5432/postgres
```

**Note:** This method requires you to manage the password in the connection string.

---

## Step 4: Install Dependencies

The async PostgreSQL driver is already in `requirements.txt`, but make sure to install:

```bash
pip install -r backend/requirements.txt
```

Specifically, this installs:
- `asyncpg>=0.29.0` - PostgreSQL async driver
- `sqlalchemy==2.0.36` - ORM
- `alembic==1.13.1` - Migrations

---

## Step 5: Create Tables

When you start the backend for the first time, it will automatically create all tables:

```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_KEY="your-key"
export SUPABASE_DB_PASSWORD="your-password"

python backend/main.py
```

The server will:
1. Detect Supabase credentials
2. Build the PostgreSQL connection string
3. Create all tables from your models
4. Start serving on `http://localhost:8000`

**Check the logs** - you should see:
```
INFO: Database tables created successfully
```

---

## Step 6: Verify Connection

### Check in Supabase Dashboard

1. Go to https://supabase.com
2. Open your project
3. Go to **SQL Editor** (left sidebar)
4. Run:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

You should see all your tables:
- `conversations`
- `participants`
- `entities`
- `action_items`
- `privacy_audit_logs`
- `follow_up_messages`
- `user_goals`
- `opportunities`
- `qa_sessions`
- `qa_interactions`

### Check in Python

```python
from sqlalchemy import text
from db.session import AsyncSessionLocal

async def check_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        print("✅ Connection successful!")
```

---

## How It Works

### Auto-Configuration

When you set `SUPABASE_URL` and `SUPABASE_DB_PASSWORD`:

```python
# config.py automatically builds:
database_url = (
    f"postgresql+asyncpg://postgres:{supabase_db_password}"
    f"@db.{supabase_host}:5432/postgres"
)
```

This creates an async PostgreSQL connection that works with SQLAlchemy.

### Connection Flow

```
Aperta Backend
    ↓
SQLAlchemy + asyncpg
    ↓
Supabase PostgreSQL
    ↓
Your Data (conversations, participants, etc.)
```

---

## Configuration Options

### Development (SQLite Local)
```env
# No configuration needed - uses SQLite by default
# DATABASE_URL=sqlite+aiosqlite:///./networkai.db
```

### Production (Supabase)
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_PASSWORD=your-database-password
```

### Direct PostgreSQL URL
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@host:5432/database
```

---

## API Endpoints Work the Same

All your existing endpoints work unchanged:

```bash
# Upload audio (saves to local FS or S3)
curl -X POST http://localhost:8000/audio/process \
  -F "file=@meeting.wav"

# Get conversation (from Supabase)
curl http://localhost:8000/conversations/conv_123

# Create conversation (saves to Supabase)
curl -X POST http://localhost:8000/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Meeting with John",
    "transcript": "..."
  }'
```

**The only difference:** Data is now persisted in Supabase instead of local SQLite.

---

## Supabase Features You Can Use

### 1. SQL Editor

Query your data directly:
```sql
-- Find all conversations
SELECT id, title, created_at FROM conversations ORDER BY created_at DESC;

-- Get conversation details with participants
SELECT c.title, p.name, p.email
FROM conversations c
JOIN participants p ON c.id = p.conversation_id;

-- Get speaker statistics
SELECT p.name, COUNT(*) as segment_count
FROM participants p
GROUP BY p.name;
```

### 2. Row-Level Security (RLS)

Restrict data by user:
```sql
-- Example: Only allow users to see their own conversations
CREATE POLICY "Users can view own conversations"
ON conversations FOR SELECT
USING (user_id = auth.uid());
```

### 3. Real-time Subscriptions

Listen for changes in real-time (future enhancement):
```python
# Example (not yet implemented):
await supabase.channel("conversations")
    .on("postgres_changes", {"event": "*"}, callback)
    .subscribe()
```

### 4. Storage Buckets

Store audio files in Supabase Storage (alternative to S3):
```python
# Upload to Supabase Storage instead of S3
await supabase.storage.from_("audio-files").upload(
    f"conversation/{file_name}",
    file_content
)
```

### 5. Backups

Automatic daily backups (included in free tier):
- Go to **Project Settings → Backups**
- See automatic backup history
- Restore from any backup with one click

---

## Troubleshooting

### Issue: "Connection refused"

**Cause:** Supabase credentials not set

**Solution:**
1. Check environment variables: `echo $SUPABASE_URL`
2. Verify credentials in Supabase dashboard
3. Make sure project is active (not paused)

### Issue: "authentication failed for user 'postgres'"

**Cause:** Wrong database password

**Solution:**
1. Go to Supabase Dashboard
2. Project Settings → Database
3. Click "Reset database password"
4. Update `SUPABASE_DB_PASSWORD` in `.env`
5. Restart backend

### Issue: "relation 'conversations' does not exist"

**Cause:** Tables not created yet

**Solution:**
1. Tables auto-create on first server startup
2. Check logs for "Database tables created successfully"
3. Manually create tables if needed:
```bash
python -c "
from db.session import init_db
import asyncio
asyncio.run(init_db())
"
```

### Issue: "SSL error"

**Cause:** SSL certificate verification issue

**Solution:**
1. Supabase uses SSL by default (secure)
2. This is expected and safe
3. Ensure you have `asyncpg>=0.29.0` installed

---

## Switching Between Databases

### From SQLite to Supabase

1. **Export data from SQLite** (optional):
```bash
# Backup SQLite database
cp networkai.db networkai_backup.db
```

2. **Set Supabase credentials** in `.env`

3. **Restart backend**
   - Tables will be created in Supabase
   - Old SQLite data is still local (not migrated)

4. **Migrate data** (optional):
```bash
# Export from SQLite
sqlite3 networkai.db .dump > export.sql

# Import to Supabase (manual in SQL Editor)
# Edit and import schema + data
```

### From Supabase back to SQLite

1. **Remove Supabase variables** from `.env`

2. **Restart backend**
   - Uses SQLite (local)

3. **Old Supabase data** is still in cloud (not deleted)

---

## Cost Estimate

### Supabase Pricing

**Free Tier:**
- Database: Unlimited (up to 500MB)
- Storage: 1GB
- Real-time API: Limited queries
- Monthly costs: $0 ✅

**Pro Tier (when you grow):**
- Database: $25/month
- Storage: +$5 per 100GB
- Custom limits

**For Aperta:**
- Small deployment (< 1,000 conversations): Free tier
- Medium deployment (10,000 conversations): ~$25-50/month
- Large deployment: Contact Supabase for pricing

---

## Production Deployment

### 1. Upgrade to Pro Plan
- More reliable backups
- Higher connection limits
- Priority support

### 2. Enable Row-Level Security (RLS)
- Restrict data per user
- Secure multi-tenant setup

### 3. Set Up Backups
- Daily automatic backups included
- Can manually trigger backups
- Restore to any point in time

### 4. Monitor Performance
- Supabase dashboard shows query times
- View active connections
- Set up alerts

### 5. Use Custom Domain (optional)
- Point your domain to Supabase
- Use with your application

---

## Supabase vs S3 Storage

### For Audio Files

**Supabase Storage:**
- ✅ Same region as database (faster)
- ✅ RLS integration (security)
- ✅ Unified dashboard
- ❌ Slightly more expensive
- ❌ Smaller free tier (1GB)

**AWS S3:**
- ✅ Global CDN available
- ✅ Very cheap ($0.023/GB)
- ✅ Large free tier
- ❌ Separate service to manage
- ❌ No RLS

**Recommendation:** Use Supabase Storage for audio files (same infrastructure), S3 if you want ultra-cheap storage.

---

## Next Steps

1. ✅ Create Supabase account
2. ✅ Get connection details
3. ✅ Set environment variables
4. ✅ Install dependencies
5. ✅ Start backend (creates tables)
6. ✅ Test uploads (saves to local FS or S3, data to Supabase)
7. ⏳ Deploy to production
8. ⏳ Set up RLS and backups

---

## Useful Supabase Resources

- **Dashboard:** https://supabase.com/dashboard
- **Documentation:** https://supabase.com/docs
- **SQL Editor:** Built into dashboard
- **API Reference:** Project Settings → API
- **Community:** https://discord.supabase.io

---

## Quick Reference

### Set Environment Variables
```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_KEY="your-anon-key"
export SUPABASE_DB_PASSWORD="your-database-password"
```

### Start Backend
```bash
python backend/main.py
```

### Test Connection
```bash
curl http://localhost:8000/health
```

### View Data in Supabase
1. Go to Supabase Dashboard
2. Click SQL Editor
3. Query your data

### Reset Database
```bash
# Go to Project Settings → Database → Reset Database
# (WARNING: This deletes all data!)
```

---

## Support

- **Questions about Supabase?** → https://supabase.com/docs
- **Issues with Aperta?** → Check `LOCAL_CHANGES.md`
- **Database connection issues?** → Check configuration in `config.py`

