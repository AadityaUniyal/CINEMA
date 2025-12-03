# 🎬 Movie Recommendation System

A full-stack movie recommendation system with machine learning-powered personalized recommendations, user authentication, and comprehensive analytics.

## ✨ Features

### Core Features
- 🎯 **Personalized Recommendations** - ML-powered movie suggestions
- 🔐 **User Authentication** - Secure login and registration
- ⭐ **Movie Ratings & Reviews** - Rate and review movies
- 📊 **Analytics Dashboard** - View trends and statistics
- 📝 **Watchlist Management** - Save movies to watch later
- 🎲 **Discover Movies** - Find random movies by genre
- � **Ssearch & Filter** - Search movies and filter by genre

### ML Features
- 🤖 **Matrix Factorization** - Collaborative filtering algorithm
- 🎯 **Personal Model Training** - Users can train custom models
- 📈 **Training Dashboard** - Monitor model performance
- ⚙️ **Hyperparameter Tuning** - Optimize model parameters
- 📊 **Model Metrics** - RMSE, Precision, Recall, Coverage
- 🔄 **Scheduled Training** - Automatic weekly retraining

### Advanced Features
- 🎨 **Preference-Based Training** - Customize recommendations by:
  - Favorite genres
  - Diversity vs popularity
  - Recency preferences
  - Quality thresholds
- 💾 **Real-time Learning** - Models update with new ratings
- 🔍 **Explainable AI** - Understand why movies are recommended
- 📱 **Responsive Design** - Works on all devices

## 🛠️ Tech Stack

### Frontend
- **React** 18 - UI framework
- **Axios** - HTTP client
- **React Router** - Navigation
- **CSS3** - Styling

### Backend
- **Flask** 3.0 - Web framework
- **Python** 3.12+ - Programming language
- **MongoDB Atlas** - Cloud database
- **PyMongo** - MongoDB driver
- **Pandas** - Data processing
- **NumPy** - Numerical computing

### Machine Learning
- **Scikit-learn** - ML algorithms
- **TensorFlow** - Deep learning
- **Surprise** - Recommendation algorithms
- **Matrix Factorization** - Collaborative filtering

### Deployment
- **Gunicorn** - Production server
- **Render** - Backend hosting (ready)
- **Vercel** - Frontend hosting (ready)
- **Docker** - Containerization (optional)

## 📋 Prerequisites

- **Python** 3.12 or higher
- **Node.js** 16+ and npm
- **MongoDB Atlas** account (free tier works)
- **Git** for version control

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd project1
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure MongoDB
# Update backend/config.py with your MongoDB Atlas credentials
# Or set environment variables:
# MONGO_URI=your_mongodb_connection_string

# Initialize database (optional - loads CSV data)
python init_db.py

# Start backend server
python app.py
```

Backend runs on: http://localhost:5000

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend runs on: http://localhost:3000

## 📁 Project Structure

```
project1/
├── backend/
│   ├── ml/                      # ML models and services
│   │   ├── matrix_factorization.py
│   │   ├── training_service.py
│   │   ├── evaluation_service.py
│   │   └── ml_model_manager.py
│   ├── models/                  # Trained models (gitignored)
│   ├── logs/                    # Application logs
│   ├── app.py                   # Main Flask application
│   ├── config.py                # Configuration
│   ├── data_processor.py        # Data processing
│   ├── ml_engine.py             # Recommendation engine
│   ├── user_auth.py             # Authentication
│   ├── watchlist.py             # Watchlist management
│   ├── reviews_manager.py       # Reviews system
│   ├── scheduler.py             # Training scheduler
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── MovieList.jsx
│   │   │   ├── Recommendations.jsx
│   │   │   ├── TrainingDashboard.jsx
│   │   │   ├── PersonalizedTraining.jsx
│   │   │   └── ...
│   │   ├── styles/              # CSS files
│   │   ├── config.js            # API configuration
│   │   └── App.js               # Main app component
│   ├── public/                  # Static files
│   └── package.json             # Node dependencies
├── movies.csv                   # Movie dataset
├── ratings.csv                  # Ratings dataset
├── README.md                    # This file
├── DEPLOYMENT.md                # Deployment guide
├── DEPLOY_NOW.md                # Quick deployment
├── ML_TRAINING_GUIDE.md         # ML training docs
├── PERSONALIZED_TRAINING_GUIDE.md
└── DEPLOYMENT_GUIDE.md          # Comprehensive deployment

