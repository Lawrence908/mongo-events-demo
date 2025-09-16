#!/bin/bash
# MongoDB Events Demo - Quick Start Script
#
# This script helps you get started with the application

set -e  # Exit on any error

echo "🚀 MongoDB Events Demo - Quick Start"
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python found"

# Check if MongoDB is running (optional)
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    echo "✅ MongoDB client found"
    
    if mongosh --eval "db.adminCommand('ping')" --quiet 2>/dev/null || mongo --eval "db.adminCommand('ping')" --quiet 2>/dev/null; then
        echo "✅ MongoDB server is running"
    else
        echo "⚠️  MongoDB server is not running - you'll need to start it to use the full features"
    fi
else
    echo "⚠️  MongoDB client not found - install MongoDB to use database features"
fi

echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "📝 Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "📝 Edit .env file to configure MongoDB connection"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🧪 Testing basic application structure..."
python -c "
import os
os.environ['MONGODB_URI'] = 'mongodb://fake:27017/'
from app import create_app
app = create_app()
app.config['TESTING'] = True
with app.test_client() as client:
    response = client.get('/')
    assert response.status_code == 200
    print('✅ Flask application loads correctly')
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start MongoDB server (if not already running)"
echo "2. Edit .env file with your MongoDB connection details"
echo "3. Generate sample data: python data/generate_sample_data.py"
echo "4. Start the application: python run.py"
echo "5. Open http://localhost:5010 in your browser"
echo ""
echo "For more details, see README.md"