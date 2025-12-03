import React, { useState } from 'react';
import axios from 'axios';
import API_BASE_URL from '../config';

const MovieCard = ({ movie, userId, onUpdate, showConfidence = false }) => {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [showRating, setShowRating] = useState(false);
  const [showComment, setShowComment] = useState(false);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showReviews, setShowReviews] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [watchlistLoading, setWatchlistLoading] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  const submitRatingAndComment = async () => {
    if (rating === 0 || isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      
      await axios.post(`${API_BASE_URL}/api/rate`, {
        userId,
        movieId: movie.movieId,
        rating
      });

      if (comment.trim()) {
        await axios.post(`${API_BASE_URL}/api/reviews`, {
          userId,
          movieId: movie.movieId,
          rating,
          comment: comment.trim()
        });
      }
      
      setShowRating(false);
      setShowComment(false);
      setRating(0);
      setComment('');
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Failed to submit:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const loadReviews = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/reviews/${movie.movieId}`);
      setReviews(response.data.reviews || []);
      setShowReviews(true);
    } catch (error) {
      console.error('Failed to load reviews:', error);
    }
  };

  const handleStarClick = (star) => {
    setRating(star);
  };

  const handleStarHover = (star) => {
    setHoverRating(star);
  };

  const handleStarLeave = () => {
    setHoverRating(0);
  };

  const toggleWatchlist = async () => {
    setWatchlistLoading(true);
    try {
      if (isInWatchlist) {
        await axios.delete(`${API_BASE_URL}/api/watchlist/${userId}/${movie.movieId}`);
        setIsInWatchlist(false);
      } else {
        await axios.post(`${API_BASE_URL}/api/watchlist/${userId}/${movie.movieId}`);
        setIsInWatchlist(true);
      }
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Failed to update watchlist:', error);
    } finally {
      setWatchlistLoading(false);
    }
  };

  const loadExplanation = async () => {
    if (explanation) {
      setShowExplanation(!showExplanation);
      return;
    }
    
    setLoadingExplanation(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/api/ml/explain/${userId}/${movie.movieId}`);
      setExplanation(response.data);
      setShowExplanation(true);
    } catch (error) {
      console.error('Failed to load explanation:', error);
      setExplanation({ error: 'Unable to load explanation' });
      setShowExplanation(true);
    } finally {
      setLoadingExplanation(false);
    }
  };

  return (
    <div className="movie-card">
      <div className="movie-card-inner">
        <div className="movie-poster">
          <div className="poster-placeholder">🎬</div>
        </div>
        
        <h3 className="movie-title">{movie.title}</h3>
        <p className="genres">{movie.genres}</p>
        
        <div className="movie-stats">
          <span className="rating-badge">⭐ {movie.avg_rating?.toFixed(1) || 'N/A'}</span>
          <span className="rating-count">{movie.rating_count || 0} ratings</span>
        </div>

        {showConfidence && movie.confidence && (
          <div className="confidence-score">
            <span className="confidence-label">Predicted for you:</span>
            <span className="confidence-value">⭐ {movie.confidence.toFixed(1)}</span>
          </div>
        )}

        <div className="movie-actions">
          <button 
            onClick={(e) => {
              e.stopPropagation();
              toggleWatchlist();
            }} 
            className={`action-btn watchlist-btn ${isInWatchlist ? 'in-watchlist' : ''}`}
            disabled={watchlistLoading}
            title={isInWatchlist ? 'Remove from Watchlist' : 'Add to Watchlist'}
          >
            {isInWatchlist ? '❤️' : '🤍'}
          </button>
          <button 
            onClick={(e) => {
              e.stopPropagation();
              setShowRating(!showRating);
              setShowComment(false);
            }} 
            className="action-btn rate-btn"
          >
            ⭐ Rate
          </button>
          <button 
            onClick={(e) => {
              e.stopPropagation();
              loadReviews();
            }} 
            className="action-btn review-btn"
          >
            💬 Reviews
          </button>
          {showConfidence && movie.mlBased && (
            <button 
              onClick={(e) => {
                e.stopPropagation();
                loadExplanation();
              }} 
              className="action-btn explain-btn"
              disabled={loadingExplanation}
            >
              {loadingExplanation ? '⏳' : '💡'} Why?
            </button>
          )}
        </div>

        {showRating && (
          <div className="rating-input">
            <div className="stars">
              {[1, 2, 3, 4, 5].map(star => (
                <span
                  key={star}
                  className={`star ${(hoverRating || rating) >= star ? 'filled' : ''}`}
                  onClick={() => handleStarClick(star)}
                  onMouseEnter={() => handleStarHover(star)}
                  onMouseLeave={handleStarLeave}
                >
                  ★
                </span>
              ))}
            </div>
            
            <button 
              onClick={() => setShowComment(!showComment)}
              className="comment-toggle"
            >
              {showComment ? '✕ Cancel Comment' : '💬 Add Comment'}
            </button>
            
            {showComment && (
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Write your review..."
                className="comment-input"
                rows="3"
              />
            )}
            
            <button 
              onClick={submitRatingAndComment} 
              disabled={rating === 0 || isSubmitting}
              className="submit-btn"
            >
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </button>
          </div>
        )}

        {showReviews && (
          <div className="reviews-section">
            <div className="reviews-header">
              <h4>Reviews ({reviews.length})</h4>
              <button onClick={() => setShowReviews(false)} className="close-btn">✕</button>
            </div>
            <div className="reviews-list">
              {reviews.length === 0 ? (
                <p className="no-reviews">No reviews yet. Be the first!</p>
              ) : (
                reviews.map((review, idx) => (
                  <div key={idx} className="review-item">
                    <div className="review-header">
                      <span className="review-user">
                        {review.userName ? review.userName.split(' ')[0] : `User ${review.userId}`}
                      </span>
                      <span className="review-rating">{'⭐'.repeat(review.rating)}</span>
                    </div>
                    {review.comment && <p className="review-comment">{review.comment}</p>}
                    <span className="review-date">
                      {new Date(review.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {showExplanation && explanation && (
          <div className="explanation-section">
            <div className="explanation-header">
              <h4>💡 Why Recommended</h4>
              <button onClick={() => setShowExplanation(false)} className="close-btn">✕</button>
            </div>
            {explanation.error ? (
              <p className="explanation-error">{explanation.error}</p>
            ) : (
              <div className="explanation-content">
                {explanation.reasons && explanation.reasons.length > 0 ? (
                  explanation.reasons.map((reason, idx) => (
                    <div key={idx} className="explanation-reason">
                      <h5 className="reason-title">
                        {reason.type === 'similar_movies' && '🎬 Similar Movies'}
                        {reason.type === 'genre_match' && '🎭 Genre Match'}
                        {reason.type === 'similar_users' && '👥 Similar Users'}
                      </h5>
                      <p className="reason-description">{reason.description}</p>
                      
                      {reason.type === 'similar_movies' && reason.movies && (
                        <div className="similar-movies-list">
                          {reason.movies.map((m, i) => (
                            <div key={i} className="similar-movie-item">
                              <span className="movie-name">{m.title}</span>
                              <span className="your-rating">Your rating: ⭐ {m.your_rating}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {reason.type === 'genre_match' && reason.genres && (
                        <div className="genre-list">
                          <span className="genres-text">{reason.genres.join(', ')}</span>
                          {reason.match_score && (
                            <span className="match-score">Match: {(reason.match_score * 100).toFixed(0)}%</span>
                          )}
                        </div>
                      )}
                      
                      {reason.type === 'similar_users' && (
                        <div className="similar-users-info">
                          <span>{reason.similar_user_count} users with similar taste</span>
                          {reason.avg_rating && (
                            <span className="avg-rating">Avg rating: ⭐ {reason.avg_rating.toFixed(1)}</span>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="no-explanation">No detailed explanation available</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MovieCard;
