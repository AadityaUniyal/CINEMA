import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TrendingGenres = ({ onGenreClick }) => {
  const [trendingGenres, setTrendingGenres] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrendingGenres();
  }, []);

  const fetchTrendingGenres = async () => {
    try {
      const response = await axios.get('http:
      setTrendingGenres(response.data.trending_genres || []);
    } catch (error) {
      console.error('Error fetching trending genres:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="trending-genres loading">Loading trending genres...</div>;
  }

  return (
    <div className="trending-genres">
      <h3>🔥 Trending Genres</h3>
      <div className="genre-chips">
        {trendingGenres.map((item, idx) => (
          <button
            key={idx}
            className="genre-chip"
            onClick={() => onGenreClick(item.genre)}
          >
            {item.genre}
            <span className="genre-count">{item.count}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default TrendingGenres;
