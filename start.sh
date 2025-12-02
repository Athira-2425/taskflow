#!/bin/bash

# Taskflow API Startup Script

echo "🚀 Starting Taskflow API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Start the API server
echo "🌟 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "📚 ReDoc Documentation: http://localhost:8000/redoc"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload