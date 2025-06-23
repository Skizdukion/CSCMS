import React from 'react';
import './Reports.css';

const Reports: React.FC = () => {
  return (
    <div className="reports-page">
      <div className="reports-header">
        <div className="reports-title">
          <h2>Reports & Analytics</h2>
          <p>Comprehensive insights into store performance and inventory</p>
        </div>
        <div className="reports-actions">
          <button className="export-btn">
            <span>📊</span>
            Export Report
          </button>
          <button className="generate-btn">
            <span>🔄</span>
            Generate New
          </button>
        </div>
      </div>

      <div className="reports-filters">
        <div className="date-range">
          <label>Date Range:</label>
          <select className="filter-select">
            <option value="last7">Last 7 Days</option>
            <option value="last30">Last 30 Days</option>
            <option value="last90">Last 90 Days</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
        <div className="store-filter">
          <label>Store:</label>
          <select className="filter-select">
            <option value="all">All Stores</option>
            <option value="store1">Store #1 - District 1</option>
            <option value="store2">Store #2 - District 2</option>
            <option value="store3">Store #3 - District 3</option>
          </select>
        </div>
        <div className="report-type">
          <label>Report Type:</label>
          <select className="filter-select">
            <option value="performance">Performance Report</option>
            <option value="inventory">Inventory Report</option>
            <option value="sales">Sales Report</option>
            <option value="coverage">Coverage Analysis</option>
          </select>
        </div>
      </div>

      <div className="reports-grid">
        <div className="report-card large">
          <h3>Store Performance Overview</h3>
          <div className="chart-placeholder">
            <div className="chart-content">
              <span className="chart-icon">📈</span>
              <p>Performance Chart</p>
              <small>Store metrics and trends visualization</small>
            </div>
          </div>
        </div>

        <div className="report-card">
          <h3>Top Performing Stores</h3>
          <div className="ranking-list">
            <div className="ranking-item">
              <span className="rank">1</span>
              <div className="store-info">
                <div className="store-name">Store #1 - District 1</div>
                <div className="store-metric">Revenue: $12,450</div>
              </div>
            </div>
            <div className="ranking-item">
              <span className="rank">2</span>
              <div className="store-info">
                <div className="store-name">Store #2 - District 2</div>
                <div className="store-metric">Revenue: $11,230</div>
              </div>
            </div>
            <div className="ranking-item">
              <span className="rank">3</span>
              <div className="store-info">
                <div className="store-name">Store #3 - District 3</div>
                <div className="store-metric">Revenue: $9,870</div>
              </div>
            </div>
          </div>
        </div>

        <div className="report-card">
          <h3>Inventory Status</h3>
          <div className="status-chart">
            <div className="status-item">
              <div className="status-label">In Stock</div>
              <div className="status-bar">
                <div className="status-fill in-stock" style={{ width: '75%' }}></div>
              </div>
              <div className="status-value">75%</div>
            </div>
            <div className="status-item">
              <div className="status-label">Low Stock</div>
              <div className="status-bar">
                <div className="status-fill low-stock" style={{ width: '15%' }}></div>
              </div>
              <div className="status-value">15%</div>
            </div>
            <div className="status-item">
              <div className="status-label">Out of Stock</div>
              <div className="status-bar">
                <div className="status-fill out-of-stock" style={{ width: '10%' }}></div>
              </div>
              <div className="status-value">10%</div>
            </div>
          </div>
        </div>

        <div className="report-card">
          <h3>District Coverage</h3>
          <div className="coverage-list">
            <div className="coverage-item">
              <div className="district-name">District 1</div>
              <div className="coverage-stats">
                <span className="store-count">5 stores</span>
                <span className="coverage-percentage">95% coverage</span>
              </div>
            </div>
            <div className="coverage-item">
              <div className="district-name">District 2</div>
              <div className="coverage-stats">
                <span className="store-count">3 stores</span>
                <span className="coverage-percentage">80% coverage</span>
              </div>
            </div>
            <div className="coverage-item">
              <div className="district-name">District 3</div>
              <div className="coverage-stats">
                <span className="store-count">2 stores</span>
                <span className="coverage-percentage">65% coverage</span>
              </div>
            </div>
          </div>
        </div>

        <div className="report-card">
          <h3>Key Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-item">
              <div className="metric-label">Total Revenue</div>
              <div className="metric-value">$45,670</div>
              <div className="metric-change positive">+12.5%</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Average Order</div>
              <div className="metric-value">$23.45</div>
              <div className="metric-change positive">+5.2%</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Customer Count</div>
              <div className="metric-value">1,847</div>
              <div className="metric-change positive">+8.7%</div>
            </div>
            <div className="metric-item">
              <div className="metric-label">Inventory Turnover</div>
              <div className="metric-value">4.2x</div>
              <div className="metric-change negative">-2.1%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports; 