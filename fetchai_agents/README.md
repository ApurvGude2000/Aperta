# Fetch.ai Agentverse Integration

This directory contains Fetch.ai agent wrappers for deploying Aperta's AI agents to the Fetch.ai Agentverse decentralized agent marketplace.

## Overview

**What this does:**
- Exposes 8 core Aperta agents as Fetch.ai uAgents
- Enables monetization via FET token payments
- Makes agents discoverable on Fetch.ai marketplace
- Maintains zero modifications to existing backend code

**Architecture:**
- Fetch.ai agents are thin HTTP wrappers
- All heavy lifting done by existing FastAPI backend
- Agents call `localhost:8000` endpoints
- Backend runs completely unchanged

## Deployed Agents

### Core 4 (Post-Event Processing)
1. **Context Understanding** (`context_agent.py`) - Extracts entities, topics, insights
2. **Privacy Guardian** (`privacy_agent.py`) - Redacts PII from transcripts
3. **Follow-Up Generator** (`followup_agent.py`) - Creates personalized follow-up messages
4. **Cross-Pollination** (`crosspoll_agent.py`) - Suggests strategic introductions

### Q&A System (4 agents)
5. **Q&A Router** (`qa_router_agent.py`) - Routes questions to appropriate agents
6. **Conversation Retrieval** (`retrieval_agent.py`) - Semantic search over history
7. **Insight Analyzer** (`insight_agent.py`) - Pattern/trend analysis
8. **Response Composer** (`composer_agent.py`) - Synthesizes final answers

## Setup

### 1. Install Dependencies

```bash
cd /Users/jedrzejcader/echopear/Aperta/fetchai_agents
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
- `FETCHAI_API_KEY` - Your Fetch.ai API key
- `AGENT_SEED` - Random seed (min 32 chars) for agent identity
- `BACKEND_API_URL` - URL of FastAPI backend (default: `http://localhost:8000`)

### 3. Start Backend

In a separate terminal:

```bash
cd /Users/jedrzejcader/echopear/Aperta/backend
python main.py
```

Backend must be running on `http://localhost:8000` for agents to function.

### 4. Start Fetch.ai Agents

```bash
source venv/bin/activate
python main.py
```

You should see:
```
✓ Context Understanding Agent registered
✓ Privacy Guardian Agent registered
✓ Follow-Up Generator Agent registered
✓ Cross-Pollination Agent registered
✓ Q&A Router Agent registered
✓ Conversation Retrieval Agent registered
✓ Insight Analyzer Agent registered
✓ Response Composer Agent registered

🚀 All agents ready. Starting bureau...
```

## Local Testing

### Test Privacy Agent

```python
from uagents import Agent, Context
from protocols.privacy_protocol import PrivacyRedactionRequest
import asyncio

async def test():
    client = Agent(name="test_client", seed="test_seed_12345678901234567890")

    await client.send(
        "agent1q...",  # privacy agent address (check logs)
        PrivacyRedactionRequest(
            transcript="Call me at 555-1234 or email john@example.com",
            redact_emails=True,
            redact_phones=True
        )
    )

asyncio.run(test())
```

### Test Q&A Router

```python
from protocols.qa_protocol import QARequest

async def test_qa():
    client = Agent(name="qa_test", seed="qa_test_seed_12345678901234567890")

    await client.send(
        "agent1q...",  # qa_router agent address
        QARequest(
            question="Who did I meet at the conference last week?",
            use_rag=True
        )
    )

asyncio.run(test_qa())
```

## Deployment to Agentverse

### Option A: Hosted Deployment

