import React, { useState, useEffect } from 'react';
import { Store, District, StoreFormData, StoreSearchFilters, UserLocation } from '../types';
import { storeApi, districtApi, getAvailableItems } from '../services/api';
import StoreForm from '../components/Store/StoreForm';
import StoreInventoryModal from '../components/Store/StoreInventoryModal';
import './Stores.css';

const Stores: React.FC = () => {
  // State for stores data
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);

  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [itemsPerPage] = useState(6); // Show 6 stores per page

  // State for form modal
  const [showForm, setShowForm] = useState(false);
  const [editingStore, setEditingStore] = useState<Store | undefined>(undefined);
  const [formLoading, setFormLoading] = useState(false);

  // State for inventory modal
  const [showInventoryModal, setShowInventoryModal] = useState(false);
  const [selectedStoreForInventory, setSelectedStoreForInventory] = useState<Store | null>(null);

  // State for districts and inventory items
  const [districts, setDistricts] = useState<District[]>([]);
  const [availableItems, setAvailableItems] = useState<string[]>([]);

  // State for feedback messages
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [searchResultsMessage, setSearchResultsMessage] = useState('');

  // State for search filters
  const [searchFilters, setSearchFilters] = useState<StoreSearchFilters>({
    search: '',
    district: '',
    store_type: '',
    is_active: undefined,
    inventory_item: '',
    sort_by_nearby: false,
    page: 1,
    limit: 6
  });

  // State for location-based search and advanced filters
  const [userLocation, setUserLocation] = useState<UserLocation | null>(null);
  const [gettingLocation, setGettingLocation] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);



  // Load initial data
  useEffect(() => {
    loadStores(1);
    loadDistricts();
    loadAvailableItems();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps



  const loadStores = async (page: number = currentPage) => {
    setLoading(true);
    try {
      const response = await storeApi.getStores({
        page: page,
        limit: itemsPerPage
      });
      if (response.success && response.data) {
        setStores(response.data.results || []);
        setTotalCount(response.data.count || 0);
        setTotalPages(Math.ceil((response.data.count || 0) / itemsPerPage));
        setCurrentPage(page);
      } else {
        setErrorMessage(response.message || 'Failed to load stores');
      }
    } catch (error) {
      setErrorMessage('Failed to load stores');
      console.error('Error loading stores:', error);
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async (page: number = 1) => {
    setLoading(true);
    try {
      let response;
      
      if (searchFilters.sort_by_nearby && userLocation) {
        // Location-based search with automatic sorting
        response = await storeApi.searchStores({
          ...searchFilters,
          latitude: userLocation.latitude,
          longitude: userLocation.longitude,
          sort_by_distance: true,
          page: page,
          limit: itemsPerPage
        });
      } else {
        // Regular search
        response = await storeApi.searchStores({
          ...searchFilters,
          page: page,
          limit: itemsPerPage
        });
      }

      if (response.success && response.data) {
        setStores(response.data.results || []);
        setTotalCount(response.data.count || 0);
        setTotalPages(Math.ceil((response.data.count || 0) / itemsPerPage));
        setCurrentPage(page);
        
        // Show search results toast when there are active filters
        if (searchFilters.search || searchFilters.district || searchFilters.store_type || searchFilters.is_active !== undefined || searchFilters.inventory_item || searchFilters.sort_by_nearby) {
          let searchMessage = `Search Results: Found ${response.data.count || 0} store${(response.data.count || 0) !== 1 ? 's' : ''}`;
          if (searchFilters.search) searchMessage += ` matching "${searchFilters.search}"`;
          if (searchFilters.sort_by_nearby && userLocation) searchMessage += ` sorted by distance`;
          if (searchFilters.district) searchMessage += ` in selected district`;
          if (searchFilters.store_type) searchMessage += ` (${searchFilters.store_type.replace('_', ' ')} stores only)`;
          if (searchFilters.is_active !== undefined) searchMessage += ` (${searchFilters.is_active ? 'Active' : 'Inactive'} only)`;
          if (searchFilters.inventory_item) searchMessage += ` with "${searchFilters.inventory_item}" in stock`;
          
          setSearchResultsMessage(searchMessage);
          // Clear search results message after 2 seconds
          setTimeout(() => setSearchResultsMessage(''), 2000);
        }
      } else {
        setErrorMessage(response.message || 'Search failed');
      }
    } catch (error) {
      setErrorMessage('Search failed');
      console.error('Error searching stores:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDistricts = async () => {
    try {
      const response = await districtApi.getDistricts();
      
      if (response.success && response.data) {
        // Extract districts from paginated response
        const districtsData = response.data.results;
        if (Array.isArray(districtsData)) {
          setDistricts(districtsData);
        } else {
          console.error('Districts data is not an array:', response.data);
          setDistricts([]);
        }
      } else {
        console.error('Failed to load districts:', response.message);
        setDistricts([]);
      }
    } catch (error) {
      console.error('Error loading districts:', error);
      setDistricts([]);
    }
  };

  const loadAvailableItems = async () => {
    try {
      const response = await getAvailableItems();
      
      if (response.success && response.data) {
        setAvailableItems(response.data.items || []);
      } else {
        console.error('Failed to load available items:', response.message);
        setAvailableItems([]);
      }
    } catch (error) {
      console.error('Error loading available items:', error);
      setAvailableItems([]);
    }
  };

  // Search handlers
  const handleSearchChange = (value: string) => {
    setSearchFilters(prev => ({ ...prev, search: value }));
  };

  const handleDistrictChange = (districtId: string) => {
    setSearchFilters(prev => ({ ...prev, district: districtId }));
  };

  const handleStatusChange = (status: string) => {
    let is_active: boolean | undefined;
    if (status === 'active') is_active = true;
    else if (status === 'inactive') is_active = false;
    else is_active = undefined;
    
    setSearchFilters(prev => ({ ...prev, is_active }));
  };

  const handleInventoryItemChange = (item: string) => {
    setSearchFilters(prev => ({ ...prev, inventory_item: item }));
  };

  const handleSortByNearbyChange = (sortByNearby: boolean) => {
    setSearchFilters(prev => ({ ...prev, sort_by_nearby: sortByNearby }));
    if (sortByNearby && !userLocation) {
      getCurrentLocation();
    }
  };

  // Location-based search handlers
  const getCurrentLocation = () => {
    setGettingLocation(true);
    
    if (!navigator.geolocation) {
      setErrorMessage('Geolocation is not supported by this browser');
      setGettingLocation(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
        setGettingLocation(false);
        setSuccessMessage('Location obtained successfully');
        // Clear success message after 2 seconds for location
        setTimeout(() => setSuccessMessage(''), 2000);
      },
      (error) => {
        let errorMsg = 'Failed to get location';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMsg = 'Location access denied. Please enable location services.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMsg = 'Location information unavailable.';
            break;
          case error.TIMEOUT:
            errorMsg = 'Location request timed out.';
            break;
        }
        setErrorMessage(errorMsg);
        setGettingLocation(false);
        // Clear error message after 2 seconds for location
        setTimeout(() => setErrorMessage(''), 2000);
        // If location fails, disable sort by nearby
        setSearchFilters(prev => ({ ...prev, sort_by_nearby: false }));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
      }
    );
  };



  const handleAddStore = () => {
    setEditingStore(undefined);
    setShowForm(true);
  };

  const handleEditStore = (store: Store) => {
    setEditingStore(store);
    setShowForm(true);
  };

  const handleViewInventory = (store: Store) => {
    setSelectedStoreForInventory(store);
    setShowInventoryModal(true);
  };

  const handleCloseInventoryModal = () => {
    setShowInventoryModal(false);
    setSelectedStoreForInventory(null);
  };

  const handleFormSubmit = async (formData: StoreFormData) => {
    setFormLoading(true);
    try {
      let response;
      if (editingStore) {
        response = await storeApi.updateStore(editingStore.id!, formData);
      } else {
        response = await storeApi.createStore(formData);
      }

      if (response.success) {
        setSuccessMessage(editingStore ? 'Store updated successfully!' : 'Store created successfully!');
        setShowForm(false);
        setEditingStore(undefined);
        
        // Reload with current search/filters
        if (searchFilters.search || searchFilters.district || searchFilters.store_type || searchFilters.is_active !== undefined || searchFilters.inventory_item || searchFilters.sort_by_nearby) {
          performSearch(currentPage);
        } else {
          loadStores(currentPage);
        }
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        setErrorMessage(response.message || 'Failed to save store');
      }
    } catch (error) {
      setErrorMessage('Failed to save store');
      console.error('Error saving store:', error);
    } finally {
      setFormLoading(false);
    }
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingStore(undefined);
  };

  const clearMessages = () => {
    setSuccessMessage('');
    setErrorMessage('');
    setSearchResultsMessage('');
  };

  // Pagination handlers
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      if (searchFilters.search || searchFilters.district || searchFilters.store_type || searchFilters.is_active !== undefined || searchFilters.inventory_item || searchFilters.sort_by_nearby) {
        performSearch(page);
      } else {
        loadStores(page);
      }
    }
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      handlePageChange(currentPage + 1);
    }
  };

  // Generate page numbers for pagination
  const getPageNumbers = () => {
    const pages = [];
    const maxPages = 5; // Show max 5 page numbers
    let startPage = Math.max(1, currentPage - Math.floor(maxPages / 2));
    let endPage = Math.min(totalPages, startPage + maxPages - 1);
    
    // Adjust start page if we're near the end
    if (endPage - startPage + 1 < maxPages) {
      startPage = Math.max(1, endPage - maxPages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  return (
    <div className="stores-page">
      {/* Success/Error/Search Results Messages */}
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
      {searchResultsMessage && (
        <div className="alert alert-info">
          {searchResultsMessage}
          <button className="alert-close" onClick={clearMessages}>×</button>
        </div>
      )}

      <div className="stores-header">
        <div className="stores-title">
          <h2>Store Management</h2>
          <p>Manage your convenience store locations and information</p>
        </div>
        <button className="add-store-btn" onClick={handleAddStore}>
          <span>➕</span>
          Add New Store
        </button>
      </div>

      <div className="stores-filters">
                  {/* Main Search Controls Row */}
          <div className="search-controls-row">
            <div className="search-box">
              <input
                type="text"
                placeholder="Search stores by name, address, or district..."
                className="search-input"
                value={searchFilters.search || ''}
                onChange={(e) => handleSearchChange(e.target.value)}
              />
              <button className="search-btn" onClick={() => performSearch(1)}>🔍</button>
            </div>

            <div className="main-controls">
              <button 
                className={`advanced-btn ${showAdvancedFilters ? 'active' : ''}`}
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              >
                ⚙️ Advanced
              </button>
            </div>
          </div>

                  {/* Advanced Filters */}
          {showAdvancedFilters && (
            <div className="advanced-filters">
              <div className="filter-row">
                <div className="filter-group">
                  <label htmlFor="district-filter">District:</label>
                  <select 
                    id="district-filter"
                    className="filter-select" 
                    value={searchFilters.district || ''}
                    onChange={(e) => handleDistrictChange(e.target.value)}
                  >
                    <option value="">All Districts</option>
                    {Array.isArray(districts) && districts.map(district => (
                      <option key={district.id} value={district.id}>
                        {district.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="filter-group">
                  <label htmlFor="status-filter">Status:</label>
                  <select 
                    id="status-filter"
                    className="filter-select"
                    value={searchFilters.is_active === true ? 'active' : searchFilters.is_active === false ? 'inactive' : ''}
                    onChange={(e) => handleStatusChange(e.target.value)}
                  >
                    <option value="">All Status</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
                <div className="filter-group">
                  <label htmlFor="store-type-filter">Store Type:</label>
                  <select
                    id="store-type-filter"
                    className="filter-select"
                    value={searchFilters.store_type || ''}
                    onChange={(e) => setSearchFilters(prev => ({ ...prev, store_type: e.target.value }))}
                  >
                    <option value="">All Store Types</option>
                    <option value="convenience">Convenience Store</option>
                    <option value="gas_station">Gas Station</option>
                    <option value="supermarket">Supermarket</option>
                    <option value="pharmacy">Pharmacy</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              <div className="filter-row">
                <div className="filter-group">
                  <label htmlFor="inventory-filter">Inventory Item:</label>
                  <select
                    id="inventory-filter"
                    className="filter-select"
                    value={searchFilters.inventory_item || ''}
                    onChange={(e) => handleInventoryItemChange(e.target.value)}
                  >
                    <option value="">All Items</option>
                    {availableItems.map(item => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="filter-group checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={searchFilters.sort_by_nearby || false}
                      onChange={(e) => handleSortByNearbyChange(e.target.checked)}
                      disabled={gettingLocation}
                    />
                    Sort by nearby {gettingLocation ? '(Getting location...)' : ''}
                  </label>
                </div>
              </div>
            </div>
          )}




      </div>



      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading stores...</p>
        </div>
      ) : (
        <div className="stores-grid">
          {stores.length > 0 ? (
            stores.map((store) => {
              // Calculate distance if we have user location and store location
              let distance = null;
              if (searchFilters.sort_by_nearby && userLocation && store.location) {
                const lat1 = userLocation.latitude;
                const lon1 = userLocation.longitude;
                const lat2 = store.location.latitude;
                const lon2 = store.location.longitude;
                
                // Haversine formula for distance calculation
                const R = 6371; // Earth's radius in kilometers
                const dLat = (lat2 - lat1) * Math.PI / 180;
                const dLon = (lon2 - lon1) * Math.PI / 180;
                const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                         Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                         Math.sin(dLon/2) * Math.sin(dLon/2);
                const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                distance = R * c;
              }

              return (
                <div 
                  key={store.id} 
                  className="store-card"
                >
                  <div className="store-header">
                    <h3>{store.name}</h3>
                    <span className={`store-status ${store.is_active ? 'active' : 'inactive'}`}>
                      {store.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="store-info">
                    <p><strong>Address:</strong> {store.address}</p>
                    {store.phone && <p><strong>Phone:</strong> {store.phone}</p>}
                    {store.email && <p><strong>Email:</strong> {store.email}</p>}
                    {store.district && <p><strong>District:</strong> {store.district}</p>}
                    {store.opening_hours && <p><strong>Hours:</strong> {store.opening_hours}</p>}
                    {store.rating && <p><strong>Rating:</strong> {store.rating}/5</p>}
                    {distance && (
                      <div className="store-distance">
                        📍 {distance.toFixed(1)} km away
                      </div>
                    )}
                  </div>
                  <div className="store-actions">
                    <button className="action-btn edit" onClick={() => handleEditStore(store)}>
                      ✏️ Edit
                    </button>
                    <button className="action-btn inventory" onClick={() => handleViewInventory(store)}>
                      📦 Inventory
                    </button>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="no-stores">
              {(searchFilters.search || searchFilters.district || searchFilters.store_type || searchFilters.is_active !== undefined || searchFilters.inventory_item || searchFilters.sort_by_nearby) ? (
                <div>
                  <p>🔍 No stores found matching your search criteria.</p>
                  <p>Try adjusting your filters to see more results.</p>
                </div>
              ) : (
                <p>No stores found. <button onClick={handleAddStore} className="link-btn">Add your first store</button></p>
              )}
            </div>
          )}
        </div>
      )}

      {totalPages > 1 && (
        <div className="stores-pagination">
          <button 
            className="pagination-btn" 
            onClick={handlePreviousPage}
            disabled={currentPage === 1}
          >
            ← Previous
          </button>
          <div className="pagination-numbers">
            {currentPage > 3 && (
              <>
                <button className="page-number" onClick={() => handlePageChange(1)}>
                  1
                </button>
                {currentPage > 4 && <span className="pagination-ellipsis">...</span>}
              </>
            )}
            {getPageNumbers().map(page => (
              <button
                key={page}
                className={`page-number ${page === currentPage ? 'active' : ''}`}
                onClick={() => handlePageChange(page)}
              >
                {page}
              </button>
            ))}
            {currentPage < totalPages - 2 && (
              <>
                {currentPage < totalPages - 3 && <span className="pagination-ellipsis">...</span>}
                <button className="page-number" onClick={() => handlePageChange(totalPages)}>
                  {totalPages}
                </button>
              </>
            )}
          </div>
          <button 
            className="pagination-btn" 
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
          >
            Next →
          </button>
        </div>
      )}

      {/* Pagination Info */}
      {totalCount > 0 && (
        <div className="pagination-info">
          Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, totalCount)} of {totalCount} stores
        </div>
      )}

      {/* Store Form Modal */}
      {showForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <StoreForm
              store={editingStore}
              onSubmit={handleFormSubmit}
              onCancel={handleFormCancel}
              districts={districts}
              isLoading={formLoading}
            />
          </div>
        </div>
      )}

      {/* Store Inventory Modal */}
      {showInventoryModal && selectedStoreForInventory && (
        <StoreInventoryModal
          store={selectedStoreForInventory}
          onClose={handleCloseInventoryModal}
        />
      )}
    </div>
  );
};

export default Stores; 