# Elasticsearch Deployment Guide for Production

Complete guide for deploying Elasticsearch in production environments.

---

## 🎯 **Deployment Options**

### **Option 1: Elastic Cloud (Recommended - Easiest)**

**Best for**: Quick setup, managed service, automatic scaling

#### Setup:
1. Go to https://cloud.elastic.co/
2. Sign up and create a deployment
3. Choose your cloud provider (AWS, GCP, Azure)
4. Select region closest to your app
5. Copy the connection details

#### Cost:
- **Free tier**: 14-day trial
- **Paid**: Starting at ~$95/month for production

#### Configuration:
```bash
# In your .env
ELASTICSEARCH_HOST=https://your-deployment.es.us-east-1.aws.found.io:9243
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=your_secure_password_from_elastic_cloud
```

#### Pros:
- ✅ Fully managed (no ops needed)
- ✅ Automatic backups
- ✅ Security included
- ✅ Auto-scaling
- ✅ Monitoring dashboard

#### Cons:
- ❌ Costs money
- ❌ Less control

---

### **Option 2: Docker + Cloud Run / App Engine**

**Best for**: Cost-effective, full control, containerized deployment

#### 1. Create Dockerfile for Elasticsearch

`elasticsearch.Dockerfile`:
```dockerfile
FROM docker.elastic.co/elasticsearch/elasticsearch:8.12.0

# Set environment variables
ENV discovery.type=single-node
ENV xpack.security.enabled=true
ENV ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"

# Expose port
EXPOSE 9200
```

#### 2. Deploy to Google Cloud Run

```bash
# Build and push to GCP
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/elasticsearch

# Deploy to Cloud Run
gcloud run deploy elasticsearch \
  --image gcr.io/YOUR_PROJECT_ID/elasticsearch \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --port 9200 \
  --set-env-vars ELASTIC_PASSWORD=your_secure_password \
  --allow-unauthenticated
```

#### 3. Update your app config

```bash
# In your .env
ELASTICSEARCH_HOST=https://elasticsearch-xxxx.run.app
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=your_secure_password
```

#### Pros:
- ✅ Cost-effective (~$20-50/month)
- ✅ Auto-scales
- ✅ Easy deployment

#### Cons:
- ❌ Stateful storage needs persistent volumes
- ❌ Cold starts possible

---

### **Option 3: Google Cloud Elasticsearch (via Marketplace)**

**Best for**: GCP native integration, enterprise features

#### Setup:
1. Go to GCP Console → Marketplace
2. Search "Elasticsearch"
3. Deploy Elastic Cloud on GCP
4. Configure VM size and region

#### Configuration:
```bash
# In your .env
ELASTICSEARCH_HOST=http://your-vm-ip:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=your_password
```

---

### **Option 4: Docker Compose (Small Production)**

**Best for**: Small deployments, budget-friendly, VPS hosting

#### docker-compose.yml:
```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - xpack.security.enabled=true
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - elastic
    restart: unless-stopped

  kibana:  # Optional: For monitoring
    image: docker.elastic.co/kibana/kibana:8.12.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=elastic
      - ELASTICSEARCH_PASSWORD=${ELASTIC_PASSWORD}
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - elastic
    restart: unless-stopped

volumes:
  es_data:
    driver: local

networks:
  elastic:
    driver: bridge
```

#### Deploy to any VPS (DigitalOcean, Linode, AWS EC2):

```bash
# On your server
git clone your-repo
cd your-repo

# Set password
echo "ELASTIC_PASSWORD=your_secure_password" > .env

# Start
docker-compose up -d

# Check health
curl http://localhost:9200/_cluster/health
```

#### Pros:
- ✅ Very cost-effective ($10-20/month)
- ✅ Full control
- ✅ Easy to manage

#### Cons:
- ❌ Manual scaling
- ❌ You manage backups
- ❌ Need to secure yourself

---

### **Option 5: Kubernetes (Enterprise)**

**Best for**: Large scale, microservices, enterprise

#### Using Elastic Cloud on Kubernetes (ECK):

```yaml
# elasticsearch.yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: aperta-es
spec:
  version: 8.12.0
  nodeSets:
  - name: default
    count: 3
    config:
      node.store.allow_mmap: false
```

Deploy:
```bash
kubectl apply -f https://download.elastic.co/downloads/eck/2.10.0/crds.yaml
kubectl apply -f https://download.elastic.co/downloads/eck/2.10.0/operator.yaml
kubectl apply -f elasticsearch.yaml
```

---

## 📊 **Recommendation by Deployment Type**

### **For Your Aperta App:**

| Deployment Type | Recommended Option | Estimated Cost |
|----------------|-------------------|----------------|
| **MVP / Testing** | Docker Compose on VPS | $10-20/month |
| **Production (Small)** | Elastic Cloud Starter | $95/month |
| **Production (Medium)** | Elastic Cloud Standard | $200/month |
| **Production (Large)** | Kubernetes + ECK | $500+/month |
| **Development** | Local (Homebrew/Docker) | Free |