```

## 🎯 Key Features Guide

### User Authentication
1. Register with name, email, password
2. Login to access personalized features
3. View profile and statistics

### Rating Movies
1. Browse or search for movies
2. Click on a movie card
3. Rate 1-5 stars and optionally add a review

### Getting Recommendations
1. Rate at least 5-10 movies
2. Go to "Recommendations" page
3. View personalized suggestions

### Training Personal Model
1. Navigate to "Train My Model"
2. Select favorite genres
3. Adjust priority sliders:
   - Diversity (varied vs predictable)
   - Popularity (mainstream vs hidden gems)
   - Recency (new vs classic)
4. Set minimum rating threshold
5. Click "Train My Personal Model"
6. Wait 10-30 seconds for training

### Watchlist
1. Click bookmark icon on any movie
2. View watchlist in Dashboard
3. Mark movies as watched
4. Remove from watchlist

## 🔧 Configuration

### Environment Variables

Create `.env` file in backend/:
```env
# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=movielens_db

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# ML Training Schedule
ML_TRAINING_SCHEDULE_ENABLED=true
ML_TRAINING_DAY=6  # Sunday
ML_TRAINING_HOUR=2  # 2 AM
```

### MongoDB Setup
1. Create free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Add database user
4. Whitelist IP (0.0.0.0/0 for development)
5. Get connection string
6. Update `backend/config.py` or set `MONGO_URI` env variable

## 📊 Data

### Included Datasets
- **movies.csv** - 5,000 movies with titles and genres
- **ratings.csv** - 5,000 ratings from users

### Database Collections
- `users` - User accounts
- `user_profiles` - User preferences and stats
- `movies` - Movie information
- `ratings` - User ratings
- `user_ratings` - Real-time ratings
- `reviews` - Movie reviews
- `watchlists` - User watchlists
- `training_preferences` - Personal model preferences

## 🚀 Deployment

### Quick Deployment (Free)

**Backend (Render):**
1. Sign up at [Render.com](https://render.com)
2. Connect GitHub repository
3. Create Web Service
4. Set environment variables
5. Deploy

**Frontend (Vercel):**
1. Sign up at [Vercel.com](https://vercel.com)
2. Import GitHub repository
3. Set `REACT_APP_API_URL` to backend URL
4. Deploy

See `DEPLOY_NOW.md` for detailed instructions.

## 📚 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile/{user_id}` - Get user profile

### Movies
- `GET /api/movies` - List movies (paginated)
- `GET /api/movies/random` - Get random movies
- `GET /api/search?q={query}` - Search movies
- `GET /api/genres` - List all genres

### Ratings & Reviews
- `POST /api/rate` - Rate a movie
- `POST /api/reviews` - Add review
- `GET /api/reviews/{movie_id}` - Get movie reviews

### Recommendations
- `GET /api/recommendations/{user_id}` - Get recommendations
- `GET /api/ml/recommendations/{user_id}` - ML recommendations
- `GET /api/ml/recommendations/personal/{user_id}` - Personal model

### ML Training
- `POST /api/ml/train` - Train global model
- `POST /api/ml/train-personal` - Train personal model
- `GET /api/ml/metrics` - Get model metrics
- `GET /api/ml/metrics/history` - Training history

### Watchlist
- `GET /api/watchlist/{user_id}` - Get watchlist
- `POST /api/watchlist/{user_id}/{movie_id}` - Add to watchlist
- `DELETE /api/watchlist/{user_id}/{movie_id}` - Remove from watchlist

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Check MongoDB connection
python check_mongo.py

# Test API endpoints
curl http://localhost:5000/api/health
```

## 🐛 Troubleshooting

### MongoDB Connection Issues
- Verify connection string in `config.py`
- Check IP whitelist in MongoDB Atlas
- Ensure Python 3.12+ is installed
- Try: `pip install --upgrade pymongo`

### Frontend Can't Connect to Backend
- Verify backend is running on port 5000
- Check `frontend/src/config.js` has correct API URL
- Clear browser cache
- Check CORS settings in `backend/app.py`

### ML Training Fails
- Ensure at least 100 ratings in database
- Check `backend/logs/ml/` for error logs
- Verify sufficient disk space for models
- Try: `python init_db.py` to load sample data

## � Performance

- **Response Time:** < 200ms for most endpoints
- **ML Training:** 10-30 seconds for 20K ratings
- **Recommendations:** Generated in < 100ms
- **Database:** Optimized with indexes

## 🔒 Security

- Passwords hashed with secure algorithms
- JWT tokens for authentication
- CORS protection
- Input validation
- SQL injection prevention (NoSQL)
- Environment variables for secrets

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## � Liicense

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- MovieLens dataset
- Flask and React communities
- MongoDB Atlas
- Scikit-learn team

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check documentation files
- Review troubleshooting section

## 🗺️ Roadmap

- [ ] Social features (follow users, share lists)
- [ ] Movie trailers integration
- [ ] Advanced filters (year, director, actors)
- [ ] Mobile app (React Native)
- [ ] Collaborative watchlists
- [ ] Movie discussion forums
- [ ] Integration with streaming services
- [ ] Multi-language support

---

**Built with ❤️ using React, Flask, and Machine Learning**
