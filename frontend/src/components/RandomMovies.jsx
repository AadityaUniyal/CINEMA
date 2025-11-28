import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MovieCard from './MovieCard';

const RandomMovies = ({ userId }) => {
  const [movies, setMovies] = useState([]);
  const [genre, setGenre] = useState('');
  const [genres, setGenres] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchGenres();
    fetchRandomMovies();
  }, []);

  const fetchGenres = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/genres');
      setGenres(response.data.genres);
    } catch (error) {
      console.error('Error fetching genres:', error);
    }
  };

  const fetchRandomMovies = async () => {
    setLoading(true);
    try {
      const params = { n: 24 };
      if (genre) params.genre = genre;
      
      const response = await axios.get('http://localhost:5000/api/movies/random', { params });
      setMovies(response.data.movies);
    } catch (error) {
      console.error('Error fetching random movies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenreChange = (e) => {
    setGenre(e.target.value);
  };

  const handleDiscover = () => {
    fetchRandomMovies();
  };

  return (
    <div className="random-movies">
      <h2>Discover Something New</h2>
      <p className="subtitle">Explore random movies and find hidden gems</p>
      
      <div className="discovery-controls">
        <select value={genre} onChange={handleGenreChange}>
          <option value="">All Genres</option>
          {genres.map(g => (
            <option key={g} value={g}>{g}</option>
          ))}
        </select>
        <button onClick={handleDiscover} disabled={loading}>
          {loading ? '🎲 Discovering...' : '🎲 Discover Movies'}
        </button>
      </div>
      
      {loading ? (
        <div className="loading">Finding movies for you</div>
      ) : movies.length === 0 ? (
        <div className="empty-state">
          <h3>Click "Discover Movies" to start</h3>
          <p>We'll show you random movies based on your selected genre</p>
        </div>
      ) : (
        <div className="movies-grid">
          {movies.map((movie) => (
            <MovieCard 
              key={movie.movieId} 
              movie={movie} 
              userId={userId}
              onUpdate={fetchRandomMovies}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default RandomMovies;
