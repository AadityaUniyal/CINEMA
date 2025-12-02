# CINÉMA Deployment Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account

## Quick Setup

### 1. Database Setup

1. Create MongoDB Atlas account at https://cloud.mongodb.com
2. Create a free cluster
3. Create database user and get connection string
4. Update `backend/config.py`:

```python
MONGO_URI = 'mongodb+srv://username:password@cluster.mongodb.net/'
```

5. Initialize data:

```bash
cd backend
python init_db.py
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs on http://localhost:5000

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on http://localhost:3000

## Docker Deployment

```bash
docker-compose up -d
```

## Production Notes

- Change `JWT_SECRET_KEY` in `config.py`
- Use environment variables for sensitive data
- Enable HTTPS
- Set up proper CORS origins

## ML Models

- Models stored in `backend/models/` (auto-created)
- Train first model: `POST /api/ml/train`
- Models are gitignored

## Troubleshooting

**MongoDB Connection Error:**
- Check connection string in `config.py`
- Verify IP whitelist in MongoDB Atlas

**Port Already in Use:**
- Backend: Change port in `app.py`
- Frontend: React will prompt for different port

**Module Not Found:**
```bash
pip install -r requirements.txt  # Backend
npm install                       # Frontend
```

---

For more details, see README.md
