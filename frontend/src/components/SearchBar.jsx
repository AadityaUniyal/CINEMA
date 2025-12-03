import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const searchRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.trim().length < 2) {
        setSuggestions([]);
        setShowSuggestions(false);
        return;
      }

      try {
        const response = await axios.get(`${API_BASE_URL}/api/search?q=${query}&limit=5`);
        setSuggestions(response.data.results || []);
        setShowSuggestions(true);
      } catch (error) {
        console.error('Suggestion error:', error);
      }
    };

    const debounce = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(debounce);
  }, [query]);

  const handleSearch = useCallback(async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setShowSuggestions(false);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/search?q=${query}`);
      onSearch(response.data.results);
    } catch (error) {
      console.error('Search error:', error);
    }
    setIsSearching(false);
  }, [query, onSearch]);

  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setShowSuggestions(false);
    onSearch(null);
  };

  const handleSuggestionClick = (movie) => {
    setQuery(movie.title);
    setShowSuggestions(false);
    onSearch([movie]);
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => 
        prev < suggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      handleSuggestionClick(suggestions[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  return (
    <div className="search-bar" ref={searchRef}>
      <form onSubmit={handleSearch}>
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search movies by title..."
            autoComplete="off"
          />
          {query && (
            <button type="button" onClick={handleClear} className="clear-btn">
              ✕
            </button>
          )}
        </div>
        <button type="submit" disabled={isSearching} className="search-submit-btn">
          {isSearching ? <span className="spinner"></span> : 'Search'}
        </button>
      </form>

      {showSuggestions && suggestions.length > 0 && (
        <div className="search-suggestions">
          <div className="suggestions-header">
            <span>🎬 Suggestions</span>
          </div>
          {suggestions.map((movie, index) => (
            <div
              key={movie.movieId}
              className={`suggestion-item ${index === selectedIndex ? 'selected' : ''}`}
              onClick={() => handleSuggestionClick(movie)}
            >
              <div className="suggestion-icon">🎬</div>
              <div className="suggestion-content">
                <div className="suggestion-title">{movie.title}</div>
                <div className="suggestion-genres">{movie.genres}</div>
              </div>
              {movie.avg_rating && (
                <div className="suggestion-rating">
                  ⭐ {movie.avg_rating.toFixed(1)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
