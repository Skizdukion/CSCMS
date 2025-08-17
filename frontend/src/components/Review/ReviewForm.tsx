import React, { useState } from 'react';
import './ReviewForm.css';

interface ReviewFormData {
  rating: number;
  comment: string;
  guest_name?: string;
}

interface ReviewFormProps {
  storeId: number;
  storeName: string;
  onSubmit: (data: ReviewFormData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  initialData?: ReviewFormData;
  isEditing?: boolean;
}

const ReviewForm: React.FC<ReviewFormProps> = ({
  storeId,
  storeName,
  onSubmit,
  onCancel,
  isLoading = false,
  initialData,
  isEditing = false
}) => {
  const [formData, setFormData] = useState<ReviewFormData>({
    rating: initialData?.rating || 5,
    comment: initialData?.comment || '',
    guest_name: initialData?.guest_name || ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.rating < 1 || formData.rating > 5) {
      setError('Please select a rating between 1 and 5 stars');
      return;
    }

    if (formData.comment.trim().length > 1000) {
      setError('Comment cannot exceed 1000 characters');
      return;
    }

    setError('');
    try {
      await onSubmit(formData);
    } catch (error) {
      setError('Failed to submit review. Please try again.');
    }
  };

  const handleRatingChange = (rating: number) => {
    setFormData(prev => ({ ...prev, rating }));
    if (error) setError('');
  };

  const handleCommentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const comment = e.target.value;
    setFormData(prev => ({ ...prev, comment }));
    if (error) setError('');
  };

  const handleGuestNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const guest_name = e.target.value;
    setFormData(prev => ({ ...prev, guest_name }));
    if (error) setError('');
  };

  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <button
          key={i}
          type="button"
          className={`star-btn ${i <= formData.rating ? 'filled' : ''}`}
          onClick={() => handleRatingChange(i)}
          disabled={isLoading}
        >
          {i <= formData.rating ? '⭐' : '☆'}
        </button>
      );
    }
    return stars;
  };

  return (
    <div className="review-form-container">
      <div className="review-form-header">
        <h3>{isEditing ? 'Edit Review' : 'Write a Review'}</h3>
        <p>Review for: <strong>{storeName}</strong></p>
      </div>

      <form onSubmit={handleSubmit} className="review-form">
        <div className="form-group">
          <label>Rating:</label>
          <div className="rating-stars">
            {renderStars()}
            <span className="rating-text">
              {formData.rating} star{formData.rating !== 1 ? 's' : ''}
            </span>
          </div>
        </div>

        {/* Guest name field for anonymous users */}
        {!localStorage.getItem('access_token') && (
          <div className="form-group">
            <label htmlFor="guest_name">Your Name (optional):</label>
            <input
              type="text"
              id="guest_name"
              value={formData.guest_name}
              onChange={handleGuestNameChange}
              placeholder="Enter your name (optional)"
              maxLength={100}
              disabled={isLoading}
              className="guest-name-input"
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="comment">Comment (optional):</label>
          <textarea
            id="comment"
            value={formData.comment}
            onChange={handleCommentChange}
            placeholder="Share your experience with this store..."
            maxLength={1000}
            rows={4}
            disabled={isLoading}
            className="comment-textarea"
          />
          <div className="character-count">
            {formData.comment.length}/1000 characters
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="cancel-btn"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="submit-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Submitting...' : (isEditing ? 'Update Review' : 'Submit Review')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ReviewForm;
