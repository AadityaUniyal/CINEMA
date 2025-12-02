import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/Dashboard.css';

const Dashboard = ({ userId }) => {
  const [userStats, setUserStats] = useState(null);
  const [userReviews, setUserReviews] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [userProfile, setUserProfile] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, [userId]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, reviewsRes, watchlistRes, profileRes] = await Promise.all([
        axios.get(`http://localhost:5000/api/user/${userId}/stats`),
        axios.get(`http://localhost:5000/api/reviews/user/${userId}`),
        axios.get(`http://localhost:5000/api/watchlist/${userId}`),
        axios.get(`http://localhost:5000/api/auth/profile/${userId}`)
      ]);

      setUserStats(statsRes.data || {
        total_ratings: 0,
        avg_rating: 0,
        favorite_genres: []
      });
      
      const reviews = reviewsRes.data.reviews || [];
      
      if (reviews.length > 0) {
        const movieIds = reviews.map(r => r.movieId);
        try {
          const moviesRes = await axios.get('http://localhost:5000/api/movies', {
            params: { per_page: 1000 }
          });
          const moviesMap = {};
          moviesRes.data.movies.forEach(m => {
            moviesMap[m.movieId] = m.title;
          });
          reviews.forEach(r => {
            r.movieTitle = moviesMap[r.movieId] || `Movie #${r.movieId}`;
          });
        } catch (err) {
          console.error('Error fetching movie titles:', err);
        }
      }
      
      setUserReviews(reviews);
      setWatchlist(watchlistRes.data.watchlist || []);
      setUserProfile(profileRes.data.profile);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      
      setUserStats({
        total_ratings: 0,
        avg_rating: 0,
        favorite_genres: []
      });
      setUserReviews([]);
      setWatchlist([]);
      setUserProfile(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner-large"></div>
        <p>Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="user-profile">
          <div className="user-avatar">
            <span>{userProfile?.name ? userProfile.name.charAt(0).toUpperCase() : userId}</span>
          </div>
          <div className="user-info">
            <h1>{userProfile?.name || `User ${userId}`}</h1>
            <p className="user-subtitle">Movie Enthusiast</p>
          </div>
        </div>

        <div className="dashboard-stats-cards">
          <div className="stat-card">
            <div className="stat-icon">🎬</div>
            <div className="stat-content">
              <div className="stat-value">{userStats?.total_ratings || 0}</div>
              <div className="stat-label">Movies Rated</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-content">
              <div className="stat-value">{userStats?.avg_rating?.toFixed(1) || 'N/A'}</div>
              <div className="stat-label">Avg Rating</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">💬</div>
            <div className="stat-content">
              <div className="stat-value">{userReviews.length}</div>
              <div className="stat-label">Reviews</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📋</div>
            <div className="stat-content">
              <div className="stat-value">{watchlist.length}</div>
              <div className="stat-label">Watchlist</div>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'reviews' ? 'active' : ''}`}
          onClick={() => setActiveTab('reviews')}
        >
          My Reviews
        </button>
        <button
          className={`tab-btn ${activeTab === 'watchlist' ? 'active' : ''}`}
          onClick={() => setActiveTab('watchlist')}
        >
          Watchlist
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            {userStats?.total_ratings === 0 && userReviews.length === 0 && watchlist.length === 0 ? (
              <div className="welcome-message">
                <div className="welcome-icon">🎬</div>
                <h2>Welcome to CINÉMA!</h2>
                <p>You're all set to start your movie journey.</p>
                <div className="welcome-actions">
                  <div className="welcome-step">
                    <span className="step-number">1</span>
                    <span className="step-text">Browse movies and rate them</span>
                  </div>
                  <div className="welcome-step">
                    <span className="step-number">2</span>
                    <span className="step-text">Write reviews to share your thoughts</span>
                  </div>
                  <div className="welcome-step">
                    <span className="step-number">3</span>
                    <span className="step-text">Add movies to your watchlist</span>
                  </div>
                  <div className="welcome-step">
                    <span className="step-number">4</span>
                    <span className="step-text">Get personalized recommendations</span>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {userProfile?.preferredGenres && userProfile.preferredGenres.length > 0 && (
                  <div className="favorite-genres">
                    <h2>❤️ Preferred Genres</h2>
                    <div className="genres-list">
                      {userProfile.preferredGenres.map((genre, idx) => (
                        <div key={idx} className="genre-badge preferred">
                          <span className="genre-name">{genre}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="favorite-genres">
                  <h2>🎭 Favorite Genres (Based on Ratings)</h2>
                  {userStats?.favorite_genres?.length > 0 ? (
                    <div className="genres-list">
                      {userStats.favorite_genres.map((genre, idx) => (
                        <div key={idx} className="genre-badge">
                          <span className="genre-rank">#{idx + 1}</span>
                          <span className="genre-name">{genre}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state-small">
                      <p>Start rating movies to discover your favorite genres!</p>
                    </div>
                  )}
                </div>

                <div className="activity-summary">
                  <h2>📊 Activity Summary</h2>
                  <div className="activity-grid">
                    <div className="activity-item">
                      <span className="activity-label">Total Ratings</span>
                      <span className="activity-value">{userStats?.total_ratings || 0}</span>
                    </div>
                    <div className="activity-item">
                      <span className="activity-label">Reviews Written</span>
                      <span className="activity-value">{userReviews.length}</span>
                    </div>
                    <div className="activity-item">
                      <span className="activity-label">Movies in Watchlist</span>
                      <span className="activity-value">{watchlist.length}</span>
                    </div>
                    <div className="activity-item">
                      <span className="activity-label">Average Rating</span>
                      <span className="activity-value">{userStats?.avg_rating?.toFixed(2) || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {activeTab === 'reviews' && (
          <div className="reviews-section">
            <h2>💬 My Reviews ({userReviews.length})</h2>
            {userReviews.length === 0 ? (
              <div className="empty-state">
                <p>You haven't written any reviews yet.</p>
                <p>Start rating and reviewing movies!</p>
              </div>
            ) : (
              <div className="reviews-grid">
                {userReviews.map((review, idx) => (
                  <div key={idx} className="review-card">
                    <div className="review-card-header">
                      <span className="review-movie-title">{review.movieTitle || `Movie #${review.movieId}`}</span>
                      <span className="review-stars">{'⭐'.repeat(review.rating)}</span>
                    </div>
                    {review.comment && (
                      <p className="review-comment">{review.comment}</p>
                    )}
                    <div className="review-footer">
                      <span className="review-author">
                        By {userProfile?.name?.split(' ')[0] || 'You'}
                      </span>
                      <span className="review-date">
                        {new Date(review.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'watchlist' && (
          <div className="watchlist-section">
            <h2>📋 My Watchlist ({watchlist.length})</h2>
            {watchlist.length === 0 ? (
              <div className="empty-state">
                <p>Your watchlist is empty.</p>
                <p>Add movies you want to watch later!</p>
              </div>
            ) : (
              <div className="watchlist-grid">
                {watchlist.map((movie) => (
                  <div key={movie.movieId} className="watchlist-card">
                    <div className="watchlist-poster">🎬</div>
                    <div className="watchlist-info">
                      <h3>{movie.title}</h3>
                      <p className="watchlist-genres">{movie.genres}</p>
                      <div className="watchlist-rating">
                        ⭐ {movie.avg_rating?.toFixed(1) || 'N/A'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
