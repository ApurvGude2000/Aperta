# Supabase Quick Start - 5 Minutes

## TL;DR - Use Supabase for Database

Your Aperta backend will now **automatically use Supabase PostgreSQL** if you provide credentials.

---

## Setup (5 minutes)

### 1. Create Supabase Account
- Go to https://supabase.com
- Sign up (free)
- Create a new project
- **Save:** Project URL and database password

### 2. Get Connection Details
- Go to **Project Settings → Database**
- Find "Connection string" section
- Note your database password

### 3. Add to .env File
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_PASSWORD=your-secure-password
```

### 4. Start Backend
```bash
pip install -r backend/requirements.txt
python backend/main.py
```

That's it! ✅

---

## What Happens

```
Backend starts
    ↓
Reads Supabase credentials
    ↓
Builds connection string
    ↓
Creates all tables in Supabase PostgreSQL
    ↓
Ready to use!
```

---

## Where Does Data Go?

| Type | Storage |
|------|---------|
| **Audio files** | Local FS (./uploads/) or S3 |
| **Transcripts** | Local FS or S3 |
| **Conversations** | ✅ **Supabase PostgreSQL** |
| **Speakers** | ✅ **Supabase PostgreSQL** |
| **Entities** | ✅ **Supabase PostgreSQL** |
| **Action Items** | ✅ **Supabase PostgreSQL** |

---

## API Usage (Same as Before)

Upload audio:
```bash
curl -X POST http://localhost:8000/audio/process \
  -F "file=@meeting.wav"
```

Get conversation:
```bash
curl http://localhost:8000/conversations/conv_123
```

Everything works the same - just stored in Supabase now!

---

## View Your Data

1. Open Supabase Dashboard
2. Go to **SQL Editor**
3. Run queries:

```sql
-- See all conversations
SELECT id, title, created_at FROM conversations;

-- See speakers
SELECT c.title, p.name, p.email
FROM conversations c
JOIN participants p ON c.id = p.conversation_id;

-- See action items
SELECT description, responsible_party FROM action_items;
```

---

## Configuration Options

### Supabase (Recommended for Production)
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-key
SUPABASE_DB_PASSWORD=your-password
```

### Direct PostgreSQL
```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db
```

### SQLite (Local Development)
```env
# Just don't set Supabase variables - uses SQLite by default
```

---

## Cost

**Free Tier** ✅
- Unlimited database (up to 500MB)
- 1GB storage
- Perfect for development

**When You Scale:**
- $25/month for Pro (more storage, backups, etc.)

---

## Next Steps

1. Create Supabase account (5 min)
2. Get connection details
3. Add to `.env` file
4. Start backend
5. Test uploads
6. View data in Supabase dashboard

**Full guide:** See `SUPABASE_SETUP.md`

---

## Troubleshooting

**"Connection refused"**
- Check credentials in `.env`
- Verify Supabase project is active

**"Authentication failed"**
- Wrong database password
- Reset in Supabase Dashboard → Database

**"Tables don't exist"**
- Backend creates them on first run
- Check logs for "Database tables created"

---

## That's It!

Your database is now in Supabase. Everything else works the same! 🎉

For detailed info, see `SUPABASE_SETUP.md`
