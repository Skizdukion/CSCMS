import React from 'react';
import './ReviewList.css';

interface Review {
  id: number;
  user?: number;
  user_name: string;
  rating: number;
  comment: string;
  created_at: string;
}

interface ReviewListProps {
  reviews: Review[];
  storeRating?: number;
  reviewCount: number;
  onWriteReview?: () => void;
  onEditReview?: (review: Review) => void;
  onDeleteReview?: (reviewId: number) => void;
  currentUserId?: number | null;
  isLoading?: boolean;
}

const ReviewList: React.FC<ReviewListProps> = ({
  reviews,
  storeRating,
  reviewCount,
  onWriteReview,
  onEditReview,
  onDeleteReview,
  currentUserId,
  isLoading = false
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const renderStars = (rating: number) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <span key={i} className={`star ${i <= rating ? 'filled' : ''}`}>
          {i <= rating ? '⭐' : '☆'}
        </span>
      );
    }
    return stars;
  };

  const renderOverallRating = () => {
    if (!storeRating || typeof storeRating !== 'number') {
      return (
        <div className="overall-rating">
          <div className="rating-stars">
            {renderStars(0)}
          </div>
          <span className="rating-text">No ratings yet</span>
        </div>
      );
    }

    return (
      <div className="overall-rating">
        <div className="rating-stars">
          {renderStars(Math.round(storeRating))}
        </div>
        <span className="rating-text">
          {storeRating.toFixed(1)} out of 5 ({reviewCount} review{reviewCount !== 1 ? 's' : ''})
        </span>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="review-list-container">
        <div className="loading-reviews">
          <div className="loading-spinner"></div>
          <p>Loading reviews...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="review-list-container">
      <div className="reviews-header">
        <div className="reviews-title">
          <h3>Customer Reviews</h3>
          {renderOverallRating()}
        </div>
        {onWriteReview && (
          <button className="write-review-btn" onClick={onWriteReview}>
            ✍️ Write a Review
          </button>
        )}
      </div>

      {reviews.length === 0 ? (
        <div className="no-reviews">
          <div className="no-reviews-icon">📝</div>
          <h4>No reviews yet</h4>
          <p>Be the first to share your experience with this store!</p>
          {onWriteReview && (
            <button className="write-first-review-btn" onClick={onWriteReview}>
              Write the First Review
            </button>
          )}
        </div>
      ) : (
        <div className="reviews-list">
          {reviews.map((review) => (
            <div key={review.id} className="review-item">
              <div className="review-header">
                <div className="reviewer-info">
                  <span className="reviewer-name">{review.user_name}</span>
                  <div className="review-rating">
                    {renderStars(review.rating)}
                  </div>
                </div>
                <div className="review-meta">
                  <span className="review-date">{formatDate(review.created_at)}</span>
                  {onEditReview && onDeleteReview && currentUserId && review.user === currentUserId && (
                    <div className="review-actions">
                      <button
                        className="edit-review-btn"
                        onClick={() => onEditReview(review)}
                        title="Edit review"
                      >
                        ✏️
                      </button>
                      <button
                        className="delete-review-btn"
                        onClick={() => onDeleteReview(review.id)}
                        title="Delete review"
                      >
                        🗑️
                      </button>
                    </div>
                  )}
                </div>
              </div>
              
              {review.comment && (
                <div className="review-comment">
                  <p>{review.comment}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReviewList;
