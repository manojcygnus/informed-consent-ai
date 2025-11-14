#!/bin/bash

# Free Consent Management System - Setup Script
# This script automates the installation process

set -e  # Exit on error

echo "=========================================="
echo "Free Consent Management System - Setup"
echo "=========================================="
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
echo "✓ Python found: $(python3 --version)"

# Check Ollama
echo ""
echo "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found"
    echo "Please install from: https://ollama.ai/download"
    echo "Then run: ollama pull llama3.1"
    exit 1
fi
echo "✓ Ollama found"

# Check if model is available
echo ""
echo "Checking Ollama model..."
if ! ollama list | grep -q "llama3.1"; then
    echo "⚠️  llama3.1 model not found"
    echo "Downloading llama3.1 model (this may take a few minutes)..."
    ollama pull llama3.1
fi
echo "✓ llama3.1 model available"

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Create directories
echo ""
echo "Creating directories..."
mkdir -p data uploads
echo "✓ Directories created"

# Setup environment file
echo ""
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created (you can edit it to customize)"
else
    echo "✓ .env file already exists"
fi

# Initialize database
echo ""
echo "Initializing database..."
cd api
python database.py
cd ..
echo "✓ Database initialized"

# Check Tesseract (optional)
echo ""
echo "Checking Tesseract (optional - for scanned PDFs)..."
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract found: $(tesseract --version | head -n1)"
else
    echo "⚠️  Tesseract not found (optional)"
    echo "   For scanned PDFs, install with:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   brew install tesseract poppler"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   sudo apt-get install tesseract-ocr poppler-utils"
    fi
fi

# Success message
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start API server:"
echo "   cd api && python app.py"
echo ""
echo "2. Open frontend:"
echo "   open frontend/index.html"
echo ""
echo "3. Process a PDF:"
echo "   cd scripts && python ingest_pdf.py path/to/consent.pdf"
echo ""
echo "For detailed instructions, see README.md or QUICKSTART.md"
echo "=========================================="
