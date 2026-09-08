#!/bin/bash

# Face Recognition API - Setup Script

echo "=========================================="
echo "Face Recognition API Setup"
echo "=========================================="

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Virtual environment created"
echo ""
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p known_faces
mkdir -p uploaded_images

echo "✓ Directories created"

# Copy .env file
if [ ! -f .env ]; then
    echo ""
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
    echo "✓ .env created (update with your settings)"
fi

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "📖 Next steps:"
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Add known faces to: known_faces/ directory"
echo "   Structure:"
echo "   known_faces/"
echo "   ├── person1/"
echo "   │   ├── image1.jpg"
echo "   │   └── image2.jpg"
echo "   └── person2/"
echo "       └── image1.jpg"
echo ""
echo "3. Run the API:"
echo "   python main.py"
echo ""
echo "4. Visit: http://localhost:8000/docs"
echo "=========================================="
