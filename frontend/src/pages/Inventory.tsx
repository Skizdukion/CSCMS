import React from 'react';
import './Inventory.css';

const Inventory: React.FC = () => {
  return (
    <div className="inventory-page">
      <div className="inventory-header">
        <div className="inventory-title">
          <h2>Inventory Management</h2>
          <p>Track and manage inventory across all stores</p>
        </div>
        <button className="add-item-btn">
          <span>➕</span>
          Add New Item
        </button>
      </div>

      <div className="inventory-filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search items by name, category, or store..."
            className="search-input"
          />
          <button className="search-btn">🔍</button>
        </div>
        <div className="filter-controls">
          <select className="filter-select">
            <option value="">All Stores</option>
            <option value="store1">Store #1 - District 1</option>
            <option value="store2">Store #2 - District 2</option>
            <option value="store3">Store #3 - District 3</option>
          </select>
          <select className="filter-select">
            <option value="">All Categories</option>
            <option value="beverages">Beverages</option>
            <option value="snacks">Snacks</option>
            <option value="household">Household</option>
          </select>
          <select className="filter-select">
            <option value="">All Status</option>
            <option value="in-stock">In Stock</option>
            <option value="low-stock">Low Stock</option>
            <option value="out-of-stock">Out of Stock</option>
          </select>
        </div>
      </div>

      <div className="inventory-table-container">
        <table className="inventory-table">
          <thead>
            <tr>
              <th>Item Name</th>
              <th>Category</th>
              <th>Store</th>
              <th>Quantity</th>
              <th>Status</th>
              <th>Last Updated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Coca Cola 330ml</td>
              <td>Beverages</td>
              <td>Store #1 - District 1</td>
              <td>45</td>
              <td><span className="status in-stock">In Stock</span></td>
              <td>2024-01-15 14:30</td>
              <td>
                <div className="table-actions">
                  <button className="action-btn edit">✏️</button>
                  <button className="action-btn delete">🗑️</button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Pepsi 500ml</td>
              <td>Beverages</td>
              <td>Store #1 - District 1</td>
              <td>12</td>
              <td><span className="status low-stock">Low Stock</span></td>
              <td>2024-01-15 13:45</td>
              <td>
                <div className="table-actions">
                  <button className="action-btn edit">✏️</button>
                  <button className="action-btn delete">🗑️</button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Lay's Chips</td>
              <td>Snacks</td>
              <td>Store #2 - District 2</td>
              <td>0</td>
              <td><span className="status out-of-stock">Out of Stock</span></td>
              <td>2024-01-15 12:20</td>
              <td>
                <div className="table-actions">
                  <button className="action-btn edit">✏️</button>
                  <button className="action-btn delete">🗑️</button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Toilet Paper</td>
              <td>Household</td>
              <td>Store #3 - District 3</td>
              <td>28</td>
              <td><span className="status in-stock">In Stock</span></td>
              <td>2024-01-15 11:15</td>
              <td>
                <div className="table-actions">
                  <button className="action-btn edit">✏️</button>
                  <button className="action-btn delete">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="inventory-summary">
        <div className="summary-card">
          <h3>Total Items</h3>
          <div className="summary-value">1,247</div>
        </div>
        <div className="summary-card">
          <h3>Low Stock Items</h3>
          <div className="summary-value warning">23</div>
        </div>
        <div className="summary-card">
          <h3>Out of Stock</h3>
          <div className="summary-value danger">8</div>
        </div>
        <div className="summary-card">
          <h3>Categories</h3>
          <div className="summary-value">12</div>
        </div>
      </div>
    </div>
  );
};

export default Inventory; 