### **My Recommendation for Aperta:**

Start with **Docker Compose on VPS** or **Elastic Cloud**:

**Docker Compose** if:
- ✅ Budget-conscious
- ✅ Small to medium scale (<100k conversations)
- ✅ You're comfortable with basic DevOps

**Elastic Cloud** if:
- ✅ Want zero ops burden
- ✅ Need enterprise features
- ✅ Budget allows $100-200/month
- ✅ Want automatic scaling

---

## 🔧 **Deployment Script for Docker Compose**

I'll create a deployment-ready configuration:

### `deploy/docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: aperta-elasticsearch
    environment:
      - discovery.type=single-node
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
      - xpack.security.enabled=true
      - xpack.security.enrollment.enabled=false
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - aperta-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: aperta-backend
    environment:
      - ELASTICSEARCH_HOST=http://elasticsearch:9200
      - ELASTICSEARCH_USER=elastic
      - ELASTICSEARCH_PASSWORD=${ELASTIC_PASSWORD}
      - JINA_API_KEY=${JINA_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
    depends_on:
      elasticsearch:
        condition: service_healthy
    ports:
      - "8000:8000"
    networks:
      - aperta-network
    restart: unless-stopped

volumes:
  elasticsearch_data:
    driver: local

networks:
  aperta-network:
    driver: bridge
```

### Deploy script: `deploy/deploy.sh`
```bash
#!/bin/bash

echo "🚀 Deploying Aperta with Elasticsearch..."

# Set environment variables
export ELASTIC_PASSWORD=$(openssl rand -base64 32)
export JINA_API_KEY="your_jina_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export PERPLEXITY_API_KEY="your_perplexity_key"

# Save passwords
echo "ELASTIC_PASSWORD=$ELASTIC_PASSWORD" >> .env.prod
echo "✓ Generated secure Elasticsearch password"

# Pull images
docker-compose -f docker-compose.prod.yml pull

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Wait for Elasticsearch to be ready
echo "⏳ Waiting for Elasticsearch to start..."
until curl -s http://localhost:9200/_cluster/health > /dev/null; do
    sleep 5
done

echo "✓ Elasticsearch ready"

# Initialize search index
echo "🔧 Initializing search index..."
sleep 10  # Wait for backend to start
curl -X POST http://localhost:8000/api/search/initialize

echo "✅ Deployment complete!"
echo "📊 Elasticsearch: http://localhost:9200"
echo "🌐 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
```

---

## 🔐 **Security Checklist for Production**

- [ ] Use strong password for Elasticsearch
- [ ] Enable HTTPS (use nginx/traefik reverse proxy)
- [ ] Restrict network access (firewall rules)
- [ ] Regular backups (use snapshots)
- [ ] Monitor resource usage
- [ ] Set up log rotation
- [ ] Use secrets management (not .env in production)

---

## 📈 **Scaling Guidelines**

### **When to scale:**
- Search latency > 500ms
- CPU usage > 70%
- Memory usage > 80%
- Index size > 50GB

### **How to scale:**

**Vertical scaling** (easier):
- Increase RAM (ES is RAM-hungry)
- More CPU cores
- Faster SSD

**Horizontal scaling** (better):
- Add more ES nodes
- Configure shards and replicas
- Use load balancer

---

## 🎯 **Quick Start for VPS Deployment**

```bash
# On DigitalOcean/Linode/AWS EC2
# (2GB RAM minimum, 4GB recommended)

# 1. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 2. Clone your repo
git clone https://github.com/your-repo/aperta.git
cd aperta/deploy

# 3. Set environment variables
cp .env.example .env
nano .env  # Add your API keys

# 4. Deploy
chmod +x deploy.sh
./deploy.sh

# 5. Verify
curl http://localhost:8000/api/search/health
```

---

## 💰 **Cost Comparison**

| Option | Monthly Cost | Setup Time | Maintenance |
|--------|-------------|------------|-------------|
| Elastic Cloud | $95-$200 | 5 minutes | None |
| Docker Compose VPS | $10-$20 | 30 minutes | Low |
| GCP Marketplace | $50-$150 | 15 minutes | Medium |
| Kubernetes | $200+ | 2-4 hours | High |
| Local (dev only) | Free | 5 minutes | None |

---

## 📞 **Support Resources**

- **Elastic Cloud Support**: https://cloud.elastic.co/support
- **Docker Docs**: https://docs.docker.com/
- **Elastic Documentation**: https://www.elastic.co/guide/
- **Our Setup Guide**: `SEARCH_SETUP_GUIDE.md`

---

**Next Steps:**
1. Choose your deployment option
2. Follow the specific setup instructions
3. Update your `.env` with production credentials
4. Test with `curl http://your-server/api/search/health`
5. Start indexing conversations!
