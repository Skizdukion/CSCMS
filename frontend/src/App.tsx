import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Stores from './pages/Stores';
import Items from './pages/Items';
import Inventory from './pages/Inventory';
import Analytics from './pages/Analytics';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stores" element={<Stores />} />
            <Route path="/items" element={<Items />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </Layout>
      </div>
    </Router>
  );
}

export default App;
