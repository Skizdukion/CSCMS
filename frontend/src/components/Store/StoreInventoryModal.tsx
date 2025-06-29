import React, { useState, useEffect, useCallback } from 'react';
import { inventoryApi } from '../../services/api';
import { Store, Inventory as InventoryItem } from '../../types';
import './StoreInventoryModal.css';

interface StoreInventoryModalProps {
  store: Store;
  onClose: () => void;
}

const StoreInventoryModal: React.FC<StoreInventoryModalProps> = ({ store, onClose }) => {
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);

  // Category options for display
  const categories = [
    { value: 'beverages', label: 'Beverages' },
    { value: 'snacks', label: 'Snacks' },
    { value: 'dairy', label: 'Dairy' },
    { value: 'frozen', label: 'Frozen Foods' },
    { value: 'household', label: 'Household' },
    { value: 'personal_care', label: 'Personal Care' },
    { value: 'other', label: 'Other' },
  ];

  // Load inventory for the store
  const loadStoreInventory = useCallback(async (page: number = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await inventoryApi.searchInventory({
        store_id: store.id,
        page,
        limit: 20,
      });

      if (response.success && response.data) {
        setInventoryItems(response.data.results || []);
        setTotalCount(response.data.count || 0);
        setHasNext(!!response.data.next);
        setHasPrevious(!!response.data.previous);
      } else {
        setError(response.message || 'Failed to load store inventory');
      }
    } catch (err) {
      setError('An error occurred while loading store inventory');
      console.error('Error loading store inventory:', err);
    } finally {
      setLoading(false);
    }
  }, [store.id]);

  // Initial load
  useEffect(() => {
    if (store.id) {
      loadStoreInventory(1);
    }
  }, [store.id, loadStoreInventory]);

  // Handle pagination
  const handlePreviousPage = () => {
    if (hasPrevious && currentPage > 1) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      loadStoreInventory(newPage);
    }
  };

  const handleNextPage = () => {
    if (hasNext) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      loadStoreInventory(newPage);
    }
  };

  // Get status display
  const getStatusDisplay = (item: InventoryItem) => {
    if (item.is_available) {
      return { text: 'Available', className: 'in-stock' };
    } else {
      return { text: 'Unavailable', className: 'out-of-stock' };
    }
  };

  // Get category display name
  const getCategoryDisplayName = (category: string) => {
    const categoryItem = categories.find(c => c.value === category);
    return categoryItem ? categoryItem.label : category;
  };

  // Handle click outside modal
  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="store-inventory-modal-overlay" onClick={handleOverlayClick}>
      <div className="store-inventory-modal-content">
        <div className="store-inventory-modal-header">
          <div className="store-inventory-modal-title">
            <h3>📦 Inventory for {store.name}</h3>
            <p>{store.address}</p>
          </div>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="store-inventory-modal-body">
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading inventory...</p>
            </div>
          ) : error ? (
            <div className="error-container">
              <p>❌ {error}</p>
              <button onClick={() => loadStoreInventory(currentPage)} className="retry-btn">
                Try Again
              </button>
            </div>
          ) : (
            <>
              <div className="inventory-summary">
                <div className="summary-item">
                  <span className="summary-label">Total Items:</span>
                  <span className="summary-value">{totalCount}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Available:</span>
                  <span className="summary-value available">
                    {inventoryItems.filter(item => item.is_available).length}
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Unavailable:</span>
                  <span className="summary-value unavailable">
                    {inventoryItems.filter(item => !item.is_available).length}
                  </span>
                </div>
              </div>

              {inventoryItems.length === 0 ? (
                <div className="no-inventory">
                  <p>📦 No inventory items found for this store.</p>
                </div>
              ) : (
                <div className="inventory-table-container">
                  <table className="inventory-table">
                    <thead>
                      <tr>
                        <th>Item Name</th>
                        <th>Category</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {inventoryItems.map((item) => {
                        const status = getStatusDisplay(item);
                        return (
                          <tr key={item.id}>
                            <td>
                              <div className="item-info">
                                <div className="item-name">{item.item_name}</div>
                              </div>
                            </td>
                            <td>{getCategoryDisplayName(item.item_category || 'other')}</td>
                            <td>
                              <span className={`status ${status.className}`}>
                                {status.text}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>

                  {/* Pagination */}
                  {(hasPrevious || hasNext) && (
                    <div className="pagination">
                      <button 
                        className="pagination-btn" 
                        onClick={handlePreviousPage}
                        disabled={!hasPrevious}
                      >
                        Previous
                      </button>
                      <span className="pagination-info">
                        Page {currentPage} • {totalCount} total items
                      </span>
                      <button 
                        className="pagination-btn"
                        onClick={handleNextPage}
                        disabled={!hasNext}
                      >
                        Next
                      </button>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default StoreInventoryModal; 