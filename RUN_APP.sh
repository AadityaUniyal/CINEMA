#!/bin/bash

echo "=========================================="
echo "Starting MovieLens Application"
echo "=========================================="
echo ""

# Check if MongoDB is running
echo "Checking MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "Starting MongoDB..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start mongodb-community
    else
        sudo systemctl start mongod
    fi
    sleep 3
fi
echo "✓ MongoDB is running"
echo ""

# Start Backend
echo "Starting Backend Server..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..
sleep 5

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "=========================================="
echo "✅ Application is running!"
echo "=========================================="
echo ""
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services..."

# Trap Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait
wait
