import React, { useState, useEffect } from 'react';
import { Store, StoreFormData, District } from '../../types';
import './StoreForm.css';

interface StoreFormProps {
  store?: Store;
  onSubmit: (data: StoreFormData) => void;
  onCancel: () => void;
  districts?: District[];
  isLoading?: boolean;
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

  // Populate form when editing existing store
  useEffect(() => {
    if (store) {
      setFormData({
        name: store.name || '',
        address: store.address || '',
        phone: store.phone || '',
        email: store.email || '',
        latitude: store.location?.latitude?.toString() || '',
        longitude: store.location?.longitude?.toString() || '',
        store_type: store.store_type || 'convenience',
        district: store.district || '',
        city: store.city || 'Ho Chi Minh City',
        opening_hours: store.opening_hours || '',
        is_active: store.is_active ?? true,
        rating: store.rating?.toString() || ''
      });
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

    // Email validation
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Phone validation (Vietnamese phone number format)
    if (formData.phone && !/^(\+84|84|0)[1-9][0-9]{8,9}$/.test(formData.phone.replace(/\s/g, ''))) {
      newErrors.phone = 'Please enter a valid Vietnamese phone number';
    }

    // Coordinate validation
    if (formData.latitude) {
      const lat = parseFloat(formData.latitude);
      if (isNaN(lat) || lat < -90 || lat > 90) {
        newErrors.latitude = 'Latitude must be between -90 and 90';
      }
    }

    if (formData.longitude) {
      const lng = parseFloat(formData.longitude);
      if (isNaN(lng) || lng < -180 || lng > 180) {
        newErrors.longitude = 'Longitude must be between -180 and 180';
      }
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
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="latitude">Latitude</label>
              <input
                type="number"
                id="latitude"
                name="latitude"
                value={formData.latitude}
                onChange={handleInputChange}
                className={errors.latitude ? 'error' : ''}
                placeholder="10.762622"
                step="any"
              />
              {errors.latitude && <span className="error-message">{errors.latitude}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="longitude">Longitude</label>
              <input
                type="number"
                id="longitude"
                name="longitude"
                value={formData.longitude}
                onChange={handleInputChange}
                className={errors.longitude ? 'error' : ''}
                placeholder="106.660172"
                step="any"
              />
              {errors.longitude && <span className="error-message">{errors.longitude}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="district">District</label>
              <select
                id="district"
                name="district"
                value={formData.district}
                onChange={handleInputChange}
              >
                <option value="">Select District</option>
                {Array.isArray(districts) && districts.map(district => (
                  <option key={district.id} value={district.name}>
                    {district.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="city">City</label>
              <input
                type="text"
                id="city"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                placeholder="Ho Chi Minh City"
              />
            </div>
          </div>
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