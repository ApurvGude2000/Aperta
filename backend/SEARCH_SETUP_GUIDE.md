## 🔍 Semantic Search Setup Guide

Complete guide for setting up Elasticsearch + JINA AI embeddings for semantic conversation search.

---

## 📋 Prerequisites

1. **Elasticsearch 8.x** installed and running
2. **JINA AI API key** for embeddings
3. **Python 3.12** with backend dependencies

---

## 🚀 Quick Start

### Step 1: Install Elasticsearch

#### macOS (Homebrew):
```bash
brew tap elastic/tap
brew install elastic/tap/elasticsearch-full

# Start Elasticsearch
brew services start elastic/tap/elasticsearch-full
```

#### Docker:
```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.12.0
```

#### Linux (apt):
```bash
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update && sudo apt-get install elasticsearch
sudo systemctl start elasticsearch
```

### Step 2: Get JINA AI API Key

1. Go to https://jina.ai/embeddings/
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `jina_...`)

### Step 3: Configure Environment

Update `backend/.env`:

```bash
# JINA AI Configuration
JINA_API_KEY=jina_your_actual_key_here

# Elasticsearch Configuration
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=  # Leave empty for local dev
```

### Step 4: Install Python Dependencies

```bash
cd backend
source venv/bin/activate
pip install elasticsearch[async]==8.12.0
```

### Step 5: Initialize Search Index

```bash
# Start the backend
python main.py

# In another terminal, initialize the index
curl -X POST http://localhost:8000/api/search/initialize
```

Or via Python:
```python
import httpx
import asyncio

async def init():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/search/initialize")
        print(response.json())

asyncio.run(init())
```

---

## 🧪 Testing

### Test 1: Health Check

```bash
curl http://localhost:8000/api/search/health
```

Expected output:
```json
{
  "elasticsearch": {
    "status": "connected",
    "cluster_name": "elasticsearch",
    "version": "8.12.0"
  },
  "embedding_service": {
    "status": "configured",
    "model": "jina-embeddings-v2-base-en",
    "dimensions": 768
  },
  "overall_status": "healthy"
}
```

### Test 2: Index a Conversation

```bash
curl -X POST http://localhost:8000/api/search/index \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_conv_1",
    "user_id": "user_123",
    "transcript": "I met Alice Chen who is a Partner at Acme Ventures. We discussed AI safety in healthcare and she is interested in funding early-stage healthcare AI startups. She asked me to send over our pitch deck.",
    "metadata": {
      "title": "Meeting with Alice Chen",
      "people": ["Alice Chen"],
      "topics": ["AI safety", "Healthcare AI", "Funding"],
      "companies": ["Acme Ventures"],
      "event_name": "TechCrunch Disrupt",
      "sentiment": "positive",
      "created_at": "2026-02-14T10:00:00Z",
      "duration_minutes": 15
    }
  }'
```

### Test 3: Search Conversations

```bash
curl -X POST http://localhost:8000/api/search/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who did I meet that invests in healthcare AI?",
    "user_id": "user_123",
    "max_results": 5
  }'
```

Expected output:
```json
{
  "results": [
    {
      "conversation_id": "test_conv_1",
      "title": "Meeting with Alice Chen",
      "excerpt": "I met Alice Chen who is a Partner at Acme Ventures...",
      "relevance_score": 0.95,
      "people": ["Alice Chen"],
      "topics": ["AI safety", "Healthcare AI", "Funding"],
      "companies": ["Acme Ventures"],
      "event_name": "TechCrunch Disrupt",
      "sentiment": "positive"
    }
  ],
  "total_found": 1,
  "query": "Who did I meet that invests in healthcare AI?",
  "execution_time_ms": 234.56
}
```

---

## 📊 How It Works

### 1. **Indexing Pipeline**

```
Conversation → JINA Embedding (768D vector) → Elasticsearch
```

When a conversation is indexed:
1. Transcript is sent to JINA AI API
2. Returns a 768-dimensional embedding vector
3. Vector + metadata stored in Elasticsearch

