import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PreferenceSetup = ({ userId, onComplete }) => {
  const [genres, setGenres] = useState([]);
  const [tags, setTags] = useState([]);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchOptions();
  }, []);

  const fetchOptions = async () => {
    try {
      const [genresRes, tagsRes] = await Promise.all([
        axios.get('http:
        axios.get('http:
      ]);
      setGenres(genresRes.data.genres);
      setTags(tagsRes.data.tags);
    } catch (error) {
      console.error('Error fetching options:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleGenre = (genre) => {
    setSelectedGenres(prev =>
      prev.includes(genre)
        ? prev.filter(g => g !== genre)
        : [...prev, genre]
    );
  };

  const toggleTag = (tag) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const handleSubmit = async () => {
    if (selectedGenres.length === 0) {
      alert('Please select at least one genre');
      return;
    }

    setSaving(true);
    try {
      await axios.post('http:
        user_id: userId,
        preferred_genres: selectedGenres,
        favorite_tags: selectedTags
      });
      onComplete();
    } catch (error) {
      console.error('Error saving preferences:', error);
      alert('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading preferences</div>;
  }

  return (
    <div className="preference-setup">
      <div className="preference-container">
        <h1>Welcome! Let's personalize your experience</h1>
        <p className="subtitle">Select your favorite genres and interests</p>

        <div className="preference-section">
          <h2>Choose Your Favorite Genres</h2>
          <p className="hint">Select at least 3 genres you enjoy</p>
          <div className="options-grid">
            {genres.map(genre => (
              <div
                key={genre}
                className={`option-card ${selectedGenres.includes(genre) ? 'selected' : ''}`}
                onClick={() => toggleGenre(genre)}
              >
                {genre}
              </div>
            ))}
          </div>
        </div>

        <div className="preference-section">
          <h2>Select Your Interests (Optional)</h2>
          <p className="hint">Choose tags that match your taste</p>
          <div className="options-grid tags-grid">
            {tags.slice(0, 30).map(tag => (
              <div
                key={tag}
                className={`option-card tag-card ${selectedTags.includes(tag) ? 'selected' : ''}`}
                onClick={() => toggleTag(tag)}
              >
                {tag}
              </div>
            ))}
          </div>
        </div>

        <div className="preference-actions">
          <button
            onClick={handleSubmit}
            disabled={saving || selectedGenres.length === 0}
            className="save-preferences-btn"
          >
            {saving ? 'Saving...' : 'Continue'}
          </button>
          <p className="skip-text" onClick={() => onComplete()}>
            Skip for now
          </p>
        </div>
      </div>
    </div>
  );
};

export default PreferenceSetup;
