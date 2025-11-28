#!/bin/bash

echo "=========================================="
echo "MovieLens Setup Script"
echo "=========================================="
echo ""

# Check if MongoDB is running
echo "Checking MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB is not running. Please start MongoDB first."
    echo "   On Linux/Mac: sudo systemctl start mongod"
    echo "   On Mac with Homebrew: brew services start mongodb-community"
    exit 1
fi
echo "✓ MongoDB is running"
echo ""

# Backend setup
echo "Setting up backend..."
cd backend
python -m pip install -r requirements.txt
echo "✓ Backend dependencies installed"
echo ""

# Initialize database
echo "Initializing database with CSV data..."
python init_db.py
if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed"
    exit 1
fi
echo ""

# Frontend setup
echo "Setting up frontend..."
cd ../frontend
npm install
echo "✓ Frontend dependencies installed"
echo ""

echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  python app.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
echo ""
