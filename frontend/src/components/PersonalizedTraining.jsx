import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config';
import '../styles/PersonalizedTraining.css';

const PersonalizedTraining = ({ userId }) => {
  const [preferences, setPreferences] = useState({
    favoriteGenres: [],
    minRating: 3.5,
    diversityWeight: 0.5,
    popularityWeight: 0.3,
    recencyWeight: 0.2
  });
  const [genres, setGenres] = useState([]);
  const [training, setTraining] = useState(false);
  const [result, setResult] = useState(null);
  const [userStats, setUserStats] = useState(null);

  useEffect(() => {
    fetchGenres();
    fetchUserStats();
    loadUserPreferences();
  }, [userId]);

  const fetchGenres = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/genres`);
      setGenres(response.data.genres);
    } catch (error) {
      console.error('Error fetching genres:', error);
    }
  };

  const fetchUserStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/user/${userId}/stats`);
      setUserStats(response.data);
    } catch (error) {
      console.error('Error fetching user stats:', error);
    }
  };

  const loadUserPreferences = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/user/${userId}/training-preferences`);
      if (response.data.preferences) {
        setPreferences(response.data.preferences);
      }
    } catch (error) {
      console.log('No saved preferences, using defaults');
    }
  };

  const handleGenreToggle = (genre) => {
    setPreferences(prev => ({
      ...prev,
      favoriteGenres: prev.favoriteGenres.includes(genre)
        ? prev.favoriteGenres.filter(g => g !== genre)
        : [...prev.favoriteGenres, genre]
    }));
  };

  const handleSliderChange = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: parseFloat(value)
    }));
  };

  const handleTrainPersonalModel = async () => {
    setTraining(true);
    setResult(null);

    try {
      // Save preferences first
      await axios.post(`${API_BASE_URL}/api/user/${userId}/training-preferences`, {
        preferences
      });

      // Train personalized model
      const response = await axios.post(`${API_BASE_URL}/api/ml/train-personal`, {
        userId,
        preferences
      });

      setResult({
        success: true,
        message: 'Your personalized model has been trained!',
        data: response.data
      });

      fetchUserStats();
    } catch (error) {
      setResult({
        success: false,
        message: error.response?.data?.error || 'Training failed. Please try again.'
      });
    } finally {
      setTraining(false);
    }
  };

  const normalizeWeights = () => {
    const total = preferences.diversityWeight + preferences.popularityWeight + preferences.recencyWeight;
    if (total > 0) {
      setPreferences(prev => ({
        ...prev,
        diversityWeight: prev.diversityWeight / total,
        popularityWeight: prev.popularityWeight / total,
        recencyWeight: prev.recencyWeight / total
      }));
    }
  };

  return (
    <div className="personalized-training">
      <div className="training-header">
        <h1>🎯 Train Your Personal Model</h1>
        <p>Customize your recommendation model based on your preferences</p>
      </div>

      {userStats && (
        <div className="user-stats-card">
          <h3>Your Activity</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Movies Rated</span>
              <span className="stat-value">{userStats.total_ratings}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Average Rating</span>
              <span className="stat-value">{userStats.avg_rating?.toFixed(1)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Genres Explored</span>
              <span className="stat-value">{userStats.genres_rated?.length || 0}</span>
            </div>
          </div>
        </div>
      )}

      <div className="preferences-section">
        <h2>1. Select Your Favorite Genres</h2>
        <p className="section-description">Choose genres you want to see more of in recommendations</p>
        <div className="genres-grid">
          {genres.map(genre => (
            <button
              key={genre}
              className={`genre-chip ${preferences.favoriteGenres.includes(genre) ? 'selected' : ''}`}
              onClick={() => handleGenreToggle(genre)}
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      <div className="preferences-section">
        <h2>2. Set Your Priorities</h2>
        <p className="section-description">Adjust how the model weighs different factors</p>
        
        <div className="slider-group">
          <div className="slider-item">
            <label>
              <span className="slider-label">🎲 Diversity</span>
              <span className="slider-value">{(preferences.diversityWeight * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={preferences.diversityWeight}
              onChange={(e) => handleSliderChange('diversityWeight', e.target.value)}
              onMouseUp={normalizeWeights}
              onTouchEnd={normalizeWeights}
            />
            <p className="slider-description">Show me varied and unexpected movies</p>
          </div>

          <div className="slider-item">
            <label>
              <span className="slider-label">⭐ Popularity</span>
              <span className="slider-value">{(preferences.popularityWeight * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={preferences.popularityWeight}
              onChange={(e) => handleSliderChange('popularityWeight', e.target.value)}
              onMouseUp={normalizeWeights}
              onTouchEnd={normalizeWeights}
            />
            <p className="slider-description">Recommend popular and highly-rated movies</p>
          </div>

          <div className="slider-item">
            <label>
              <span className="slider-label">🆕 Recency</span>
              <span className="slider-value">{(preferences.recencyWeight * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={preferences.recencyWeight}
              onChange={(e) => handleSliderChange('recencyWeight', e.target.value)}
              onMouseUp={normalizeWeights}
              onTouchEnd={normalizeWeights}
            />
            <p className="slider-description">Prefer newer releases</p>
          </div>
        </div>
      </div>

      <div className="preferences-section">
        <h2>3. Quality Threshold</h2>
        <p className="section-description">Minimum rating for recommended movies</p>
        
        <div className="slider-item">
          <label>
            <span className="slider-label">Minimum Rating</span>
            <span className="slider-value">{preferences.minRating.toFixed(1)} ⭐</span>
          </label>
          <input
            type="range"
            min="1"
            max="5"
            step="0.5"
            value={preferences.minRating}
            onChange={(e) => handleSliderChange('minRating', e.target.value)}
          />
          <p className="slider-description">Only recommend movies rated {preferences.minRating} or higher</p>
        </div>
      </div>

      <div className="training-action">
        <button
          className="train-personal-btn"
          onClick={handleTrainPersonalModel}
          disabled={training || preferences.favoriteGenres.length === 0}
        >
          {training ? '⏳ Training Your Model...' : '🚀 Train My Personal Model'}
        </button>
        
        {preferences.favoriteGenres.length === 0 && (
          <p className="warning-text">Please select at least one favorite genre</p>
        )}
      </div>

      {result && (
        <div className={`training-result ${result.success ? 'success' : 'error'}`}>
          <h3>{result.success ? '✅ Success!' : '❌ Error'}</h3>
          <p>{result.message}</p>
          {result.success && result.data && (
            <div className="result-details">
              <p><strong>Model Version:</strong> {result.data.version}</p>
              <p><strong>Trained on:</strong> {result.data.training_data?.n_ratings} ratings</p>
              <p><strong>Your preferences applied:</strong></p>
              <ul>
                <li>{preferences.favoriteGenres.length} favorite genres</li>
                <li>Diversity: {(preferences.diversityWeight * 100).toFixed(0)}%</li>
                <li>Popularity: {(preferences.popularityWeight * 100).toFixed(0)}%</li>
                <li>Recency: {(preferences.recencyWeight * 100).toFixed(0)}%</li>
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="info-section">
        <h3>💡 How It Works</h3>
        <ul>
          <li><strong>Favorite Genres:</strong> The model will prioritize movies from these genres</li>
          <li><strong>Diversity:</strong> Higher values show you more varied, unexpected recommendations</li>
          <li><strong>Popularity:</strong> Higher values recommend well-known, highly-rated movies</li>
          <li><strong>Recency:</strong> Higher values prefer newer releases over classics</li>
          <li><strong>Quality Threshold:</strong> Filters out low-rated movies from recommendations</li>
        </ul>
        <p className="tip">💡 Tip: Train your model after rating at least 10-20 movies for best results!</p>
      </div>
    </div>
  );
};

export default PersonalizedTraining;
