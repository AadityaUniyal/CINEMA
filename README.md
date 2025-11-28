# 🎬 CINÉMA - AI-Powered Movie Recommendation Platform

A premium Netflix-style movie recommendation platform with ML-powered suggestions, user authentication, personalized dashboards, and real-time reviews.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🔐 User Authentication
- Secure registration with email and password
- Password validation (8+ chars, uppercase, lowercase, number)
- Auto-generated unique 8-digit User IDs
- SHA-256 password hashing
- Personal user profiles

### 🎭 Genre Preferences
- Interactive genre selection on first login
- Minimum 2 genres required
- Personalized recommendations based on preferences
- Stored in user profile

### 🎬 Movie Browsing
- 20,000+ movies from MovieLens dataset
- Smart search with real-time autocomplete
- Trending genres with clickable chips
- Genre filtering and pagination
- Movie ratings and reviews

### ⭐ Rating & Review System
- 5-star rating system
- Write detailed reviews with comments
- View all reviews for any movie
- Reviews show user names (first name)
- Stored in MongoDB with timestamps

### ❤️ Watchlist Management
- One-click add/remove with heart icon
- White heart (🤍) = Not in watchlist
- Red heart (❤️) = In watchlist
- Heartbeat animation on add
- Syncs across all tabs

### 📊 Personal Dashboard
- User statistics (total ratings, average rating)
- Preferred genres (user-selected)
- Favorite genres (calculated from ratings)
- All your reviews with movie titles
- Watchlist management
- Activity summary

### 🎯 ML-Powered Recommendations
- Hybrid collaborative + content-based filtering
- Personalized based on your ratings
- Filtered by preferred genres
- Similar users discovery
- Updates as you rate more movies

### 📈 Analytics
- Platform-wide statistics
- Top rated movies
- Genre distribution
- Rating trends over time
- User activity metrics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account (free tier)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/cinema.git
cd cinema
```

### 2. Setup MongoDB Atlas
1. Create account at https://cloud.mongodb.com
2. Create a cluster (free tier)
3. Create database user with password
4. Get connection string
5. Update `backend/config.py` with your connection string:
```python
MONGO_URI = 'mongodb+srv://username:password@cluster.mongodb.net/'
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 4. Load Data to MongoDB
```bash
cd backend
python init_db.py
```

### 5. Start the Application

**Backend (Terminal 1):**
```bash
cd backend
python app.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm start
```

### 6. Access the App
Open http://localhost:3000 in your browser

---

## 🎯 Usage

### First Time User
1. **Register**: Enter name, email, and password
2. **Get User ID**: Note your unique 8-digit ID
3. **Select Genres**: Choose at least 2 favorite genres
4. **Browse Movies**: Explore 20,000+ movies
5. **Rate & Review**: Share your opinions
6. **Get Recommendations**: Personalized suggestions

### Returning User
1. **Login**: Use your email and password
2. **Browse**: Search and filter movies
3. **Watchlist**: Click hearts to save movies
4. **Dashboard**: View your statistics and activity

---

## 🏗️ Project Structure

```
cinema/
├── backend/                    # Flask API
│   ├── app.py                 # Main application (20+ endpoints)
│   ├── config.py              # Configuration
│   ├── user_auth.py           # Authentication system
│   ├── reviews_manager.py     # Reviews management
│   ├── data_processor.py      # Data processing
│   ├── ml_engine.py           # ML recommendation engine
│   ├── watchlist.py           # Watchlist management
│   ├── init_db.py             # Database initialization
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx           # Authentication
│   │   │   ├── GenrePreference.jsx # Genre selection
│   │   │   ├── Dashboard.jsx       # User dashboard
│   │   │   ├── MovieList.jsx       # Movie browsing
│   │   │   ├── MovieCard.jsx       # Movie card with heart
│   │   │   ├── SearchBar.jsx       # Search with autocomplete
│   │   │   ├── TrendingGenres.jsx  # Trending genres
│   │   │   ├── Recommendations.jsx # ML recommendations
│   │   │   ├── Watchlist.jsx       # Watchlist management
│   │   │   └── Analytics.jsx       # Platform analytics
│   │   ├── styles/
│   │   │   ├── Login.css
│   │   │   ├── GenrePreference.css
│   │   │   └── Dashboard.css
│   │   ├── App.js             # Main application
│   │   └── App.css            # Global styles
│   └── package.json
│
├── movies.csv                 # Movie data (20,000 movies)
├── ratings.csv                # Rating data (20,000 ratings)
├── docker-compose.yml         # Docker configuration
└── README.md                  # This file
```

