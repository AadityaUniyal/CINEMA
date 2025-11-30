# 🚀 Deployment Guide - CINÉMA

Deploy your movie recommendation app to the web for FREE!

## 📋 Prerequisites
- GitHub account (you already have this!)
- Vercel account (sign up with GitHub)
- Render account (sign up with GitHub)

---

## 🎯 Step 1: Deploy Backend to Render

### 1. Go to [Render.com](https://render.com) and sign up with GitHub

### 2. Create New Web Service
- Click "New +" → "Web Service"
- Connect your GitHub repository: `AadityaUniyal/project1`
- Configure:
  - **Name**: `cinema-backend`
  - **Root Directory**: `backend`
  - **Environment**: `Python 3`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 3. Add Environment Variables
Click "Environment" and add:
```
MONGO_URI = mongodb+srv://aadityauniyal22_db_user:3vQYBshs_!nv@j9@cluster1.4irifqj.mongodb.net/?appName=Cluster1
JWT_SECRET_KEY = your-secret-key-here
PYTHON_VERSION = 3.11.0
```

### 4. Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Copy your backend URL (e.g., `https://cinema-backend.onrender.com`)

---

## 🎨 Step 2: Deploy Frontend to Vercel

### 1. Go to [Vercel.com](https://vercel.com) and sign up with GitHub

### 2. Import Project
- Click "Add New..." → "Project"
- Import `AadityaUniyal/project1`
- Configure:
  - **Framework Preset**: Create React App
  - **Root Directory**: `frontend`
  - **Build Command**: `npm run build`
  - **Output Directory**: `build`

### 3. Add Environment Variable
In "Environment Variables" section, add:
```
REACT_APP_API_URL = https://cinema-backend.onrender.com/api
```
(Replace with your actual Render backend URL from Step 1)

### 4. Deploy
- Click "Deploy"
- Wait 2-3 minutes
- Your site will be live at: `https://your-project.vercel.app`

---

## ✅ Step 3: Test Your Live Website

1. Visit your Vercel URL
2. Register a new account
3. Set your genre preferences
4. Browse movies and get recommendations!

---

## 🔧 Alternative: Deploy to Railway (All-in-One)

### Option: Railway (Backend + Frontend Together)

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables:
   ```
   MONGO_URI = your-mongodb-uri
   JWT_SECRET_KEY = your-secret-key
   ```
6. Railway will auto-detect and deploy both services

---

## 📝 Update API URLs After Deployment

After deploying backend, update this file:
`frontend/.env.production`
```
REACT_APP_API_URL=https://your-actual-backend-url.onrender.com/api
```

Then redeploy frontend on Vercel.

---

## 🎉 Your App is Live!

Share your live URL with friends:
- Frontend: `https://your-project.vercel.app`
- Backend API: `https://cinema-backend.onrender.com`

---

## 💡 Tips

- **Free Tier Limits**:
  - Render: Backend may sleep after 15 min of inactivity (first request takes ~30s to wake up)
  - Vercel: Unlimited bandwidth for personal projects
  
- **Custom Domain**: Both Vercel and Render support custom domains for free!

- **Automatic Deployments**: Every push to GitHub will auto-deploy to Vercel/Render

---

## 🐛 Troubleshooting

### Backend not responding?
- Check Render logs for errors
- Verify MongoDB connection string
- Ensure all environment variables are set

### Frontend can't connect to backend?
- Check CORS settings in `backend/app.py`
- Verify `REACT_APP_API_URL` is correct
- Check browser console for errors

### Need help?
- Render docs: https://render.com/docs
- Vercel docs: https://vercel.com/docs
