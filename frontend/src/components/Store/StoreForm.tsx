import React, { useState, useEffect, useCallback } from 'react';
import { Store, StoreFormData, District } from '../../types';
import LocationPicker from '../Map/LocationPicker';
import './StoreForm.css';

interface StoreFormProps {
  store?: Store;
  onSubmit: (data: StoreFormData) => void;
  onCancel: () => void;
  districts?: District[];
  isLoading?: boolean;
}

interface LocationDetails {
  address: string;
  district: string;
  city: string;
  country: string;
}

const StoreForm: React.FC<StoreFormProps> = ({
  store,
  onSubmit,
  onCancel,
  districts = [],
  isLoading = false
}) => {
  const [formData, setFormData] = useState<StoreFormData>({
    name: '',
    address: '',
    phone: '',
    email: '',
    latitude: '',
    longitude: '',
    store_type: 'convenience',
    district: '',
    city: 'Ho Chi Minh City',
    opening_hours: '',
    is_active: true,
    rating: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [locationDetails, setLocationDetails] = useState<LocationDetails | null>(null);
  const [showLocationPicker, setShowLocationPicker] = useState(false);

  // Populate form when editing existing store
  useEffect(() => {
    if (store) {
      const lat = store.latitude || store.location?.latitude;
      const lng = store.longitude || store.location?.longitude;
      
      setFormData({
        name: store.name || '',
        address: store.address || '',
        phone: store.phone || '',
        email: store.email || '',
        latitude: lat?.toString() || '',
        longitude: lng?.toString() || '',
        store_type: store.store_type || 'convenience',
        district: store.district || '',
        city: store.city || 'Ho Chi Minh City',
        opening_hours: store.opening_hours || '',
        is_active: store.is_active ?? true,
        rating: store.rating?.toString() || ''
      });

      // Show location picker if we have coordinates
      if (lat && lng) {
        setShowLocationPicker(true);
      }
    }
  }, [store]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checkbox = e.target as HTMLInputElement;
      setFormData(prev => ({
        ...prev,
        [name]: checkbox.checked
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Required fields validation
    if (!formData.name.trim()) {
      newErrors.name = 'Store name is required';
    }

    if (!formData.address.trim()) {
      newErrors.address = 'Address is required';
    }

    // Coordinate validation - now required
    if (!formData.latitude) {
      newErrors.latitude = 'Latitude is required';
    } else {
      const lat = parseFloat(formData.latitude);
      if (isNaN(lat) || lat < -90 || lat > 90) {
        newErrors.latitude = 'Latitude must be between -90 and 90';
      }
    }

    if (!formData.longitude) {
      newErrors.longitude = 'Longitude is required';
    } else {
      const lng = parseFloat(formData.longitude);
      if (isNaN(lng) || lng < -180 || lng > 180) {
        newErrors.longitude = 'Longitude must be between -180 and 180';
      }
    }

    // Email validation
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Phone validation (Vietnamese phone number format)
    if (formData.phone && !/^(\+84|84|0)[1-9][0-9]{8,9}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'Please enter a valid Vietnamese phone number';
    }

    // Rating validation
    if (formData.rating) {
      const rating = parseFloat(formData.rating);
      if (isNaN(rating) || rating < 0 || rating > 5) {
        newErrors.rating = 'Rating must be between 0 and 5';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle location change from map picker
  const handleLocationChange = useCallback((lat: number, lng: number) => {
    setFormData(prev => ({
      ...prev,
      latitude: lat.toString(),
      longitude: lng.toString()
    }));

    // Clear location-related errors
    if (errors.latitude || errors.longitude) {
      setErrors(prev => ({
        ...prev,
        latitude: '',
        longitude: ''
      }));
    }
  }, [errors.latitude, errors.longitude]);

  // Handle location details from reverse geocoding
  const handleLocationDetails = useCallback((details: LocationDetails) => {
    setLocationDetails(details);
    
    // Auto-update district and address if available
    setFormData(prev => ({
      ...prev,
      district: details.district || prev.district,
      city: details.city || prev.city,
      // Only update address if it's empty to avoid overwriting user input
      address: prev.address || details.address
    }));
  }, []);

  // Toggle location picker visibility
  const handleToggleLocationPicker = useCallback(() => {
    setShowLocationPicker(prev => !prev);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const storeTypeOptions = [
    { value: 'convenience', label: 'Convenience Store' },
    { value: 'gas_station', label: 'Gas Station' },
    { value: 'supermarket', label: 'Supermarket' },
    { value: 'pharmacy', label: 'Pharmacy' },
    { value: 'other', label: 'Other' }
  ];

  return (
    <div className="store-form-container">
      <button className="close-btn" onClick={onCancel} type="button">×</button>

      <form onSubmit={handleSubmit} className="store-form">
        <div className="form-section">
          <h3>Basic Information</h3>
          
          <div className="form-group">
            <label htmlFor="name">Store Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className={errors.name ? 'error' : ''}
              placeholder="Enter store name"
            />
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="address">Address *</label>
            <textarea
              id="address"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              className={errors.address ? 'error' : ''}
              placeholder="Enter full address"
              rows={3}
            />
            {errors.address && <span className="error-message">{errors.address}</span>}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="phone">Phone Number</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                className={errors.phone ? 'error' : ''}
                placeholder="+84 XX XXXX XXXX"
              />
              {errors.phone && <span className="error-message">{errors.phone}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={errors.email ? 'error' : ''}
                placeholder="store@example.com"
              />
              {errors.email && <span className="error-message">{errors.email}</span>}
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Location Details</h3>
          
          <div className="location-picker-toggle">
            <button
              type="button"
              className={`btn-toggle-map ${showLocationPicker ? 'active' : ''}`}
              onClick={handleToggleLocationPicker}
            >
              {showLocationPicker ? '📍 Hide Map' : '🗺️ Pick Location on Map'}
            </button>
            <span className="toggle-hint">
              {showLocationPicker ? 'Click on map to set location' : 'Use map to pick precise coordinates'}
            </span>
          </div>

          {showLocationPicker && (
            <LocationPicker
              latitude={formData.latitude ? parseFloat(formData.latitude) : undefined}
              longitude={formData.longitude ? parseFloat(formData.longitude) : undefined}
              onLocationChange={handleLocationChange}
              onLocationDetails={handleLocationDetails}
              height="350px"
              zoom={15}
            />
          )}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="latitude">Latitude *</label>
              <input
                type="number"
                id="latitude"
                name="latitude"
                value={formData.latitude}
                onChange={handleInputChange}
                className={errors.latitude ? 'error' : ''}
                placeholder="10.762622"
                step="any"
                required
              />
              {errors.latitude && <span className="error-message">{errors.latitude}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="longitude">Longitude *</label>
              <input
                type="number"
                id="longitude"
                name="longitude"
                value={formData.longitude}
                onChange={handleInputChange}
                className={errors.longitude ? 'error' : ''}
                placeholder="106.660172"
                step="any"
                required
              />
              {errors.longitude && <span className="error-message">{errors.longitude}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="district">District {locationDetails && <span className="auto-detected">(Auto-detected)</span>}</label>
              <input
                type="text"
                id="district"
                name="district"
                value={formData.district}
                placeholder="Will be auto-detected from coordinates"
                className={locationDetails ? 'auto-filled' : ''}
                readOnly
              />
            </div>

            <div className="form-group">
              <label htmlFor="city">City</label>
              <input
                type="text"
                id="city"
                name="city"
                value={formData.city}
                placeholder="Ho Chi Minh City"
                readOnly
              />
            </div>
          </div>

          {locationDetails && (
            <div className="location-details">
              <h4>📍 Detected Location Information</h4>
              <div className="location-info">
                <div className="info-item">
                  <span className="info-label">Address:</span>
                  <span className="info-value">{locationDetails.address}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">District:</span>
                  <span className="info-value">{locationDetails.district || 'Not detected'}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">City:</span>
                  <span className="info-value">{locationDetails.city}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="form-section">
          <h3>Store Details</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="store_type">Store Type</label>
              <select
                id="store_type"
                name="store_type"
                value={formData.store_type}
                onChange={handleInputChange}
              >
                {storeTypeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="rating">Rating (0-5)</label>
              <input
                type="number"
                id="rating"
                name="rating"
                value={formData.rating}
                onChange={handleInputChange}
                className={errors.rating ? 'error' : ''}
                placeholder="4.5"
                min="0"
                max="5"
                step="0.1"
              />
              {errors.rating && <span className="error-message">{errors.rating}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="opening_hours">Opening Hours</label>
            <input
              type="text"
              id="opening_hours"
              name="opening_hours"
              value={formData.opening_hours}
              onChange={handleInputChange}
              placeholder="8:00 - 22:00"
            />
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
              />
              <span className="checkbox-text">Store is active</span>
            </label>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={isLoading}>
            {isLoading ? 'Saving...' : (store ? 'Update Store' : 'Create Store')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default StoreForm; 