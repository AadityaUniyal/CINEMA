import React, { useState } from 'react';
import axios from 'axios';

const MovieCard = ({ movie, userId, onUpdate }) => {
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

  const submitRatingAndComment = async () => {
    if (rating === 0 || isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      
      await axios.post('http:
        userId,
        movieId: movie.movieId,
        rating
      });

      if (comment.trim()) {
        await axios.post('http:
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
      const response = await axios.get(`http:
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
        await axios.delete(`http:
        setIsInWatchlist(false);
      } else {
        await axios.post(`http:
        setIsInWatchlist(true);
      }
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Failed to update watchlist:', error);
    } finally {
      setWatchlistLoading(false);
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
      </div>
    </div>
  );
};

export default MovieCard;
