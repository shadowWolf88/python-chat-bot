#!/bin/bash
# Setup script for local development with virtual environment

echo "🔧 Setting up Healing Space development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install main dependencies
echo "📥 Installing main dependencies..."
pip install -r requirements.txt

# Ask about training dependencies
echo ""
read -p "Install AI training dependencies? (~2-3GB, optional) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Installing training dependencies..."
    pip install -r requirements-training.txt
    echo "✅ Training system ready!"
else
    echo "⏭️  Skipping training dependencies (can install later)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate environment in future sessions:"
echo "  source venv/bin/activate"
echo ""
echo "To run the app:"
echo "  python api.py"
echo ""
