import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config';
import MovieCard from './MovieCard';

const Recommendations = ({ userId }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [userRatingCount, setUserRatingCount] = useState(0);

  useEffect(() => {
    fetchRecommendations();
    fetchUserStats();
  }, [userId]);

  const fetchUserStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/user/${userId}/stats`);
      setUserRatingCount(response.data.total_ratings || 0);
    } catch (error) {
      console.error('Error fetching user stats:', error);
    }
  };

  const fetchRecommendations = async () => {
    if (recommendations.length > 0) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);
    
    try {
      // Try ML endpoint first
      const response = await axios.get(`${API_BASE_URL}/api/ml/recommendations/${userId}`, {
        params: { n: 24 }
      });
      
      // Fetch confidence scores (predicted ratings) for each recommendation
      const recommendationsWithConfidence = await Promise.all(
        response.data.recommendations.map(async (movie) => {
          try {
            const predictionResponse = await axios.post(`${API_BASE_URL}/api/ml/predict`, {
              userId,
              movieId: movie.movieId
            });
            return {
              ...movie,
              confidence: predictionResponse.data.predicted_rating,
              mlBased: true
            };
          } catch (err) {
            // If prediction fails, return movie without confidence
            return { ...movie, mlBased: true };
          }
        })
      );
      
      setRecommendations(recommendationsWithConfidence);
    } catch (error) {
      console.error('Error fetching ML recommendations:', error);
      
      // Fallback to hybrid recommendations
      try {
        const fallbackResponse = await axios.get(`${API_BASE_URL}/api/recommendations/${userId}`, {
          params: { n: 24 }
        });
        setRecommendations(fallbackResponse.data.recommendations.map(m => ({ ...m, mlBased: false })));
      } catch (fallbackError) {
        console.error('Error fetching fallback recommendations:', fallbackError);
        setError('Unable to generate recommendations. Try rating more movies.');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return <div className="loading">Generating your personalized recommendations</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error">{error}</div>
        <button onClick={fetchRecommendations} className="refresh-btn">
          Try Again
        </button>
      </div>
    );
  }

  const getConfidenceLevel = () => {
    if (userRatingCount < 5) return 'low';
    if (userRatingCount < 20) return 'medium';
    return 'high';
  };

  const getConfidenceMessage = () => {
    const level = getConfidenceLevel();
    if (level === 'low') {
      return `Rate ${5 - userRatingCount} more movies to improve recommendation accuracy`;
    }
    if (level === 'medium') {
      return `Rate ${20 - userRatingCount} more movies for even better recommendations`;
    }
    return 'Great! Your recommendations are highly personalized';
  };

  return (
    <div className="recommendations">
      <h2>Recommended For You</h2>
      <p className="subtitle">Personalized picks based on your taste</p>
      
      {userRatingCount > 0 && (
        <div className={`recommendation-confidence ${getConfidenceLevel()}`}>
          <div className="confidence-indicator">
            <span className="confidence-icon">
              {getConfidenceLevel() === 'low' && '📊'}
              {getConfidenceLevel() === 'medium' && '📈'}
              {getConfidenceLevel() === 'high' && '✨'}
            </span>
            <span className="confidence-text">{getConfidenceMessage()}</span>
          </div>
          <div className="rating-progress">
            <div 
              className="progress-bar" 
              style={{ width: `${Math.min((userRatingCount / 20) * 100, 100)}%` }}
            />
          </div>
        </div>
      )}
      
      <button 
        onClick={fetchRecommendations} 
        className="refresh-btn"
        disabled={refreshing}
      >
        {refreshing ? '🔄 Refreshing...' : '🔄 Refresh Recommendations'}
      </button>

      {recommendations.length === 0 ? (
        <div className="empty-state">
          <h3>Start Your Journey</h3>
          <p>Rate some movies to get personalized recommendations!</p>
        </div>
      ) : (
        <div className="movies-grid">
          {recommendations.map((movie) => (
            <MovieCard 
              key={movie.movieId} 
              movie={movie} 
              userId={userId}
              onUpdate={() => {
                fetchRecommendations();
                fetchUserStats();
              }}
              showConfidence={true}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Recommendations;
