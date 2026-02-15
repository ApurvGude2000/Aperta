#!/bin/bash

set -e  # Exit on error

echo "🚀 Deploying Aperta with Elasticsearch..."
echo "================================================"

# Check if .env.prod exists, if not create it
if [ ! -f .env.prod ]; then
    echo "📝 Creating .env.prod file..."

    # Generate secure password
    ELASTIC_PASSWORD=$(openssl rand -base64 32)

    cat > .env.prod <<EOF
# Auto-generated deployment configuration
# Generated: $(date)

# Elasticsearch
ELASTIC_PASSWORD=${ELASTIC_PASSWORD}

# JINA AI (add your key)
JINA_API_KEY=your_jina_api_key_here

# Anthropic (add your key)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Perplexity (add your key)
PERPLEXITY_API_KEY=your_perplexity_api_key_here
EOF

    echo "✓ Created .env.prod"
    echo "⚠️  IMPORTANT: Edit .env.prod and add your API keys!"
    echo ""
    read -p "Press Enter after you've added your API keys to .env.prod..."
fi

# Load environment variables
export $(cat .env.prod | grep -v '^#' | xargs)

# Check required variables
if [ "$JINA_API_KEY" = "your_jina_api_key_here" ]; then
    echo "❌ Please set JINA_API_KEY in .env.prod"
    exit 1
fi

if [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo "❌ Please set ANTHROPIC_API_KEY in .env.prod"
    exit 1
fi

echo "✓ Environment variables loaded"
echo ""

# Pull latest images
echo "📦 Pulling Docker images..."
docker-compose -f docker-compose.prod.yml pull
echo "✓ Images pulled"
echo ""

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down
echo "✓ Containers stopped"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d
echo "✓ Services started"
echo ""

# Wait for Elasticsearch to be ready
echo "⏳ Waiting for Elasticsearch to start..."
max_attempts=30
attempt=0

until curl -s -u "elastic:${ELASTIC_PASSWORD}" http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Elasticsearch failed to start after 30 attempts"
        echo "Check logs with: docker logs aperta-elasticsearch"
        exit 1
    fi
    echo "  Attempt $attempt/$max_attempts..."
    sleep 5
done

echo "✓ Elasticsearch ready"
echo ""

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 10

max_attempts=30
attempt=0

until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "⚠️  Backend may not have started. Check logs with: docker logs aperta-backend"
        break
    fi
    echo "  Attempt $attempt/$max_attempts..."
    sleep 5
done

echo "✓ Backend ready"
echo ""

# Initialize search index
echo "🔧 Initializing search index..."
if curl -s -X POST http://localhost:8000/api/search/initialize > /dev/null 2>&1; then
    echo "✓ Search index initialized"
else
    echo "⚠️  Could not initialize search index automatically"
    echo "   You can do it manually later with:"
    echo "   curl -X POST http://localhost:8000/api/search/initialize"
fi

echo ""
echo "================================================"
echo "✅ Deployment complete!"
echo "================================================"
echo ""
echo "📊 Elasticsearch:"
echo "   URL: http://localhost:9200"
echo "   Username: elastic"
echo "   Password: (saved in .env.prod)"
echo ""
echo "🌐 Backend API:"
echo "   URL: http://localhost:8000"
echo "   Health: http://localhost:8000/health"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Search Health:"
echo "   http://localhost:8000/api/search/health"
echo ""
echo "📝 Logs:"
echo "   All: docker-compose -f docker-compose.prod.yml logs -f"
echo "   ES: docker logs -f aperta-elasticsearch"
echo "   Backend: docker logs -f aperta-backend"
echo ""
echo "🛑 Stop:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
