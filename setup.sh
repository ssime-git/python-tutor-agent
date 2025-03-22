#!/bin/bash
set -e

echo "Setting up Simplified LLMOps Demo"
echo "================================"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Create directories if they don't exist
if [ ! -d data ]; then
    mkdir -p data/chroma code-executor/tmp
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Please create a .env file with your API keys:"
    echo "GOOGLE_API_KEY=your_google_api_key"
    echo "LANGCHAIN_API_KEY=your_langsmith_api_key"
    echo "LANGCHAIN_PROJECT=llmops-demo"
    echo "LANGCHAIN_ENDPOINT=https://api.smith.langchain.com"
    exit 1
fi

# Build and start containers
echo "Starting services..."
docker-compose up -d

echo ""
echo "Setup complete!"
echo "Access the app at: http://localhost:8000"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"