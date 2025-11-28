import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Watchlist = ({ userId }) => {
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWatchlist();
  }, [userId]);

  const fetchWatchlist = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http:
      setWatchlist(response.data.watchlist);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFromWatchlist = async (movieId, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`http:
      setWatchlist(prev => prev.filter(m => m.movieId !== movieId));
    } catch (error) {
      console.error('Error removing from watchlist:', error);
    }
  };

  const markAsWatched = async (movieId, e) => {
    e.stopPropagation();
    try {
      await axios.put(`http:
      setWatchlist(prev => prev.filter(m => m.movieId !== movieId));
    } catch (error) {
      console.error('Error marking as watched:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading your list</div>;
  }

  return (
    <div className="watchlist">
      <h2>My List</h2>
      <p className="subtitle">Movies you want to watch</p>
      
      {watchlist.length === 0 ? (
        <div className="empty-state">
          <h3>Your list is empty</h3>
          <p>Add movies you want to watch to your list</p>
        </div>
      ) : (
        <div className="watchlist-grid">
          {watchlist.map((movie) => (
            <div key={movie.movieId} className="watchlist-item">
              <div className="movie-card-inner">
                <h3>{movie.title}</h3>
                <p className="genres">{movie.genres}</p>
                <div className="movie-stats">
                  <span>⭐ {movie.avg_rating?.toFixed(1) || 'N/A'}</span>
                  <span>{movie.rating_count || 0} ratings</span>
                </div>
                <div className="watchlist-actions">
                  <button onClick={(e) => markAsWatched(movie.movieId, e)}>
                    ✓ Watched
                  </button>
                  <button onClick={(e) => removeFromWatchlist(movie.movieId, e)}>
                    ✕ Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Watchlist;
