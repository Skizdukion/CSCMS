import React, { useState } from 'react';
import { Item } from '../../types';
import './ItemEditForm.css';

interface ItemEditFormProps {
  item?: Item;
  onSubmit: (formData: ItemFormData) => void;
  onCancel: () => void;
  isEdit?: boolean;
}

interface ItemFormData {
  name: string;
  is_active: boolean;
}

const ItemEditForm: React.FC<ItemEditFormProps> = ({
  item,
  onSubmit,
  onCancel,
  isEdit = false
}) => {
  const [formData, setFormData] = useState<ItemFormData>({
    name: item?.name || '',
    is_active: item?.is_active ?? true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

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

    if (!formData.name.trim()) {
      newErrors.name = 'Item name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Item name must be at least 2 characters';
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
      const submitData = {
        name: formData.name.trim(),
        is_active: formData.is_active,
      };
      
      await onSubmit(submitData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="item-edit-form-overlay">
      <div className="item-edit-form-container">
        <div className="item-edit-form-header">
          <h3>{isEdit ? 'Edit Item' : 'Add New Item'}</h3>
          <button className="close-btn" onClick={onCancel} type="button">×</button>
        </div>

        <form onSubmit={handleSubmit} className="item-edit-form">
          <div className="form-section">
            <div className="form-group">
              <label htmlFor="name">Item Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className={errors.name ? 'error' : ''}
                placeholder="Enter item name"
              />
              {errors.name && <span className="error-message">{errors.name}</span>}
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
              <small className="form-hint">
                Inactive items will not appear in new store selections
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
              {submitting ? 'Saving...' : (isEdit ? 'Update Item' : 'Add Item')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ItemEditForm; 