---

## 🎨 Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: MongoDB Atlas
- **ML**: scikit-learn, pandas, numpy
- **Auth**: SHA-256 password hashing
- **Caching**: In-memory cache

### Frontend
- **Framework**: React 18
- **Styling**: CSS3 with animations
- **HTTP**: Axios
- **State**: React Hooks

### Database
- **Provider**: MongoDB Atlas (Free Tier)
- **Collections**: users, user_profiles, movies, ratings, reviews
- **Size**: ~2 MB (optimized)

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile/:userId` - Get user profile

### Movies
- `GET /api/movies` - Get movies with pagination
- `GET /api/movies/:id` - Get movie details
- `GET /api/search?q=<query>` - Search movies
- `GET /api/genres` - Get all genres

### Recommendations
- `GET /api/recommendations/:userId` - Get personalized recommendations
- `GET /api/similar-users/:userId` - Find similar users

### Reviews
- `GET /api/reviews/:movieId` - Get movie reviews
- `POST /api/reviews` - Add review
- `GET /api/reviews/user/:userId` - Get user reviews

### User Preferences
- `POST /api/user/preferences` - Save genre preferences

### Watchlist
- `GET /api/watchlist/:userId` - Get watchlist
- `POST /api/watchlist/:userId/:movieId` - Add to watchlist
- `DELETE /api/watchlist/:userId/:movieId` - Remove from watchlist

### Analytics
- `GET /api/analytics/trending-genres` - Get trending genres
- `GET /api/analytics/top-rated` - Get top rated movies
- `GET /api/analytics/genre-distribution` - Genre statistics

---

## 🎨 UI Features

### Design
- Netflix-inspired dark theme
- Red accent color (#e50914)
- Glass-morphism effects
- Smooth animations (60fps)
- Responsive design (mobile, tablet, desktop)

### Animations
- Login page floating shapes
- Smooth page transitions
- Hover effects on cards
- Loading spinners
- Heartbeat animation on watchlist add
- Slide-down dropdowns

### Interactions
- Keyboard navigation (arrows, enter, escape)
- Click outside to close
- Smooth scrolling
- Touch-friendly buttons

---

## 🐳 Docker Support

### Using Docker Compose
```bash
docker-compose up -d
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

---

## 🧪 Testing

### Test API Endpoints
```bash
python test_api.py
```

### Test New Features
```bash
python test_new_features.py
```

---

## 📝 Documentation

- `README.md` - Main documentation (this file)
- `QUICK_GUIDE.md` - Quick user guide
- `API_REFERENCE.md` - Complete API documentation
- `ARCHITECTURE.md` - System architecture
- `DEPLOYMENT.md` - Production deployment guide

---

## 🔒 Security

- SHA-256 password hashing
- Unique email constraint
- Password validation (8+ chars, uppercase, lowercase, number)
- Input validation on all endpoints
- CORS enabled for frontend

---

## 🐛 Troubleshooting

### MongoDB Connection Error
- Check your connection string in `backend/config.py`
- Ensure MongoDB Atlas cluster is running
- Verify database user credentials
- Check IP whitelist in MongoDB Atlas

### Port Already in Use
- Backend (5000): Change port in `backend/app.py`
- Frontend (3000): React will prompt to use another port

### Module Not Found
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- MovieLens dataset for movie data
- Netflix for UI inspiration
- React and Flask communities

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

## 🎬 Screenshots

### Login Page
Beautiful animated login with Netflix-style background.

### Genre Selection
Interactive genre selection with minimum 2 genres required.

### Movie Browsing
Browse 20,000+ movies with search, filters, and trending genres.

### Dashboard
Personal dashboard with statistics, reviews, and watchlist.

### Recommendations
ML-powered personalized movie recommendations.

---

**Built with ❤️ using React, Flask, and MongoDB**

**⭐ Star this repo if you find it useful!**
