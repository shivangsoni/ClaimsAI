#!/bin/bash

echo "========================================"
echo "Claims AI - Document Processing System"
echo "React Frontend + Python Backend + GPT-4"
echo "========================================"
echo

echo "IMPORTANT SETUP NOTES:"
echo "1. Make sure you have Node.js installed (https://nodejs.org)"
echo "2. Set your OpenAI API key in backend/utils/document_processor.py"
echo "3. Install Tesseract OCR for image text extraction (optional)"
echo

echo "Setting up Backend..."
cd backend
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo
echo "Initializing database..."
python -c "from utils.database import DatabaseManager; db = DatabaseManager(); print('Database initialized!')"

echo
echo "Creating uploads directory..."
mkdir -p uploads

echo
echo "Setting up React Frontend..."
cd ../react-frontend

echo "Installing Node.js dependencies..."
npm install


echo
echo "========================================"
echo "STARTING SYSTEM"
echo "========================================"
echo

echo "1. Starting Python Backend (Flask)..."
cd ../backend
python app.py &
BACKEND_PID=$!

echo
echo "2. Waiting for backend to start..."
sleep 5

echo
echo "3. Starting React Frontend..."
echo "Frontend will open in your browser at http://localhost:3000"
echo "Backend API is running at http://localhost:8000"
echo
cd ../react-frontend
npm start

# Clean up background process when script ends
trap "kill $BACKEND_PID" EXIT