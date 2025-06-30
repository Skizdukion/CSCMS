import React, { useState, useEffect } from 'react';
import { Store, Item, Inventory } from '../../types';
import { storeApi, itemApi } from '../../services/api';
import SearchableSelect from './SearchableSelect';
import './InventoryForm.css';

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

interface InventoryFormProps {
  initialData?: Inventory;
  onSubmit: (formData: InventoryFormData) => void;
  onCancel: () => void;
  isEdit?: boolean;
}

interface InventoryFormData {
  store_id: number;
  item_id: number;
  is_available: boolean;
}

interface FormState {
  store_id: number | null;
  item_id: number | null;
  is_available: boolean;
}

const InventoryForm: React.FC<InventoryFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
  isEdit = false
}) => {
  const [formData, setFormData] = useState<FormState>({
    store_id: initialData?.store || null,
    item_id: initialData?.item || null,
    is_available: initialData?.is_available ?? true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [stores, setStores] = useState<Store[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [loadingStores, setLoadingStores] = useState(false);
  const [loadingItems, setLoadingItems] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Load initial data for dropdowns (just a small set for initial display)
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Load just the first few stores and items for initial display
        const [storesResponse, itemsResponse] = await Promise.all([
          storeApi.getStores({ limit: 50 }),
          itemApi.getItems({ limit: 50 })
        ]);

        if (storesResponse.success && storesResponse.data) {
          setStores(storesResponse.data.results || []);
        }

        if (itemsResponse.success && itemsResponse.data) {
          setItems(itemsResponse.data.results || []);
        }
      } catch (error) {
        console.error('Error loading initial data:', error);
      }
    };

    loadInitialData();
  }, []);

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

  const handleStoreSearch = async (searchTerm: string) => {
    if (searchTerm.length < 2) return;
    
    setLoadingStores(true);
    try {
      const response = await storeApi.getStores({ 
        search: searchTerm, 
        limit: 100 
      });
      
      if (response.success && response.data) {
        setStores(response.data.results || []);
      }
    } catch (error) {
      console.error('Error searching stores:', error);
    } finally {
      setLoadingStores(false);
    }
  };

  const handleItemSearch = async (searchTerm: string) => {
    if (searchTerm.length < 2) return;
    
    setLoadingItems(true);
    try {
      const response = await itemApi.searchItems({ 
        name: searchTerm, 
        limit: 100 
      });
      
      if (response.success && response.data) {
        setItems(response.data.results || []);
      }
    } catch (error) {
      console.error('Error searching items:', error);
    } finally {
      setLoadingItems(false);
    }
  };

  const handleStoreSelect = (store: Store | null) => {
    setFormData(prev => ({
      ...prev,
      store_id: store?.id || null
    }));
    
    // Clear error
    if (errors.store_id) {
      setErrors(prev => ({
        ...prev,
        store_id: ''
      }));
    }
  };

  const handleItemSelect = (item: Item | null) => {
    setFormData(prev => ({
      ...prev,
      item_id: item?.id || null
    }));
    
    // Clear error
    if (errors.item_id) {
      setErrors(prev => ({
        ...prev,
        item_id: ''
      }));
    }
  };



  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Required fields validation
    if (!formData.store_id) {
      newErrors.store_id = 'Store selection is required';
    }

    if (!formData.item_id) {
      newErrors.item_id = 'Item selection is required';
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
        store_id: formData.store_id!,
        item_id: formData.item_id!,
        is_available: formData.is_available,
      };
      
      await onSubmit(submitData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="inventory-form-overlay">
      <div className="inventory-form-container">
        <div className="inventory-form-header">
          <h3>{isEdit ? 'Edit Item' : 'Add New Item'}</h3>
          <button className="close-btn" onClick={onCancel} type="button">×</button>
        </div>

        <form onSubmit={handleSubmit} className="inventory-form">
          <div className="form-section">
            <SearchableSelect
              options={stores.filter(store => store.id !== undefined).map(store => ({
                id: store.id!,
                name: store.name,
                subtitle: store.address,
                                      description: `${formatStoreTypeName(store.store_type)} • ${store.city}`
              }))}
              selectedId={formData.store_id}
              onSelect={(option) => handleStoreSelect(option ? stores.find(s => s.id === option.id) || null : null)}
              placeholder="Search for a store..."
              label="Store"
              required
              error={errors.store_id}
              disabled={isEdit}
              loading={loadingStores}
              onSearch={handleStoreSearch}
            />

            <SearchableSelect
              options={items.filter(item => item.id !== undefined).map(item => ({
                id: item.id!,
                name: item.name,
                subtitle: item.category,
                description: item.brand ? `Brand: ${item.brand}` : undefined
              }))}
              selectedId={formData.item_id}
              onSelect={(option) => handleItemSelect(option ? items.find(i => i.id === option.id) || null : null)}
              placeholder="Search for an item..."
              label="Item"
              required
              error={errors.item_id}
              disabled={isEdit}
              loading={loadingItems}
              onSearch={handleItemSearch}
            />



            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_available"
                  checked={formData.is_available}
                  onChange={handleInputChange}
                />
                <span className="checkbox-text">Item is available</span>
              </label>
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
              disabled={submitting || loadingStores}
            >
              {submitting ? 'Saving...' : (isEdit ? 'Update Item' : 'Add Item')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InventoryForm; 