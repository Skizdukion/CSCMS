import React, { useState, useEffect } from 'react';
import { Store, Item } from '../../types';
import { storeApi } from '../../services/api';
import './ItemStoreForm.css';

interface ItemStoreFormProps {
  item: Item;
  onSubmit: (storeIds: number[]) => void;
  onCancel: () => void;
}

const ItemStoreForm: React.FC<ItemStoreFormProps> = ({
  item,
  onSubmit,
  onCancel,
}) => {
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedStoreIds, setSelectedStoreIds] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Load stores and current item-store relationships
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Load all stores
        const storesResponse = await storeApi.getStores({ limit: 1000 });
        if (storesResponse.success && storesResponse.data) {
          setStores(storesResponse.data.results || []);
        }

        // Load stores that currently have this item
        if (item.id) {
          const itemStoresResponse = await storeApi.searchStores({ 
            inventory_item: item.name,
            limit: 1000 
          });
          if (itemStoresResponse.success && itemStoresResponse.data) {
            const currentStoreIds = new Set(
              itemStoresResponse.data.results.map((store: Store) => store.id!).filter(Boolean)
            );
            setSelectedStoreIds(currentStoreIds);
          }
        }
      } catch (err) {
        setError('Failed to load stores data');
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [item.id, item.name]);

  const handleStoreToggle = (storeId: number) => {
    setSelectedStoreIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(storeId)) {
        newSet.delete(storeId);
      } else {
        newSet.add(storeId);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    const filteredStores = getFilteredStores();
    const allIds = new Set(filteredStores.map(store => store.id!).filter(Boolean));
    setSelectedStoreIds(allIds);
  };

  const handleDeselectAll = () => {
    setSelectedStoreIds(new Set());
  };

  const getFilteredStores = () => {
    if (!searchTerm.trim()) {
      return stores;
    }
    
    return stores.filter(store =>
      store.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      store.address.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      await onSubmit(Array.from(selectedStoreIds));
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredStores = getFilteredStores();
  const selectedCount = selectedStoreIds.size;

  return (
    <div className="item-store-form-overlay">
      <div className="item-store-form-container">
        <div className="item-store-form-header">
          <h3>Manage Stores for "{item.name}"</h3>
          <button className="close-btn" onClick={onCancel} type="button">×</button>
        </div>

        {loading && (
          <div className="loading-message">
            Loading stores...
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {!loading && !error && (
          <form onSubmit={handleSubmit} className="item-store-form">
            <div className="form-section">
              {/* Search section */}
              <div className="search-section">
                <div className="search-input-container">
                  <input
                    type="text"
                    placeholder="Search stores by name or address..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="search-input"
                  />
                </div>
                
                <div className="bulk-actions">
                  <button
                    type="button"
                    onClick={handleSelectAll}
                    className="btn-select-all"
                    disabled={filteredStores.length === 0}
                  >
                    Select All ({filteredStores.length})
                  </button>
                  <button
                    type="button"
                    onClick={handleDeselectAll}
                    className="btn-deselect-all"
                    disabled={selectedCount === 0}
                  >
                    Deselect All
                  </button>
                </div>

                <div className="selection-summary">
                  Selected: {selectedCount} of {stores.length} stores
                  {searchTerm && ` (showing ${filteredStores.length} filtered)`}
                </div>
              </div>

              {/* Stores list */}
              <div className="stores-list-container">
                {filteredStores.length === 0 ? (
                  <div className="no-stores-message">
                    {searchTerm ? 'No stores match your search' : 'No stores available'}
                  </div>
                ) : (
                  <div className="stores-list">
                    {filteredStores.map((store) => (
                      <div key={store.id} className="store-item">
                        <label className="store-checkbox-label">
                          <input
                            type="checkbox"
                            checked={selectedStoreIds.has(store.id!)}
                            onChange={() => handleStoreToggle(store.id!)}
                            className="store-checkbox"
                          />
                          <div className="store-info">
                            <div className="store-name">{store.name}</div>
                            <div className="store-address">{store.address}</div>
                            <div className="store-details">
                              {store.district && <span className="store-district">{store.district}</span>}
                              <span className="store-type">{store.store_type}</span>
                              {!store.is_active && <span className="store-inactive">Inactive</span>}
                            </div>
                          </div>
                        </label>
                      </div>
                    ))}
                  </div>
                )}
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
                {submitting ? 'Updating...' : `Update Stores (${selectedCount} selected)`}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ItemStoreForm; 