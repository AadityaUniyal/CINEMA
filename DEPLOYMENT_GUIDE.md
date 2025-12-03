# Deployment Guide - Make Your Project Accessible from Anywhere

## Overview

To make your movie recommendation system accessible from anywhere, you need to:
1. Fix MongoDB Atlas connection (cloud database - already accessible)
2. Deploy your backend (Flask API)
3. Deploy your frontend (React app)

## Option 1: Free Deployment (Recommended for Testing)

### Backend Deployment Options:

#### A. Render (Free Tier)
- **Pros**: Free, easy setup, supports Python
- **Cons**: Sleeps after 15 min of inactivity
- **Steps**:
  1. Create account at https://render.com
  2. Connect your GitHub repository
  3. Create new "Web Service"
  4. Set build command: `pip install -r requirements.txt`
  5. Set start command: `gunicorn app:app`
  6. Add environment variables (MongoDB credentials)

#### B. Railway (Free Tier)
- **Pros**: Easy deployment, good free tier
- **Cons**: Limited free hours
- **Steps**:
  1. Sign up at https://railway.app
  2. Create new project from GitHub
  3. Add MongoDB Atlas connection string
  4. Deploy automatically

#### C. PythonAnywhere (Free Tier)
- **Pros**: Python-focused, simple
- **Cons**: Limited features on free tier
- **URL**: https://www.pythonanywhere.com

### Frontend Deployment Options:

#### A. Vercel (Free - Recommended)
- **Pros**: Optimized for React, unlimited bandwidth
- **Steps**:
  1. Sign up at https://vercel.com
  2. Import your GitHub repository
  3. Set root directory to `frontend`
  4. Add environment variable: `REACT_APP_API_URL=<your-backend-url>`
  5. Deploy automatically

#### B. Netlify (Free)
- **Pros**: Easy setup, good for static sites
- **Steps**:
  1. Sign up at https://netlify.com
  2. Connect GitHub repository
  3. Build command: `npm run build`
  4. Publish directory: `build`

#### C. GitHub Pages (Free)
- **Pros**: Free hosting with GitHub
- **Cons**: Static only, requires configuration

## Option 2: Full Cloud Deployment (Production)

### A. AWS (Amazon Web Services)
- **Backend**: EC2 or Elastic Beanstalk
- **Frontend**: S3 + CloudFront
- **Database**: MongoDB Atlas (already cloud)
- **Cost**: ~$10-50/month

### B. Google Cloud Platform
- **Backend**: Cloud Run or App Engine
- **Frontend**: Cloud Storage + CDN
- **Cost**: ~$10-30/month

### C. Microsoft Azure
- **Backend**: App Service
- **Frontend**: Static Web Apps
- **Cost**: ~$10-40/month

### D. DigitalOcean
- **Backend + Frontend**: Droplet ($5/month)
- **Database**: MongoDB Atlas
- **Cost**: $5-10/month

## Quick Start: Free Deployment (Vercel + Render)

This is the easiest way to get your project online for free:

### Step 1: Prepare Your Code

1. **Add to backend/requirements.txt**:
```
gunicorn==21.2.0
```

2. **Create backend/Procfile** (for Render):
```
web: gunicorn app:app
```

3. **Update frontend API URLs** to use environment variable:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
```

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 3: Deploy Backend (Render)

1. Go to https://render.com and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: movie-recommender-api
   - **Root Directory**: backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add Environment Variables:
   - `MONGO_URI`: Your MongoDB Atlas connection string
   - `JWT_SECRET_KEY`: Your secret key
6. Click "Create Web Service"
7. Copy your service URL (e.g., https://movie-recommender-api.onrender.com)

### Step 4: Deploy Frontend (Vercel)

1. Go to https://vercel.com and sign up
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: build
5. Add Environment Variable:
   - `REACT_APP_API_URL`: Your Render backend URL
6. Click "Deploy"
7. Your site will be live at: https://your-project.vercel.app

### Step 5: Update CORS in Backend

Update `backend/app.py` to allow your Vercel domain:

```python
from flask_cors import CORS

# Update CORS configuration
CORS(app, origins=[
    'http://localhost:3000',
    'https://your-project.vercel.app'  # Add your Vercel URL
])
```

## MongoDB Atlas Setup (For Any Location Access)

Your MongoDB Atlas is already cloud-based, but you need to:

1. **Whitelist All IPs** (for testing):
   - Go to MongoDB Atlas → Network Access
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"

2. **For Production**: Add specific IPs of your hosting providers

## Testing Your Deployment

Once deployed:
1. Visit your Vercel URL
2. Test all features (search, recommendations, login)
3. Share the URL with anyone - they can access it!

## Cost Summary

**Free Option** (Good for testing/portfolio):
- MongoDB Atlas: Free (512MB)
- Render Backend: Free (sleeps after 15 min)
- Vercel Frontend: Free (unlimited)
- **Total: $0/month**

**Production Option** (Reliable, always on):
- MongoDB Atlas: Free or $9/month
- Render Backend: $7/month
- Vercel Frontend: Free
- **Total: $7-16/month**

## Next Steps

Would you like me to:
1. Help you deploy to free hosting (Vercel + Render)?
2. Set up for paid hosting (more reliable)?
3. First fix the MongoDB connection, then deploy?

Let me know which path you'd like to take!
