import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config';
import '../styles/GenrePreference.css';

const GenrePreference = ({ userId, onComplete }) => {
  const [genres, setGenres] = useState([]);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchGenres();
  }, []);

  const fetchGenres = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/genres`);
      setGenres(response.data.genres || []);
    } catch (error) {
      console.error('Error fetching genres:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleGenre = (genre) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter(g => g !== genre));
    } else {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  const handleSubmit = async () => {
    if (selectedGenres.length < 2) {
      alert('Please select at least 2 genres');
      return;
    }

    setSaving(true);
    try {
      await axios.post(`${API_BASE_URL}/api/user/preferences`, {
        userId,
        preferredGenres: selectedGenres
      });
      onComplete(selectedGenres);
    } catch (error) {
      console.error('Error saving preferences:', error);
      alert('Failed to save preferences. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="genre-preference-page">
        <div className="loading">Loading genres...</div>
      </div>
    );
  }

  return (
    <div className="genre-preference-page">
      <div className="genre-preference-background">
        <div className="gradient-overlay"></div>
      </div>

      <div className="genre-preference-content">
        <div className="preference-header">
          <h1>🎬 Choose Your Favorite Genres</h1>
          <p>Select at least 2 genres to personalize your experience</p>
          <div className="selection-count">
            {selectedGenres.length} selected
            {selectedGenres.length >= 2 && ' ✓'}
          </div>
        </div>

        <div className="genres-grid">
          {genres.map((genre) => (
            <button
              key={genre}
              className={`genre-option ${selectedGenres.includes(genre) ? 'selected' : ''}`}
              onClick={() => toggleGenre(genre)}
            >
              <span className="genre-name">{genre}</span>
              {selectedGenres.includes(genre) && (
                <span className="check-icon">✓</span>
              )}
            </button>
          ))}
        </div>

        <div className="preference-actions">
          <button
            className="submit-preferences-btn"
            onClick={handleSubmit}
            disabled={selectedGenres.length < 2 || saving}
          >
            {saving ? 'Saving...' : 'Continue'}
          </button>
          <p className="skip-text">
            You can change these preferences later in your dashboard
          </p>
        </div>
      </div>
    </div>
  );
};

export default GenrePreference;
