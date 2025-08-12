#!/bin/bash

echo "🔧 Installing Document Processing Dependencies..."

# Update package list
sudo apt-get update

# Install system dependencies for OCR and document processing
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements-hybrid.txt

# Install spaCy English model
echo "🧠 Installing spaCy English model..."
python -m spacy download en_core_web_sm

# Install NLTK data
echo "📚 Installing NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

echo "✅ Document processing dependencies installed successfully!"
echo ""
echo "📋 Supported file types:"
echo "   - PDF (.pdf)"
echo "   - Word documents (.docx, .doc)"
echo "   - Text files (.txt)"
echo "   - Images (.png, .jpg, .jpeg, .tiff, .bmp)"
echo ""
echo "🤖 Features:"
echo "   - OCR for images and scanned PDFs"
echo "   - AI-powered document classification"
echo "   - Entity extraction (companies, dates, amounts)"
echo "   - Keyword extraction"
echo "   - Financial data analysis" 