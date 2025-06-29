import React, { useState, useEffect, useCallback } from 'react';
import { itemApi } from '../services/api';
import { Item } from '../types';
import ItemForm from '../components/Items/ItemForm';
import './Items.css';

const ItemsPage: React.FC = () => {
  // State management
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  // Form states
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [deleteConfirmItem, setDeleteConfirmItem] = useState<Item | null>(null);

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
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
  ];

  // Load items data
  const loadItemsData = useCallback(async (page: number = 1, searchParams?: {
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
        params.search = currentSearchTerm.trim();
      }
      if (currentCategory) {
        params.category = currentCategory;
      }
      if (currentStatus === 'active') {
        params.is_active = true;
      } else if (currentStatus === 'inactive') {
        params.is_active = false;
      }

      const response = await itemApi.getItems(params);

      if (response.success && response.data) {
        setItems(response.data.results || []);
      } else {
        setError(response.message || 'Failed to load items data');
      }
    } catch (err) {
      setError('An error occurred while loading items data');
      console.error('Error loading items:', err);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, selectedCategory, selectedStatus]);

  // Initial data load
  useEffect(() => {
    loadItemsData(1);
  }, [loadItemsData]);

  // Handle search
  const handleSearch = () => {
    setCurrentPage(1);
    loadItemsData(1, {
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
      loadItemsData(1, {
        searchTerm,
        category: filterType === 'category' ? value : selectedCategory,
        status: filterType === 'status' ? value : selectedStatus,
      });
    }, 0);
  };

  // Form handlers
  const handleAddItem = () => {
    setEditingItem(null);
    setShowForm(true);
  };

  const handleEditItem = (item: Item) => {
    setEditingItem(item);
    setShowForm(true);
  };

  const handleDeleteClick = (item: Item) => {
    setDeleteConfirmItem(item);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmItem) return;

    try {
      const response = await itemApi.deleteItem(deleteConfirmItem.id!);
      
      if (response.success) {
        setSuccessMessage(`"${deleteConfirmItem.name}" has been deleted successfully`);
        setDeleteConfirmItem(null);
        // Reload data
        loadItemsData(currentPage);
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
        response = await itemApi.updateItem(editingItem.id!, formData);
      } else {
        response = await itemApi.createItem(formData);
      }

      if (response.success) {
        const action = editingItem ? 'updated' : 'created';
        setSuccessMessage(`"${formData.name}" has been ${action} successfully`);
        setShowForm(false);
        setEditingItem(null);
        loadItemsData(currentPage);
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setError(response.message || `Failed to ${editingItem ? 'update' : 'create'} item`);
      }
    } catch (err) {
      setError(`An error occurred while ${editingItem ? 'updating' : 'creating'} the item`);
      console.error('Error submitting form:', err);
    }
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingItem(null);
  };

  // Get status display
  const getStatusDisplay = (item: Item) => {
    if (item.is_active) {
      return { text: 'Active', className: 'active' };
    } else {
      return { text: 'Inactive', className: 'inactive' };
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="items-page">
      <div className="items-header">
        <div className="items-title">
          <h2>Items Management</h2>
          <p>Manage your product catalog</p>
        </div>
        <button className="add-item-btn" onClick={handleAddItem}>
          <span>➕</span>
          Add New Item
        </button>
      </div>

      <div className="items-filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search items by name or brand..."
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
          <button onClick={() => loadItemsData(currentPage)}>Try Again</button>
        </div>
      )}

      {successMessage && (
        <div className="success-message">
          <p>✅ {successMessage}</p>
        </div>
      )}

      <div className="items-table-container">
        {loading ? (
          <div className="loading-container">
            <p>Loading items data...</p>
          </div>
        ) : (
          <table className="items-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Brand</th>
                <th>Category</th>
                <th>Stores</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 ? (
                <tr>
                  <td colSpan={7} className="no-data">
                    No items found
                  </td>
                </tr>
              ) : (
                items.map((item) => {
                  const status = getStatusDisplay(item);
                  return (
                    <tr key={item.id}>
                      <td>
                        <div className="item-info">
                          <div className="item-name">{item.name}</div>
                          {item.description && (
                            <div className="item-description">{item.description}</div>
                          )}
                        </div>
                      </td>
                      <td>{item.brand || '-'}</td>
                      <td>{categories.find(c => c.value === item.category)?.label || item.category}</td>
                      <td>
                        <span className="store-count">
                          {item.store_count || 0} stores
                        </span>
                      </td>
                      <td>
                        <span className={`status ${status.className}`}>
                          {status.text}
                        </span>
                      </td>
                      <td>{item.updated_at ? formatDate(item.updated_at) : 'N/A'}</td>
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
        )}
      </div>

      {/* Item Form Modal */}
      {showForm && (
        <ItemForm
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
              Are you sure you want to delete <strong>"{deleteConfirmItem.name}"</strong>?
              <br />
              This will also remove it from all store inventories. This action cannot be undone.
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

export default ItemsPage; 