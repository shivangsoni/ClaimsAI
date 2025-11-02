@echo off
echo ========================================
echo Claims AI - Quick Setup Script
echo ========================================
echo.

echo 1. Installing Python dependencies...
cd backend
pip install -r requirements.txt

echo.
echo 2. Initializing database...
python -c "from utils.database import DatabaseManager; db = DatabaseManager(); print('Database initialized successfully!')"

echo.
echo 3. Starting the Flask backend...
echo Backend will run on http://localhost:5000
echo.
echo To use the system:
echo 1. Keep this terminal open (backend will be running)
echo 2. Open frontend/index.html in your web browser
echo 3. The frontend will connect to this backend automatically
echo.
echo Press Ctrl+C to stop the backend when you're done.
echo.
echo Starting backend now...
python app.py