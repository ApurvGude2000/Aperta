#!/bin/bash

# Quick script to download and run Elasticsearch locally

ES_VERSION="8.12.0"
ES_DIR="elasticsearch-${ES_VERSION}"
ES_TARBALL="${ES_DIR}-darwin-x86_64.tar.gz"

if [ ! -d "$ES_DIR" ]; then
    echo "📦 Downloading Elasticsearch ${ES_VERSION}..."
    curl -O https://artifacts.elastic.co/downloads/elasticsearch/${ES_TARBALL}
    
    echo "📂 Extracting..."
    tar -xzf ${ES_TARBALL}
    rm ${ES_TARBALL}
fi

echo "🚀 Starting Elasticsearch..."
cd ${ES_DIR}

# Configure for single-node, no security (dev only)
export ES_JAVA_OPTS="-Xms512m -Xmx512m"
./bin/elasticsearch -E discovery.type=single-node -E xpack.security.enabled=false &

echo "✓ Elasticsearch starting on http://localhost:9200"
echo "  Press Ctrl+C to stop"
