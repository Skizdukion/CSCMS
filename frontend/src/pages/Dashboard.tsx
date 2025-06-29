import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Store } from '../types';
import { storeApi } from '../services/api';
import StoreMap from '../components/Map/StoreMap';
import './Dashboard.css';

const StoreMapMemo = React.memo(StoreMap);

const Dashboard: React.FC = () => {
  const [stores, setStores] = useState<Store[]>([]);
  const [dashboardStats, setDashboardStats] = useState(() => ({
    totalStores: 0,
    activeStores: 0,
    totalInventory: 0,
    districts: 0
  }));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [locationMessage, setLocationMessage] = useState<string | null>(null);

  // Fetch stores and calculate dashboard stats
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch store locations only (optimized for map display)
        const storesResponse = await storeApi.getStoreLocations();
        
        if (storesResponse.success && storesResponse.data) {
          const storeData = storesResponse.data;
          setStores(storeData);

          // Calculate stats
          const activeStores = storeData.filter(store => store.is_active).length;
          const uniqueDistricts = new Set(storeData.map(store => store.district).filter(Boolean)).size;
          
          setDashboardStats({
            totalStores: storeData.length,
            activeStores: activeStores,
            totalInventory: storeData.length * 52, // Approximate items per store
            districts: uniqueDistricts
          });
        } else {
          setError(storesResponse.message || 'Failed to fetch stores');
        }
      } catch (err) {
        setError('Network error occurred');
        console.error('Dashboard data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLocationFound = useCallback((location: { lat: number; lng: number; accuracy: number }) => {
    setLocationMessage(`Location found! Accuracy: ±${Math.round(location.accuracy)}m`);
    // Clear message after 5 seconds
    setTimeout(() => setLocationMessage(null), 5000);
  }, []);

  const handleLocationError = useCallback((errorMessage: string) => {
    setLocationMessage(`Location error: ${errorMessage}`);
    // Clear message after 5 seconds
    setTimeout(() => setLocationMessage(null), 5000);
  }, []);

  const mapCenter = useMemo(() => [10.8231, 106.6297] as [number, number], []);

  const formattedStores = useMemo(() => {
    return stores
      .filter(store => store.latitude && store.longitude)
      .map(store => ({
        id: store.id!,
        name: store.name,
        address: store.address,
        latitude: store.latitude,
        longitude: store.longitude,
        district_name: store.district || 'Unknown District',
        store_type: store.store_type,
        is_active: store.is_active,
        phone: store.phone,
        email: store.email,
        rating: store.rating,
        opening_hours: store.opening_hours
      }));
  }, [stores]);

  if (loading) {
    return (
      <div className="dashboard">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="dashboard-error">
          <p>Error loading dashboard: {error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h3>Total Stores</h3>
            <span className="card-icon">🏪</span>
          </div>
          <div className="card-content">
            <div className="card-value">{dashboardStats.totalStores}</div>
            <div className="card-description">All convenience stores</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>Active Stores</h3>
            <span className="card-icon">🟢</span>
          </div>
          <div className="card-content">
            <div className="card-value">{dashboardStats.activeStores}</div>
            <div className="card-description">Currently operational</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>Estimated Inventory</h3>
            <span className="card-icon">📦</span>
          </div>
          <div className="card-content">
            <div className="card-value">{dashboardStats.totalInventory.toLocaleString()}</div>
            <div className="card-description">Approximate items across stores</div>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>Districts</h3>
            <span className="card-icon">🗺️</span>
          </div>
          <div className="card-content">
            <div className="card-value">{dashboardStats.districts}</div>
            <div className="card-description">Coverage areas</div>
          </div>
        </div>


      </div>

      <div className="dashboard-map-section">
        <div className="section">
          <h3>Store Locations ({stores.length} stores)</h3>
          <div className="map-container">
            <StoreMapMemo
              stores={formattedStores}
              height="500px"
              center={mapCenter}
              zoom={11}
              showLayerControl={true}
              showScaleControl={true}
              showAdvancedControls={true}
              onLocationFound={handleLocationFound}
              onLocationError={handleLocationError}
            />
            {locationMessage && (
              <div className={`location-message ${locationMessage.includes('error') ? 'error' : 'success'}`}>
                {locationMessage}
              </div>
            )}
          </div>
        </div>
      </div>


    </div>
  );
};

export default Dashboard; 