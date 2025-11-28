import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import SearchBar from './SearchBar';
import MovieCard from './MovieCard';
import TrendingGenres from './TrendingGenres';

const MovieList = ({ userId }) => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [genres, setGenres] = useState([]);
  const [searchResults, setSearchResults] = useState(null);

  useEffect(() => {
    fetchGenres();
  }, []);

  useEffect(() => {
    fetchMovies();
  }, [page, selectedGenre]);

  const fetchGenres = async () => {
    try {
      const response = await axios.get('http:
      setGenres(response.data.genres);
    } catch (error) {
      console.error('Error fetching genres:', error);
    }
  };

  const fetchMovies = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 24 };
      if (selectedGenre) params.genre = selectedGenre;
      
      const response = await axios.get('http:
      setMovies(response.data.movies);
      setTotalPages(response.data.total_pages);
      setSearchResults(null);
    } catch (error) {
      console.error('Error fetching movies:', error);
    }
    setLoading(false);
  }, [page, selectedGenre]);

  const handleSearch = (results) => {
    setSearchResults(results);
    setPage(1);
  };

  const handleGenreChange = (e) => {
    setSelectedGenre(e.target.value);
    setPage(1);
    setSearchResults(null);
  };

  const handleTrendingGenreClick = (genre) => {
    setSelectedGenre(genre);
    setPage(1);
    setSearchResults(null);
    window.scrollTo({ top: 300, behavior: 'smooth' });
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const displayMovies = searchResults || movies;

  if (loading) {
    return <div className="loading">Loading movies...</div>;
  }

  return (
    <div className="movie-list">
      <SearchBar onSearch={handleSearch} />
      
      <TrendingGenres onGenreClick={handleTrendingGenreClick} />
      
      <div className="filters">
        <select value={selectedGenre} onChange={handleGenreChange} className="genre-select">
          <option value="">All Genres</option>
          {genres.map(genre => (
            <option key={genre} value={genre}>{genre}</option>
          ))}
        </select>
        {selectedGenre && (
          <button 
            onClick={() => setSelectedGenre('')} 
            className="clear-filter"
          >
            ✕ Clear Filter
          </button>
        )}
      </div>

      {displayMovies.length === 0 ? (
        <div className="empty-state">
          <h2>No movies found</h2>
          <p>Try adjusting your filters or search query</p>
        </div>
      ) : (
        <>
          <div className="movies-grid">
            {displayMovies.map((movie) => (
              <MovieCard 
                key={movie.movieId} 
                movie={movie} 
                userId={userId}
                onUpdate={fetchMovies}
              />
            ))}
          </div>

          {!searchResults && totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                className="pagination-btn"
              >
                ← Previous
              </button>
              <span className="page-info">Page {page} of {totalPages}</span>
              <button 
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages}
                className="pagination-btn"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MovieList;
