import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MovieCard from './MovieCard';

const Recommendations = ({ userId }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchRecommendations();
  }, [userId]);

  const fetchRecommendations = async () => {
    if (recommendations.length > 0) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);
    
    try {
      const response = await axios.get(`http://localhost:5000/api/recommendations/${userId}`, {
        params: { n: 24 }
      });
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setError('Unable to generate recommendations. Try rating more movies.');
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

  return (
    <div className="recommendations">
      <h2>Recommended For You</h2>
      <p className="subtitle">Personalized picks based on your taste</p>
      
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
              onUpdate={fetchRecommendations}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Recommendations;
