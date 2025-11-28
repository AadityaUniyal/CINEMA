import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MovieCard from './MovieCard';

const Favorites = ({ userId }) => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFavorites();
  }, [userId]);

  const fetchFavorites = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/favorites/${userId}`);
      setFavorites(response.data.favorites);
    } catch (error) {
      console.error('Error fetching favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = () => {
    fetchFavorites();
  };

  if (loading) {
    return <div className="loading">Loading your favorites</div>;
  }

  return (
    <div className="favorites">
      <h2>My Favorites</h2>
      <p className="subtitle">Movies you've marked as favorites</p>

      {favorites.length === 0 ? (
        <div className="empty-state">
          <h3>No favorites yet</h3>
          <p>Start adding movies to your favorites by clicking the ❤️ button</p>
        </div>
      ) : (
        <div className="movies-grid">
          {favorites.map((movie) => (
            <MovieCard
              key={movie.movieId}
              movie={movie}
              userId={userId}
              onUpdate={handleRemove}
              showFavorite={true}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Favorites;
