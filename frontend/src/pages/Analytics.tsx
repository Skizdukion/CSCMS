import React, { useState, useEffect, useCallback } from 'react';
import { analyticsApi } from '../services/api';
import './Analytics.css';

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

interface AnalyticsData {
  totalStores: number;
  activeStores: number;
  inactiveStores: number;
  totalDistricts: number;
  totalInventoryItems: number;
  availableInventoryItems: number;
  unavailableInventoryItems: number;
  storesByDistrict: { [key: string]: number };
  storesByType: { [key: string]: number };
  averageStoresPerDistrict: number;
  topDistricts: Array<{ name: string; count: number }>;
  inventoryAvailabilityRate: number;
  topStoreTypes: Array<{ type: string; count: number; percentage: number }>;
  inventoryByCategory: { [key: string]: number };
  totalItems: number;
  averageInventoryPerStore: number;
}

const Analytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<'overview' | 'stores' | 'districts' | 'inventory'>('overview');

  const loadAnalyticsData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch analytics data from the dedicated API endpoint
      const response = await analyticsApi.getAnalytics();

      if (!response.success) {
        throw new Error(response.message || 'Failed to load analytics data');
      }

      setAnalyticsData(response.data);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while loading analytics data');
      console.error('Error loading analytics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnalyticsData();
  }, [loadAnalyticsData]);





  if (loading) {
    return (
      <div className="analytics-page">
        <div className="analytics-header">
          <h2>📊 Analytics Dashboard</h2>
          <p>Loading analytics data...</p>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-page">
        <div className="analytics-header">
          <h2>📊 Analytics Dashboard</h2>
          <p>System insights and statistics</p>
        </div>
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={loadAnalyticsData} className="retry-btn">
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="analytics-page">
        <div className="analytics-header">
          <h2>📊 Analytics Dashboard</h2>
          <p>No data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <div className="analytics-title">
          <h2>📊 Analytics Dashboard</h2>
          <p>Comprehensive insights about your convenience store chain</p>
        </div>
        <button onClick={loadAnalyticsData} className="refresh-btn">
          🔄 Refresh Data
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="analytics-nav">
        <button 
          className={`nav-tab ${selectedView === 'overview' ? 'active' : ''}`}
          onClick={() => setSelectedView('overview')}
        >
          📈 Overview
        </button>
        <button 
          className={`nav-tab ${selectedView === 'stores' ? 'active' : ''}`}
          onClick={() => setSelectedView('stores')}
        >
          🏪 Stores
        </button>
        <button 
          className={`nav-tab ${selectedView === 'districts' ? 'active' : ''}`}
          onClick={() => setSelectedView('districts')}
        >
          🗺️ Districts
        </button>
        <button 
          className={`nav-tab ${selectedView === 'inventory' ? 'active' : ''}`}
          onClick={() => setSelectedView('inventory')}
        >
          📦 Inventory
        </button>
      </div>

      {/* Overview Tab */}
      {selectedView === 'overview' && (
        <div className="analytics-content">
          <div className="stats-overview">
            <div className="stat-card primary">
              <div className="stat-icon">🏪</div>
              <div className="stat-content">
                <h3>{analyticsData.totalStores}</h3>
                <p>Total Stores</p>
                <span className="stat-detail">
                  {analyticsData.activeStores} active, {analyticsData.inactiveStores} inactive
                </span>
              </div>
            </div>

            <div className="stat-card success">
              <div className="stat-icon">🗺️</div>
              <div className="stat-content">
                <h3>{analyticsData.totalDistricts}</h3>
                <p>Districts Covered</p>
                <span className="stat-detail">
                  Avg. {analyticsData.averageStoresPerDistrict.toFixed(1)} stores/district
                </span>
              </div>
            </div>

            <div className="stat-card info">
              <div className="stat-icon">📦</div>
              <div className="stat-content">
                <h3>{analyticsData.totalInventoryItems}</h3>
                <p>Inventory Items</p>
                <span className="stat-detail">
                  {analyticsData.inventoryAvailabilityRate.toFixed(1)}% availability rate
                </span>
              </div>
            </div>

            <div className="stat-card warning">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <h3>{((analyticsData.activeStores / analyticsData.totalStores) * 100).toFixed(1)}%</h3>
                <p>Store Activity Rate</p>
                <span className="stat-detail">
                  {analyticsData.activeStores} of {analyticsData.totalStores} stores active
                </span>
              </div>
            </div>

            <div className="stat-card info">
              <div className="stat-icon">🛍️</div>
              <div className="stat-content">
                <h3>{analyticsData.totalItems}</h3>
                <p>Total Products</p>
                <span className="stat-detail">
                  Avg. {analyticsData.averageInventoryPerStore} items per store
                </span>
              </div>
            </div>
          </div>

          <div className="analytics-row">
            <div className="analytics-card">
              <h3>🏆 Top Districts by Store Count</h3>
              <div className="top-list">
                {analyticsData.topDistricts.map((district, index) => (
                  <div key={district.name} className="top-item">
                    <span className="rank">#{index + 1}</span>
                    <span className="name">{district.name}</span>
                    <span className="count">{district.count} stores</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="analytics-card">
              <h3>🏪 Store Brands Distribution</h3>
              <div className="distribution-list">
                {analyticsData.topStoreTypes.map(({ type, count, percentage }) => (
                  <div key={type} className="distribution-item">
                    <span className="type-name">
                      {formatStoreTypeName(type)}
                    </span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${percentage}%` 
                        }}
                      ></div>
                    </div>
                    <span className="count">{count} ({percentage}%)</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="analytics-card">
              <h3>📦 Inventory by Category</h3>
              <div className="distribution-list">
                {Object.entries(analyticsData.inventoryByCategory)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 8)
                  .map(([category, count]) => {
                    const percentage = (count / analyticsData.totalInventoryItems) * 100;
                    return (
                      <div key={category} className="distribution-item">
                        <span className="type-name">
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{ 
                              width: `${percentage}%` 
                            }}
                          ></div>
                        </div>
                        <span className="count">{count} ({percentage.toFixed(1)}%)</span>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stores Tab */}
      {selectedView === 'stores' && (
        <div className="analytics-content">
          <div className="analytics-section">
            <h3>🏪 Store Analytics</h3>
            <div className="stores-stats">
              <div className="stat-grid">
                <div className="stat-item">
                  <strong>Total Stores:</strong> {analyticsData.totalStores}
                </div>
                <div className="stat-item">
                  <strong>Active Stores:</strong> {analyticsData.activeStores}
                </div>
                <div className="stat-item">
                  <strong>Inactive Stores:</strong> {analyticsData.inactiveStores}
                </div>
                <div className="stat-item">
                  <strong>Activity Rate:</strong> {((analyticsData.activeStores / analyticsData.totalStores) * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="store-type-breakdown">
              <h4>Store Brand Breakdown</h4>
              <div className="type-grid">
                {analyticsData.topStoreTypes.map(({ type, count, percentage }) => (
                  <div key={type} className="type-card">
                    <h5>{formatStoreTypeName(type)}</h5>
                    <p className="type-count">{count}</p>
                    <p className="type-percentage">
                      {percentage}%
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="store-type-breakdown">
              <h4>Product Categories</h4>
              <div className="type-grid">
                {Object.entries(analyticsData.inventoryByCategory)
                  .sort(([,a], [,b]) => b - a)
                  .slice(0, 6)
                  .map(([category, count]) => {
                    const percentage = (count / analyticsData.totalInventoryItems) * 100;
                    return (
                      <div key={category} className="type-card">
                        <h5>{category.charAt(0).toUpperCase() + category.slice(1)}</h5>
                        <p className="type-count">{count}</p>
                        <p className="type-percentage">
                          {percentage.toFixed(1)}%
                        </p>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Districts Tab */}
      {selectedView === 'districts' && (
        <div className="analytics-content">
          <div className="analytics-section">
            <h3>🗺️ District Analytics</h3>
            <div className="districts-stats">
              <div className="stat-grid">
                <div className="stat-item">
                  <strong>Total Districts:</strong> {analyticsData.totalDistricts}
                </div>
                <div className="stat-item">
                  <strong>Average Stores per District:</strong> {analyticsData.averageStoresPerDistrict.toFixed(2)}
                </div>
                <div className="stat-item">
                  <strong>Most Stores in a District:</strong> {Math.max(...Object.values(analyticsData.storesByDistrict))}
                </div>
                <div className="stat-item">
                  <strong>Least Stores in a District:</strong> {Math.min(...Object.values(analyticsData.storesByDistrict))}
                </div>
              </div>
            </div>

            <div className="district-breakdown">
              <h4>Stores per District</h4>
              <div className="district-list">
                {Object.entries(analyticsData.storesByDistrict)
                  .sort(([,a], [,b]) => b - a)
                  .map(([district, count]) => (
                    <div key={district} className="district-item">
                      <span className="district-name">{district}</span>
                      <div className="district-bar">
                        <div 
                          className="district-fill" 
                          style={{ 
                            width: `${(count / Math.max(...Object.values(analyticsData.storesByDistrict))) * 100}%` 
                          }}
                        ></div>
                      </div>
                      <span className="district-count">{count} stores</span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Inventory Tab */}
      {selectedView === 'inventory' && (
        <div className="analytics-content">
          <div className="analytics-section">
            <h3>📦 Inventory Analytics</h3>
            <div className="inventory-stats">
              <div className="stat-grid">
                <div className="stat-item">
                  <strong>Total Inventory Items:</strong> {analyticsData.totalInventoryItems}
                </div>
                <div className="stat-item">
                  <strong>Available Items:</strong> {analyticsData.availableInventoryItems}
                </div>
                <div className="stat-item">
                  <strong>Unavailable Items:</strong> {analyticsData.unavailableInventoryItems}
                </div>
                <div className="stat-item">
                  <strong>Availability Rate:</strong> {analyticsData.inventoryAvailabilityRate.toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="inventory-health">
              <h4>Inventory Health</h4>
              <div className="health-indicator">
                <div className="health-bar">
                  <div 
                    className="health-fill"
                    style={{ 
                      width: `${analyticsData.inventoryAvailabilityRate}%`,
                      backgroundColor: analyticsData.inventoryAvailabilityRate > 80 ? '#4caf50' : 
                                     analyticsData.inventoryAvailabilityRate > 60 ? '#ff9800' : '#f44336'
                    }}
                  ></div>
                </div>
                <p className="health-description">
                  {analyticsData.inventoryAvailabilityRate > 80 ? '✅ Excellent' :
                   analyticsData.inventoryAvailabilityRate > 60 ? '⚠️ Good' : '❌ Needs Attention'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics; 