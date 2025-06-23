import React from 'react';
import './Stores.css';

const Stores: React.FC = () => {
  return (
    <div className="stores-page">
      <div className="stores-header">
        <div className="stores-title">
          <h2>Store Management</h2>
          <p>Manage your convenience store locations and information</p>
        </div>
        <button className="add-store-btn">
          <span>➕</span>
          Add New Store
        </button>
      </div>

      <div className="stores-filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search stores by name, address, or district..."
            className="search-input"
          />
          <button className="search-btn">🔍</button>
        </div>
        <div className="filter-controls">
          <select className="filter-select">
            <option value="">All Districts</option>
            <option value="district1">District 1</option>
            <option value="district2">District 2</option>
            <option value="district3">District 3</option>
          </select>
          <select className="filter-select">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <div className="stores-grid">
        <div className="store-card">
          <div className="store-header">
            <h3>Store #1 - District 1</h3>
            <span className="store-status active">Active</span>
          </div>
          <div className="store-info">
            <p><strong>Address:</strong> 123 Nguyen Hue Street, District 1, HCM City</p>
            <p><strong>Phone:</strong> +84 28 1234 5678</p>
            <p><strong>Manager:</strong> Nguyen Van A</p>
            <p><strong>Inventory Items:</strong> 45</p>
          </div>
          <div className="store-actions">
            <button className="action-btn edit">✏️ Edit</button>
            <button className="action-btn view">👁️ View</button>
            <button className="action-btn inventory">📦 Inventory</button>
          </div>
        </div>

        <div className="store-card">
          <div className="store-header">
            <h3>Store #2 - District 2</h3>
            <span className="store-status active">Active</span>
          </div>
          <div className="store-info">
            <p><strong>Address:</strong> 456 Thao Dien Street, District 2, HCM City</p>
            <p><strong>Phone:</strong> +84 28 2345 6789</p>
            <p><strong>Manager:</strong> Tran Thi B</p>
            <p><strong>Inventory Items:</strong> 38</p>
          </div>
          <div className="store-actions">
            <button className="action-btn edit">✏️ Edit</button>
            <button className="action-btn view">👁️ View</button>
            <button className="action-btn inventory">📦 Inventory</button>
          </div>
        </div>

        <div className="store-card">
          <div className="store-header">
            <h3>Store #3 - District 3</h3>
            <span className="store-status inactive">Inactive</span>
          </div>
          <div className="store-info">
            <p><strong>Address:</strong> 789 Vo Van Tan Street, District 3, HCM City</p>
            <p><strong>Phone:</strong> +84 28 3456 7890</p>
            <p><strong>Manager:</strong> Le Van C</p>
            <p><strong>Inventory Items:</strong> 0</p>
          </div>
          <div className="store-actions">
            <button className="action-btn edit">✏️ Edit</button>
            <button className="action-btn view">👁️ View</button>
            <button className="action-btn inventory">📦 Inventory</button>
          </div>
        </div>
      </div>

      <div className="stores-pagination">
        <button className="pagination-btn">← Previous</button>
        <div className="pagination-numbers">
          <span className="page-number active">1</span>
          <span className="page-number">2</span>
          <span className="page-number">3</span>
        </div>
        <button className="pagination-btn">Next →</button>
      </div>
    </div>
  );
};

export default Stores; 