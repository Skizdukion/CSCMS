import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Store } from '../../types';
import { reviewApi } from '../../services/api';
import ReviewForm from '../Review/ReviewForm';
import ReviewList from '../Review/ReviewList';
import 'leaflet/dist/leaflet.css';
import './StoreMapModal.css';
import L from 'leaflet';

// Helper function to format store type names for display
const formatStoreTypeName = (type: string): string => {
  const typeMap: { [key: string]: string } = {
    '7-eleven': '7-Eleven',
    'satrafoods': 'Satrafoods',
    'familymart': 'FamilyMart',
    'ministop': 'MINISTOP',
    'bach-hoa-xanh': 'Bách hóa XANH',
    'gs25': 'GS25',
    'circle-k': 'Circle K',
    'winmart': 'WinMart',
    'coopxtra': 'Co.opXtra',
    'other': 'Other',
    'unknown': 'Unknown'
  };
  
  return typeMap[type] || type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

// Fix for default markers in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface StoreMapModalProps {
  store: Store;
  onClose: () => void;
}

const StoreMapModal: React.FC<StoreMapModalProps> = ({ store, onClose }) => {
  // Review state
  const [reviews, setReviews] = useState<any[]>([]);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [showReviewList, setShowReviewList] = useState(false);
  const [editingReview, setEditingReview] = useState<any>(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [expandedComments, setExpandedComments] = useState<Set<number>>(new Set());

  // Load reviews when component mounts
  useEffect(() => {
    loadReviews();
  }, [store.id]);

  const loadReviews = async () => {
    setReviewLoading(true);
    try {
      const response = await reviewApi.getStoreReviews(store.id!);
      if (response.success && response.data) {
        setReviews(response.data.reviews || []);
      } else {
        setErrorMessage(response.message || 'Failed to load reviews');
      }
    } catch (error) {
      setErrorMessage('Failed to load reviews');
      console.error('Error loading reviews:', error);
    } finally {
      setReviewLoading(false);
    }
  };

  const handleWriteReview = () => {
    setEditingReview(null);
    setShowReviewForm(true);
  };

  const handleEditReview = (review: any) => {
    setEditingReview(review);
    setShowReviewForm(true);
  };

  const handleDeleteReview = async (reviewId: number) => {
    if (!window.confirm('Are you sure you want to delete this review?')) {
      return;
    }

    try {
      const response = await reviewApi.deleteReview(reviewId);
      if (response.success) {
        setSuccessMessage('Review deleted successfully!');
        loadReviews();
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setErrorMessage(response.message || 'Failed to delete review');
      }
    } catch (error) {
      setErrorMessage('Failed to delete review');
      console.error('Error deleting review:', error);
    }
  };

  const handleReviewSubmit = async (reviewData: { rating: number; comment: string; guest_name?: string }) => {
    try {
      let response;
      if (editingReview) {
        response = await reviewApi.updateReview(editingReview.id, reviewData);
      } else {
        response = await reviewApi.createReview({
          store: store.id!,
          ...reviewData
        });
      }

      if (response.success) {
        setSuccessMessage(editingReview ? 'Review updated successfully!' : 'Review submitted successfully!');
        setShowReviewForm(false);
        setEditingReview(null);
        loadReviews();
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setErrorMessage(response.message || 'Failed to submit review');
      }
    } catch (error) {
      setErrorMessage('Failed to submit review');
      console.error('Error submitting review:', error);
    }
  };

  const handleCloseReviewForm = () => {
    setShowReviewForm(false);
    setEditingReview(null);
  };

  const clearMessages = () => {
    setSuccessMessage('');
    setErrorMessage('');
  };

  const toggleCommentExpansion = (reviewId: number) => {
    setExpandedComments(prev => {
      const newSet = new Set(prev);
      if (newSet.has(reviewId)) {
        newSet.delete(reviewId);
      } else {
        newSet.add(reviewId);
      }
      return newSet;
    });
  };
  // Check if store has location data - use the separate latitude/longitude fields
  if (!store.latitude || !store.longitude) {
    return (
      <div className="store-map-modal-overlay">
        <div className="store-map-modal">
          <div className="store-map-modal-header">
            <h3>{store.name} - Location</h3>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          <div className="store-map-modal-content">
            <div className="no-location">
              <p>📍 No location data available for this store.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const position: [number, number] = [
    store.latitude,
    store.longitude
  ];

  return (
    <div className="store-map-modal-overlay">
      <div className="store-map-modal">
        <div className="store-map-modal-header">
          <h3>{store.name} - Location</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="store-map-modal-content">
          {/* Success/Error Messages */}
          {successMessage && (
            <div className="alert alert-success">
              {successMessage}
              <button className="alert-close" onClick={clearMessages}>×</button>
            </div>
          )}
          {errorMessage && (
            <div className="alert alert-error">
              {errorMessage}
              <button className="alert-close" onClick={clearMessages}>×</button>
            </div>
          )}

          <div className="store-info-summary">
            <p><strong>📍 Address:</strong> {store.address}</p>
            <p><strong>🏪 Brand:</strong> {formatStoreTypeName(store.store_type)}</p>
            {store.phone && <p><strong>📞 Phone:</strong> {store.phone}</p>}
            {store.opening_hours && <p><strong>🕐 Hours:</strong> {store.opening_hours}</p>}
            {store.rating && typeof store.rating === 'number' && <p><strong>⭐ Rating:</strong> {store.rating.toFixed(1)}/5 ({reviews.length} reviews)</p>}
          </div>

          <div className="map-container">
            <MapContainer
              center={position}
              zoom={16}
              style={{ height: '300px', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={position}>
                <Popup>
                  <div className="store-popup">
                    <h4>{store.name}</h4>
                    <p>{store.address}</p>
                    {store.phone && <p>📞 {store.phone}</p>}
                    <p className={`status ${store.is_active ? 'active' : 'inactive'}`}>
                      {store.is_active ? '✅ Active' : '❌ Inactive'}
                    </p>
                  </div>
                </Popup>
              </Marker>
            </MapContainer>
          </div>

          {/* Reviews Section */}
          <div className="reviews-section">
            <div className="reviews-header">
              <h4>Customer Reviews</h4>
              <button className="write-review-btn" onClick={handleWriteReview}>
                ✍️ Write Review
              </button>
            </div>
            
            {reviewLoading ? (
              <div className="loading-reviews">
                <div className="loading-spinner"></div>
                <p>Loading reviews...</p>
              </div>
            ) : reviews.length === 0 ? (
              <div className="no-reviews">
                <p>No reviews yet. Be the first to share your experience!</p>
              </div>
            ) : (
              <div className="reviews-preview">
                {reviews.slice(0, 3).map((review) => (
                  <div key={review.id} className="review-preview-item">
                    <div className="review-header">
                      <span className="reviewer-name">{review.user_name}</span>
                      <div className="review-rating">
                        {[...Array(5)].map((_, i) => (
                          <span key={i} className={`star ${i < review.rating ? 'filled' : ''}`}>
                            {i < review.rating ? '⭐' : '☆'}
                          </span>
                        ))}
                      </div>
                      {review.comment && (
                        <p className={`review-comment ${expandedComments.has(review.id) ? 'expanded' : ''}`}>
                          {review.comment}
                        </p>
                      )}
                      {review.comment && review.comment.length > 50 && (
                        <button
                          className="expand-comment-btn"
                          onClick={() => toggleCommentExpansion(review.id)}
                        >
                          {expandedComments.has(review.id) ? 'Less' : 'More'}
                        </button>
                      )}
                      <span className="review-date">{new Date(review.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
                {reviews.length > 3 && (
                  <button 
                    className="view-all-reviews-btn" 
                    onClick={() => setShowReviewList(true)}
                  >
                    View all {reviews.length} reviews
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Review Form Modal */}
      {showReviewForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <ReviewForm
              storeId={store.id!}
              storeName={store.name}
              onSubmit={handleReviewSubmit}
              onCancel={handleCloseReviewForm}
              isLoading={false}
              initialData={editingReview ? {
                rating: editingReview.rating,
                comment: editingReview.comment
              } : undefined}
              isEditing={!!editingReview}
            />
          </div>
        </div>
      )}

      {/* Review List Modal */}
      {showReviewList && (
        <div className="modal-overlay">
          <div className="modal-content">
            <ReviewList
              reviews={reviews}
              storeRating={store.rating}
              reviewCount={reviews.length}
              onWriteReview={handleWriteReview}
              onEditReview={handleEditReview}
              onDeleteReview={handleDeleteReview}
              currentUserId={null} // Anonymous users can't edit/delete
              isLoading={reviewLoading}
            />
            <div className="modal-actions">
              <button className="modal-close-btn" onClick={() => setShowReviewList(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoreMapModal; 