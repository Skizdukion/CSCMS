import React, { useState } from 'react';
import { Item } from '../../types';
import './ItemForm.css';

interface ItemFormProps {
  initialData?: Item;
  onSubmit: (formData: ItemFormData) => void;
  onCancel: () => void;
  isEdit?: boolean;
}

interface ItemFormData {
  name: string;
  description?: string;
  category: string;
  brand?: string;
  barcode?: string;
  is_active: boolean;
}

const ItemForm: React.FC<ItemFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  isEdit = false
}) => {
  const [formData, setFormData] = useState<ItemFormData>({
    name: initialData?.name || '',
    description: initialData?.description || '',
    category: initialData?.category || '',
    brand: initialData?.brand || '',
    barcode: initialData?.barcode || '',
    is_active: initialData?.is_active ?? true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  // Category options
  const categories = [
    { value: 'beverages', label: 'Beverages' },
    { value: 'snacks', label: 'Snacks' },
    { value: 'dairy', label: 'Dairy' },
    { value: 'frozen', label: 'Frozen Foods' },
    { value: 'household', label: 'Household' },
    { value: 'personal_care', label: 'Personal Care' },
    { value: 'other', label: 'Other' },
  ];



  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({
        ...prev,
        [name]: checked
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
      newErrors.name = 'Item name is required';
    }

    if (!formData.category) {
      newErrors.category = 'Category is required';
    }

    // Name length validation
    if (formData.name.length > 200) {
      newErrors.name = 'Item name must be less than 200 characters';
    }

    // Description length validation
    if (formData.description && formData.description.length > 500) {
      newErrors.description = 'Description must be less than 500 characters';
    }

    // Brand length validation
    if (formData.brand && formData.brand.length > 100) {
      newErrors.brand = 'Brand must be less than 100 characters';
    }

    // Barcode validation (if provided)
    if (formData.barcode && formData.barcode.trim()) {
      const barcodeRegex = /^[0-9]+$/;
      if (!barcodeRegex.test(formData.barcode.trim())) {
        newErrors.barcode = 'Barcode must contain only numbers';
      }
      if (formData.barcode.length < 8 || formData.barcode.length > 20) {
        newErrors.barcode = 'Barcode must be between 8 and 20 digits';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    
    try {
      // Clean up the data before submitting
      const submitData = {
        ...formData,
        name: formData.name.trim(),
        description: formData.description?.trim() || undefined,
        brand: formData.brand?.trim() || undefined,
        barcode: formData.barcode?.trim() || undefined,
      };
      
      await onSubmit(submitData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="item-form-overlay">
      <div className="item-form-container">
        <div className="item-form-header">
          <h3>{isEdit ? 'Edit Item' : 'Add New Item'}</h3>
          <button className="close-btn" onClick={onCancel} type="button">×</button>
        </div>

        <form onSubmit={handleSubmit} className="item-form">
          <div className="form-section">
            <div className="form-group">
              <label htmlFor="name">Item Name *</label>
              <input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter item name"
                className={errors.name ? 'error' : ''}
                maxLength={200}
              />
              {errors.name && <span className="error-message">{errors.name}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Enter item description (optional)"
                className={errors.description ? 'error' : ''}
                rows={3}
                maxLength={500}
              />
              {errors.description && <span className="error-message">{errors.description}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="category">Category *</label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className={errors.category ? 'error' : ''}
              >
                <option value="">Select a category</option>
                {categories.map(category => (
                  <option key={category.value} value={category.value}>
                    {category.label}
                  </option>
                ))}
              </select>
              {errors.category && <span className="error-message">{errors.category}</span>}
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="brand">Brand</label>
                <input
                  id="brand"
                  name="brand"
                  type="text"
                  value={formData.brand}
                  onChange={handleInputChange}
                  placeholder="Enter brand (optional)"
                  className={errors.brand ? 'error' : ''}
                  maxLength={100}
                />
                {errors.brand && <span className="error-message">{errors.brand}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="barcode">Barcode</label>
                <input
                  id="barcode"
                  name="barcode"
                  type="text"
                  value={formData.barcode}
                  onChange={handleInputChange}
                  placeholder="Enter barcode (optional)"
                  className={errors.barcode ? 'error' : ''}
                  maxLength={20}
                />
                {errors.barcode && <span className="error-message">{errors.barcode}</span>}
              </div>
            </div>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleInputChange}
                />
                <span className="checkbox-text">Item is active</span>
              </label>
              <small className="help-text">
                Inactive items will not be available for adding to store inventories
              </small>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn-cancel"
              onClick={onCancel}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-submit"
              disabled={submitting}
            >
              {submitting ? 'Saving...' : (isEdit ? 'Update Item' : 'Create Item')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ItemForm; 