1. Go to [agentverse.ai](https://agentverse.ai)
2. Connect your wallet
3. Upload agent code
4. Configure pricing
5. Publish to marketplace

### Option B: Self-Hosted

1. Deploy to a server with public IP
2. Ensure ports 8000-8008 are accessible
3. Run with systemd or supervisor:

```ini
[program:fetchai_agents]
command=/path/to/venv/bin/python /path/to/main.py
directory=/path/to/fetchai_agents
autostart=true
autorestart=true
```

4. Register agents on Agentverse:

```bash
uagents register context_understanding \
  --address <agent_address> \
  --price 0.10 \
  --description "Extract entities and insights from conversations"
```

## Pricing

Default pricing (in FET tokens):

| Agent | Price per Request |
|-------|------------------|
| Context Understanding | 0.10 FET |
| Privacy Redaction | 0.05 FET |
| Follow-Up Generation | 0.08 FET |
| Cross-Pollination | 0.15 FET |
| Q&A Routing | 0.03 FET |
| Retrieval | 0.05 FET |
| Insight Analysis | 0.12 FET |
| Response Composition | 0.05 FET |

Adjust in `.env` or `config.py`.

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│   Fetch.ai Agentverse Marketplace       │
│   (Users discover and pay for agents)   │
└─────────────────┬───────────────────────┘
                  │
                  │ FET Token Payment
                  │
┌─────────────────▼───────────────────────┐
│   Fetch.ai Agent Bureau (main.py)       │
│   ┌─────────────────────────────────┐   │
│   │  context_agent (port 8001)      │   │
│   │  privacy_agent (port 8002)      │   │
│   │  followup_agent (port 8003)     │   │
│   │  crosspoll_agent (port 8004)    │   │
│   │  qa_router_agent (port 8005)    │   │
│   │  retrieval_agent (port 8006)    │   │
│   │  insight_agent (port 8007)      │   │
│   │  composer_agent (port 8008)     │   │
│   └─────────────┬───────────────────┘   │
└─────────────────┼───────────────────────┘
                  │
                  │ HTTP POST
                  │
┌─────────────────▼───────────────────────┐
│   FastAPI Backend (port 8000)           │
│   /conversations, /qa, /search, etc.    │
│                                          │
│   ┌──────────────────────────────────┐  │
│   │  Backend Agents (Unchanged)      │  │
│   │  - ContextUnderstandingAgent     │  │
│   │  - PrivacyGuardianAgent          │  │
│   │  - FollowUpAgent                 │  │
│   │  - CrossPollinationAgent         │  │
│   │  - QAOrchestrator                │  │
│   └──────────────────────────────────┘  │
└──────────────────┬──────────────────────┘
                   │
                   │ Claude Opus 4.6 API
                   │
┌──────────────────▼──────────────────────┐
│   Anthropic API                          │
│   (Claude Opus 4.6)                      │
└──────────────────────────────────────────┘
```

## File Structure

```
fetchai_agents/
├── .env.example          # Environment template
├── config.py             # Configuration management
├── main.py               # Bureau entry point
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── protocols/            # Message schemas
│   ├── __init__.py
│   ├── context_protocol.py
│   ├── privacy_protocol.py
│   ├── followup_protocol.py
│   ├── crosspoll_protocol.py
│   └── qa_protocol.py
└── agents/              # Agent implementations
    ├── __init__.py
    ├── context_agent.py
    ├── privacy_agent.py
    ├── followup_agent.py
    ├── crosspoll_agent.py
    ├── qa_router_agent.py
    ├── retrieval_agent.py
    ├── insight_agent.py
    └── composer_agent.py
```

## Monitoring

Check agent logs for requests:

```bash
# In the terminal running main.py
# You'll see logs like:
# 2026-02-15 09:30:45 - context_understanding - INFO - Received context extraction request
# 2026-02-15 09:30:47 - context_understanding - INFO - Context extraction completed in 1.85s
```

Check backend logs for API calls:

```bash
tail -f /Users/jedrzejcader/echopear/Aperta/backend/logs/backend.log
```

## Troubleshooting

### Agents fail to start
- Check `.env` file exists and has valid values
- Ensure `AGENT_SEED` is at least 32 characters
- Verify ports 8000-8008 are available

### Backend connection errors
- Ensure FastAPI backend is running on `http://localhost:8000`
- Check `BACKEND_API_URL` in `.env`
- Test backend health: `curl http://localhost:8000/health`

### Payment verification fails
- Set `ENABLE_PAYMENT_VERIFICATION=false` for testing
- Ensure Fetch.ai wallet is funded for production

## Next Steps

1. **Test locally** with both backend and agents running
2. **Deploy to staging** on a test server
3. **Register on Agentverse** and configure pricing
4. **Publish to marketplace** and monitor usage
5. **Scale as needed** based on demand

## Support

- Fetch.ai Docs: https://docs.fetch.ai
- uAgents Framework: https://github.com/fetchai/uAgents
- Agentverse: https://agentverse.ai

---

**Note:** This integration does NOT modify any existing backend code. The FastAPI webapp continues running unchanged. Fetch.ai agents are external HTTP clients.
