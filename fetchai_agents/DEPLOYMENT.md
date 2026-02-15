# Fetch.ai Agentverse Deployment Guide

Complete guide for deploying Aperta agents to Fetch.ai's Agentverse marketplace.

## Prerequisites

- Python 3.11+
- Fetch.ai account (sign up at [agentverse.ai](https://agentverse.ai))
- FET tokens for gas fees
- Running Aperta backend

## Local Development Setup

### 1. Initial Setup

```bash
cd /Users/jedrzejcader/echopear/Aperta/fetchai_agents
./setup.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Create `.env` file from template

### 2. Configure Environment

Edit `.env`:

```bash
# Required
FETCHAI_API_KEY=fet_your_api_key_here
AGENT_SEED=your_random_32_char_seed_here_minimum_length

# Optional (defaults shown)
BACKEND_API_URL=http://localhost:8000
AGENT_PORT_START=8001
ENABLE_PAYMENT_VERIFICATION=false
```

**Generate a secure seed:**

```bash
# On macOS/Linux
openssl rand -hex 32
# or
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Start Services

**Terminal 1 - Backend:**
```bash
cd /Users/jedrzejcader/echopear/Aperta/backend
python main.py
```

**Terminal 2 - Fetch.ai Agents:**
```bash
cd /Users/jedrzejcader/echopear/Aperta/fetchai_agents
source venv/bin/activate
python main.py
```

### 4. Verify Running

```bash
# Test script
python test_agents.py

# Manual curl tests
curl http://localhost:8000/health  # Backend
curl http://localhost:8001/        # Context agent
curl http://localhost:8002/        # Privacy agent
```

## Production Deployment

### Option 1: Agentverse Hosted (Recommended)

**Pros:** No server management, automatic scaling, built-in monitoring
**Cons:** Less control, potential cold starts

1. **Package your agents:**

```bash
cd fetchai_agents
zip -r fetchai_agents.zip . -x "venv/*" -x "*.pyc" -x "__pycache__/*" -x ".env"
```

2. **Upload to Agentverse:**
   - Go to [agentverse.ai/deploy](https://agentverse.ai/deploy)
   - Upload `fetchai_agents.zip`
   - Configure environment variables in UI
   - Select Python 3.11 runtime
   - Set entry point: `main.py`

3. **Configure each agent:**
   - Set pricing (FET per request)
   - Add description and tags
   - Configure compute tier (basic/standard/premium)
   - Enable/disable public discovery

4. **Publish to marketplace:**
   - Review agent profiles
   - Submit for approval (if required)
   - Monitor usage via dashboard

### Option 2: Self-Hosted

**Pros:** Full control, no platform fees, private deployment
**Cons:** Server management, security updates, monitoring setup

#### Server Requirements

- Ubuntu 20.04+ or similar
- 2+ CPU cores
- 4GB+ RAM
- Python 3.11+
- Open ports: 8000-8008

#### Deployment Steps

1. **Clone and setup on server:**

```bash
# SSH to your server
ssh user@your-server.com

# Clone repo (or scp files)
cd /opt
git clone https://github.com/yourusername/aperta.git
cd aperta/fetchai_agents

# Run setup
./setup.sh

# Configure .env
nano .env
```

2. **Create systemd services:**

**Backend service:** `/etc/systemd/system/aperta-backend.service`

```ini
[Unit]
Description=Aperta FastAPI Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/aperta/backend
Environment="PATH=/opt/aperta/backend/venv/bin"
ExecStart=/opt/aperta/backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Fetch.ai agents service:** `/etc/systemd/system/aperta-fetchai.service`

```ini
[Unit]
Description=Aperta Fetch.ai Agents
After=network.target aperta-backend.service
Requires=aperta-backend.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/aperta/fetchai_agents
Environment="PATH=/opt/aperta/fetchai_agents/venv/bin"
ExecStart=/opt/aperta/fetchai_agents/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Enable and start services:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable aperta-backend aperta-fetchai
sudo systemctl start aperta-backend aperta-fetchai

# Check status
sudo systemctl status aperta-backend
sudo systemctl status aperta-fetchai

# View logs
sudo journalctl -u aperta-fetchai -f
```

4. **Configure firewall:**

```bash
# Allow agent ports
sudo ufw allow 8000:8008/tcp

# If using nginx reverse proxy
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

5. **Setup nginx reverse proxy (optional):**

```nginx
# /etc/nginx/sites-available/aperta-agents

upstream fetchai_agents {
    server localhost:8000;  # Backend
    server localhost:8001;  # Context agent
    server localhost:8002;  # Privacy agent
    # ... etc
}

server {
    listen 80;
    server_name agents.yourdomain.com;

    location / {
        proxy_pass http://fetchai_agents;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Register agents on Agentverse:**

```bash
source venv/bin/activate

# Get agent addresses from logs
# Then register each one

uagents register context_understanding \
  --address agent1q... \
  --endpoint https://agents.yourdomain.com:8001/submit \
  --price 0.10 \
  --description "Extract entities and insights from conversations"

uagents register privacy_guardian \
  --address agent1q... \
  --endpoint https://agents.yourdomain.com:8002/submit \
  --price 0.05 \
  --description "Redact PII from transcripts"

# ... repeat for all 8 agents
```

## Monitoring

### Logs

**Fetch.ai agents:**
```bash
# If using systemd
sudo journalctl -u aperta-fetchai -f

# If running manually
# Logs go to stdout
```

**Backend:**
```bash
sudo journalctl -u aperta-backend -f
```

### Metrics to track

1. **Request volume:** Requests per agent per hour
2. **Response times:** Average execution time per agent
3. **Error rates:** Failed requests / total requests
4. **Revenue:** FET tokens earned per agent
5. **Backend health:** API response times, CPU/memory usage

### Monitoring tools

- **Agentverse Dashboard:** Built-in for hosted deployments
- **Prometheus + Grafana:** For self-hosted monitoring
- **Uptimerobot:** Uptime monitoring
- **Sentry:** Error tracking

## Cost Analysis

### Running Costs (Self-Hosted)

**Server (DigitalOcean/AWS):**
- Small: $20-40/month (4GB RAM, 2 CPU)
- Medium: $80-120/month (8GB RAM, 4 CPU)
- Large: $200+/month (16GB+ RAM, 8+ CPU)

**Claude API Costs:**
- $15 per 1M input tokens
- $75 per 1M output tokens
- Estimate: $0.50-2.00 per agent request

**Total monthly cost (estimate):**
- Server: $40
- API: $500-2000 (depending on volume)
- **Total: $540-2040/month**

### Revenue (Example)

If each agent processes 1000 requests/month:
- Context (0.10 FET × 1000) = 100 FET
- Privacy (0.05 FET × 1000) = 50 FET
- Follow-up (0.08 FET × 1000) = 80 FET
- Cross-poll (0.15 FET × 1000) = 150 FET
- Q&A Router (0.03 FET × 1000) = 30 FET
- Retrieval (0.05 FET × 1000) = 50 FET
- Insight (0.12 FET × 1000) = 120 FET
- Composer (0.05 FET × 1000) = 50 FET

**Total: 630 FET/month**

At $0.50/FET = **$315/month revenue**

**Break-even:** ~3000 requests/month total across all agents

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:

```nginx
upstream context_agents {
    server 10.0.1.10:8001;
    server 10.0.1.11:8001;
    server 10.0.1.12:8001;
}
```

### Vertical Scaling

Increase server resources:
- More CPU cores for parallel requests
- More RAM for larger context windows
- SSD storage for faster ChromaDB queries

### Auto-scaling (AWS/GCP)

Use container orchestration:
- Kubernetes deployment
- Auto-scale based on request rate
- Load balancer with health checks

## Security

### Production Checklist

- [ ] Enable HTTPS/TLS
- [ ] Set `ENABLE_PAYMENT_VERIFICATION=true`
- [ ] Rotate `AGENT_SEED` periodically
- [ ] Secure `.env` file (chmod 600)
- [ ] Use firewall rules
- [ ] Set up rate limiting
- [ ] Enable API authentication
- [ ] Monitor for suspicious activity
- [ ] Regular security updates
- [ ] Backup configuration

### API Authentication

Add authentication to backend:

```python
# In backend/api/routes/conversations.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.post("/analyze")
async def analyze(
    token: str = Depends(security),
    # ... other params
):
    # Verify token is from Fetch.ai agents
    if token != settings.fetchai_agent_token:
        raise HTTPException(401)
    # ... continue
```

## Troubleshooting

### Common Issues

**1. Agents can't connect to backend**
- Check `BACKEND_API_URL` in `.env`
- Verify backend is running: `curl http://localhost:8000/health`
- Check firewall rules

**2. Payment verification failing**
- Set `ENABLE_PAYMENT_VERIFICATION=false` for testing
- Ensure Fetch.ai wallet has FET tokens
- Check agent addresses are registered

**3. High latency**
- Backend may be slow - check Claude API quotas
- Add caching layer (Redis)
- Scale horizontally

**4. Port conflicts**
- Change `AGENT_PORT_START` in `.env`
- Check which ports are in use: `lsof -i :8000-8008`

**5. Import errors**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

## Support

- **Fetch.ai Discord:** https://discord.gg/fetchai
- **uAgents Docs:** https://docs.fetch.ai/uagents
- **Agentverse Support:** support@fetch.ai

---

**Last updated:** 2026-02-15