### 2. **Search Pipeline**

```
Query → JINA Embedding → Vector Similarity Search → Ranked Results
```

When searching:
1. Query is embedded using same JINA model
2. Elasticsearch performs cosine similarity search
3. Results ranked by relevance score
4. Returns top-k most relevant conversations

### 3. **Vector Similarity**

- **Model**: jina-embeddings-v2-base-en (768 dimensions)
- **Similarity**: Cosine similarity
- **kNN Search**: k-nearest neighbors with filtering

---

## 🔧 Advanced Configuration

### Custom Elasticsearch Settings

For production, update `.env`:
```bash
ELASTICSEARCH_HOST=https://your-es-cluster.com:9200
ELASTICSEARCH_USER=your_username
ELASTICSEARCH_PASSWORD=your_secure_password
```

### Search with Filters

```bash
curl -X POST http://localhost:8000/api/search/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI safety discussions",
    "user_id": "user_123",
    "max_results": 10,
    "filters": {
      "topics": ["AI safety", "Healthcare"],
      "sentiment": "positive",
      "people": ["Alice Chen"]
    }
  }'
```

### Batch Indexing

Index multiple conversations:
```python
import httpx
import asyncio

conversations = [
    {
        "conversation_id": f"conv_{i}",
        "user_id": "user_123",
        "transcript": f"Conversation {i} transcript...",
        "metadata": {...}
    }
    for i in range(10)
]

async def batch_index():
    async with httpx.AsyncClient() as client:
        for conv in conversations:
            response = await client.post(
                "http://localhost:8000/api/search/index",
                json=conv
            )
            print(f"Indexed: {conv['conversation_id']}")

asyncio.run(batch_index())
```

---

## 🐛 Troubleshooting

### Elasticsearch not connecting

```bash
# Check if Elasticsearch is running
curl http://localhost:9200

# Check logs
tail -f /usr/local/var/log/elasticsearch/elasticsearch.log  # macOS
docker logs elasticsearch  # Docker
```

### JINA API errors

```bash
# Test JINA API key
curl -X POST https://api.jina.ai/v1/embeddings \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input":["test"],"model":"jina-embeddings-v2-base-en"}'
```

### Index not found

```bash
# Reinitialize the index
curl -X POST http://localhost:8000/api/search/initialize
```

### Slow searches

- Increase `num_candidates` in search
- Add more specific filters
- Use Elasticsearch query profiler

---

## 📈 Performance Tips

1. **Batch indexing**: Index conversations in batches for faster processing
2. **Filters**: Use filters (topics, people) to reduce search space
3. **Cache**: Cache embeddings for frequently searched queries
4. **Elasticsearch tuning**: Adjust heap size and shards for scale

---

## 🔐 Security Considerations

1. **JINA API Key**: Keep secure, don't commit to version control
2. **Elasticsearch**: Use authentication in production
3. **User isolation**: Always filter by `user_id` to prevent data leaks
4. **HTTPS**: Use HTTPS for Elasticsearch in production

---

## 📚 API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search/conversations` | POST | Search conversations |
| `/api/search/index` | POST | Index a conversation |
| `/api/search/initialize` | POST | Initialize search index |
| `/api/search/conversations/{id}` | DELETE | Delete from index |
| `/api/search/health` | GET | Health check |

### Full API Docs

Visit: http://localhost:8000/docs

---

## ✅ Verification Checklist

- [ ] Elasticsearch running on port 9200
- [ ] JINA API key configured in `.env`
- [ ] Search index initialized
- [ ] Health check returns "healthy"
- [ ] Can index test conversation
- [ ] Can search and get results
- [ ] Results have relevance scores

---

## 🎯 Next Steps

1. **Integrate with app**: Auto-index conversations when created
2. **Frontend**: Add search UI to webapp
3. **Advanced features**: Faceted search, autocomplete, highlighting
4. **Monitoring**: Add metrics and logging for search performance

---

**Need help?** Check the API docs at `/docs` or review `services/elasticsearch_service.py`
