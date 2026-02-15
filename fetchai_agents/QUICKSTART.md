# Fetch.ai Agents - Quick Start Guide

Get your Fetch.ai agents running in 5 minutes.

## TL;DR

```bash
# 1. Setup
cd /Users/jedrzejcader/echopear/Aperta/fetchai_agents
./setup.sh

# 2. Configure
nano .env  # Add FETCHAI_API_KEY and AGENT_SEED

# 3. Start backend (separate terminal)
cd ../backend && python main.py

# 4. Start agents
source venv/bin/activate && python main.py

# 5. Test
python test_agents.py
```

## What You Get

✅ **8 monetized AI agents** ready for Fetch.ai marketplace:

1. **Context Understanding** (0.10 FET) - Extract entities and insights
2. **Privacy Guardian** (0.05 FET) - Redact PII from transcripts
3. **Follow-Up Generator** (0.08 FET) - Create personalized messages
4. **Cross-Pollination** (0.15 FET) - Suggest strategic introductions
5. **Q&A Router** (0.03 FET) - Route questions to right agents
6. **Conversation Retrieval** (0.05 FET) - Semantic search
7. **Insight Analyzer** (0.12 FET) - Pattern analysis
8. **Response Composer** (0.05 FET) - Synthesize answers

**Total potential:** 630 FET/month (1000 requests × 8 agents)

## Prerequisites

- Python 3.11+
- Running Aperta backend (`localhost:8000`)
- Fetch.ai account (sign up: [agentverse.ai](https://agentverse.ai))

## Step 1: Install

```bash
cd /Users/jedrzejcader/echopear/Aperta/fetchai_agents
./setup.sh
```

This creates a virtual environment and installs dependencies.

## Step 2: Configure

Edit `.env`:

```bash
# Required
FETCHAI_API_KEY=your_key_here
AGENT_SEED=$(openssl rand -hex 32)  # Generate 32+ char seed

# Optional
BACKEND_API_URL=http://localhost:8000
ENABLE_PAYMENT_VERIFICATION=false  # true for production
```

## Step 3: Start Services

**Terminal 1 - Backend:**
```bash
cd /Users/jedrzejcader/echopear/Aperta/backend
python main.py
# Wait for "NetworkAI Backend Ready"
```

**Terminal 2 - Agents:**
```bash
cd /Users/jedrzejcader/echopear/Aperta/fetchai_agents
source venv/bin/activate
python main.py
# Wait for "🚀 All agents ready. Starting bureau..."
```

## Step 4: Verify

```bash
python test_agents.py
```

Expected output:
```
✓ Backend is running
✓ Privacy agent responding
✓ Q&A router responding
✅ All tests passed!
```

## Step 5: Deploy to Agentverse

### Option A: Hosted (Easiest)

1. Zip your code:
```bash
zip -r fetchai_agents.zip . -x "venv/*" -x ".env"
```

2. Upload to [agentverse.ai/deploy](https://agentverse.ai/deploy)
3. Configure environment variables in UI
4. Publish to marketplace

### Option B: Self-Hosted

See [DEPLOYMENT.md](DEPLOYMENT.md) for full guide.

Quick version:
```bash
# On your server
git clone your-repo
cd fetchai_agents
./setup.sh
nano .env  # Configure

# Run with systemd (see DEPLOYMENT.md)
sudo systemctl start aperta-fetchai
```

## Architecture

```
User → Fetch.ai Agent → HTTP POST → FastAPI Backend → Claude Opus 4.6
```

**Key insight:** Fetch.ai agents are thin wrappers. All AI logic stays in your existing backend. Zero code duplication.

## Pricing Strategy

**Default pricing** (per request in FET):
- Simple ops (routing, retrieval): 0.03-0.05 FET
- Medium ops (context, privacy, follow-up): 0.05-0.10 FET
- Complex ops (cross-poll, insight): 0.12-0.15 FET

**Break-even analysis:**
- Cost per request: ~$0.50-2.00 (Claude API + server)
- Revenue per request: ~0.08 FET average
- At $0.50/FET: Need ~3000 requests/month to break even

**Adjust in `.env`:**
```bash
PRICE_CONTEXT_UNDERSTANDING=0.10
PRICE_PRIVACY_REDACTION=0.05
# etc.
```

## Common Issues

**"Backend is not running"**
→ Start backend first: `cd ../backend && python main.py`

**"Port already in use"**
→ Change `AGENT_PORT_START` in `.env`

**"Import errors"**
→ Reinstall: `pip install -r requirements.txt`

**"Agents not responding"**
→ Check logs for errors, verify backend URL

## What's Next?

1. ✅ Get agents running locally
2. 📊 Monitor usage patterns
3. 💰 Adjust pricing based on demand
4. 🚀 Deploy to production
5. 📈 Scale based on traffic

## Files Created

```
fetchai_agents/
├── .env.example          # Config template
├── .gitignore            # Git ignore
├── config.py             # Settings management
├── main.py               # Bureau runner
├── requirements.txt      # Dependencies
├── setup.sh              # Setup script
├── test_agents.py        # Test suite
├── README.md             # Full documentation
├── DEPLOYMENT.md         # Production guide
├── QUICKSTART.md         # This file
├── protocols/            # Message schemas (5 files)
└── agents/              # Agent implementations (8 files)
```

**Total: 24 new files, 0 modifications to existing code**

## Support

- 📖 Full docs: [README.md](README.md)
- 🚀 Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)
- 💬 Fetch.ai Discord: https://discord.gg/fetchai

---

**Ready to monetize? Start with `./setup.sh`**
