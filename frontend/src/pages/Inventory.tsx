import React, { useState, useEffect, useCallback } from 'react';
import { inventoryApi } from '../services/api';
import { Inventory as InventoryItem } from '../types';
import InventoryForm from '../components/Inventory/InventoryForm';
import './Inventory.css';

const InventoryPage: React.FC = () => {
  // State management
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  // Form states
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [deleteConfirmItem, setDeleteConfirmItem] = useState<InventoryItem | null>(null);

  // Category and status options
  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'beverages', label: 'Beverages' },
    { value: 'snacks', label: 'Snacks' },
    { value: 'dairy', label: 'Dairy' },
    { value: 'frozen', label: 'Frozen Foods' },
    { value: 'household', label: 'Household' },
    { value: 'personal_care', label: 'Personal Care' },
    { value: 'other', label: 'Other' },
  ];

  const statusOptions = [
    { value: '', label: 'All Status' },
    { value: 'available', label: 'Available' },
    { value: 'unavailable', label: 'Unavailable' },
  ];



  // Load inventory data
  const loadInventoryData = useCallback(async (page: number = 1, searchParams?: {
    searchTerm?: string;
    category?: string;
    status?: string;
  }) => {
    setLoading(true);
    setError(null);
    
    try {
      const params: any = {
        page,
        limit: 20,
      };

      // Use provided search parameters or current state
      const currentSearchTerm = searchParams?.searchTerm ?? searchTerm;
      const currentCategory = searchParams?.category ?? selectedCategory;
      const currentStatus = searchParams?.status ?? selectedStatus;

      // Add filters if they exist
      if (currentSearchTerm.trim()) {
        params.item_name = currentSearchTerm.trim();
      }
      if (currentCategory) {
        params.category = currentCategory;
      }
      if (currentStatus === 'available') {
        params.available_only = true;
      }

      // Use search endpoint if there are filters, otherwise use general endpoint
      const hasFilters = currentSearchTerm.trim() || currentCategory || currentStatus;
      const response = hasFilters 
        ? await inventoryApi.searchInventory(params)
        : await inventoryApi.getInventory(params);

      if (response.success) {
        let filteredItems = response.data.results;

        // Apply client-side filtering for unavailable status
        if (currentStatus === 'unavailable') {
          filteredItems = filteredItems.filter(item => !item.is_available);
        }

        setInventoryItems(filteredItems);
        setTotalCount(response.data.count);
        setHasNext(!!response.data.next);
        setHasPrevious(!!response.data.previous);
      } else {
        setError(response.message || 'Failed to load inventory data');
      }
    } catch (err) {
      setError('An error occurred while loading inventory data');
      console.error('Error loading inventory:', err);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, selectedCategory, selectedStatus]);

  // Initial data load
  useEffect(() => {
    loadInventoryData(1);
  }, [loadInventoryData]);

  // Handle search
  const handleSearch = () => {
    setCurrentPage(1);
    loadInventoryData(1, {
      searchTerm,
      category: selectedCategory,
      status: selectedStatus,
    });
  };

  // Handle filter changes
  const handleFilterChange = (filterType: string, value: string) => {
    switch (filterType) {
      case 'category':
        setSelectedCategory(value);
        break;
      case 'status':
        setSelectedStatus(value);
        break;
    }
    setCurrentPage(1);
    // Trigger search immediately when filters change
    setTimeout(() => {
      loadInventoryData(1, {
        searchTerm,
        category: filterType === 'category' ? value : selectedCategory,
        status: filterType === 'status' ? value : selectedStatus,
      });
    }, 0);
  };

  // Handle pagination
  const handlePreviousPage = () => {
    if (hasPrevious && currentPage > 1) {
      const newPage = currentPage - 1;
      setCurrentPage(newPage);
      loadInventoryData(newPage, {
        searchTerm,
        category: selectedCategory,
        status: selectedStatus,
      });
    }
  };

  const handleNextPage = () => {
    if (hasNext) {
      const newPage = currentPage + 1;
      setCurrentPage(newPage);
      loadInventoryData(newPage, {
        searchTerm,
        category: selectedCategory,
        status: selectedStatus,
      });
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

  // Format date


  // Form handlers
  const handleAddItem = () => {
    setEditingItem(null);
    setShowForm(true);
  };

  const handleEditItem = (item: InventoryItem) => {
    setEditingItem(item);
    setShowForm(true);
  };

  const handleDeleteClick = (item: InventoryItem) => {
    setDeleteConfirmItem(item);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmItem) return;

    try {
      const response = await inventoryApi.deleteInventoryItem(deleteConfirmItem.id!);
      
      if (response.success) {
        setSuccessMessage(`"${deleteConfirmItem.item_name}" has been deleted successfully`);
        setDeleteConfirmItem(null);
        // Reload data
        loadInventoryData(currentPage, {
          searchTerm,
          category: selectedCategory,
          status: selectedStatus,
        });
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setError(response.message || 'Failed to delete item');
      }
    } catch (err) {
      setError('An error occurred while deleting the item');
      console.error('Error deleting item:', err);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmItem(null);
  };

  const handleFormSubmit = async (formData: any) => {
    try {
      let response;
      
      if (editingItem) {
        // Update existing item
        response = await inventoryApi.updateInventoryItem(editingItem.id!, {
          store_id: formData.store_id,
          item_name: formData.item_name,
          category: formData.category,
          is_available: formData.is_available,
        });
      } else {
        // Create new item
        response = await inventoryApi.createInventoryItem({
          store_id: formData.store_id,
          item_name: formData.item_name,
          category: formData.category,
          is_available: formData.is_available,
        });
      }

      if (response.success) {
        const action = editingItem ? 'updated' : 'added';
        setSuccessMessage(`"${formData.item_name}" has been ${action} successfully`);
        setShowForm(false);
        setEditingItem(null);
        // Reload data
        loadInventoryData(currentPage, {
          searchTerm,
          category: selectedCategory,
          status: selectedStatus,
        });
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setError(response.message || `Failed to ${editingItem ? 'update' : 'add'} item`);
      }
    } catch (err) {
      setError(`An error occurred while ${editingItem ? 'updating' : 'adding'} the item`);
      console.error('Error submitting form:', err);
    }
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingItem(null);
  };

  // Calculate summary statistics
  const getSummaryStats = () => {
    const totalItems = inventoryItems.length;
    const availableItems = inventoryItems.filter(item => item.is_available).length;
    const unavailableItems = inventoryItems.filter(item => !item.is_available).length;
    const categoriesCount = new Set(inventoryItems.map(item => item.item_category)).size;

    return {
      totalItems,
      availableItems,
      unavailableItems,
      categoriesCount,
    };
  };

  const stats = getSummaryStats();

  return (
    <div className="inventory-page">
      <div className="inventory-header">
        <div className="inventory-title">
          <h2>Inventory Management</h2>
          <p>Track and manage inventory across all stores</p>
        </div>
        <button className="add-item-btn" onClick={handleAddItem}>
          <span>➕</span>
          Add New Item
        </button>
      </div>

      <div className="inventory-filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search items by name..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button className="search-btn" onClick={handleSearch}>
            🔍
          </button>
        </div>
        <div className="filter-controls">
          <select 
            className="filter-select"
            value={selectedCategory}
            onChange={(e) => handleFilterChange('category', e.target.value)}
          >
            {categories.map(category => (
              <option key={category.value} value={category.value}>
                {category.label}
              </option>
            ))}
          </select>
          <select 
            className="filter-select"
            value={selectedStatus}
            onChange={(e) => handleFilterChange('status', e.target.value)}
          >
            {statusOptions.map(status => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={() => loadInventoryData(currentPage, {
            searchTerm,
            category: selectedCategory,
            status: selectedStatus,
          })}>Try Again</button>
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          <p>✅ {successMessage}</p>
        </div>
      )}

      <div className="inventory-table-container">
        {loading ? (
          <div className="loading-container">
            <p>Loading inventory data...</p>
          </div>
        ) : (
          <>
                         <table className="inventory-table">
               <thead>
                 <tr>
                   <th>Item Name</th>
                   <th>Category</th>
                   <th>Store</th>
                   <th>Status</th>
                   <th>Actions</th>
                 </tr>
               </thead>
               <tbody>
                 {inventoryItems.length === 0 ? (
                   <tr>
                     <td colSpan={5} className="no-data">
                       No inventory items found
                     </td>
                   </tr>
                 ) : (
                   inventoryItems.map((item) => {
                     const status = getStatusDisplay(item);
                     return (
                       <tr key={item.id}>
                         <td>{item.item_name}</td>
                         <td>{categories.find(c => c.value === item.item_category)?.label || item.item_category}</td>
                         <td>{item.store_name}</td>
                         <td>
                           <span className={`status ${status.className}`}>
                             {status.text}
                           </span>
                         </td>
                         <td>
                           <div className="table-actions">
                             <button 
                               className="action-btn edit" 
                               title="Edit"
                               onClick={() => handleEditItem(item)}
                             >
                               ✏️
                             </button>
                             <button 
                               className="action-btn delete" 
                               title="Delete"
                               onClick={() => handleDeleteClick(item)}
                             >
                               🗑️
                             </button>
                           </div>
                         </td>
                       </tr>
                     );
                   })
                 )}
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
          </>
        )}
      </div>

      <div className="inventory-summary">
        <div className="summary-card">
          <h3>Total Items</h3>
          <div className="summary-value">{totalCount}</div>
        </div>
        <div className="summary-card">
          <h3>Available</h3>
          <div className="summary-value">{stats.availableItems}</div>
        </div>
        <div className="summary-card">
          <h3>Unavailable</h3>
          <div className="summary-value danger">{stats.unavailableItems}</div>
        </div>
        <div className="summary-card">
          <h3>Categories</h3>
          <div className="summary-value">{stats.categoriesCount}</div>
        </div>
      </div>

      {/* Inventory Form Modal */}
      {showForm && (
        <InventoryForm
          initialData={editingItem || undefined}
          onSubmit={handleFormSubmit}
          onCancel={handleFormCancel}
          isEdit={!!editingItem}
        />
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmItem && (
        <div className="delete-confirmation-overlay">
          <div className="delete-confirmation-modal">
            <h3>Confirm Delete</h3>
            <p>
              Are you sure you want to delete <strong>"{deleteConfirmItem.item_name}"</strong>?
              <br />
              This action cannot be undone.
            </p>
            <div className="delete-confirmation-actions">
              <button 
                className="btn-cancel"
                onClick={handleDeleteCancel}
              >
                Cancel
              </button>
              <button 
                className="btn-delete"
                onClick={handleDeleteConfirm}
              >
                Delete Item
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryPage; 