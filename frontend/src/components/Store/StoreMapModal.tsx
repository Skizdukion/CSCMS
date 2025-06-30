import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Store } from '../../types';
import 'leaflet/dist/leaflet.css';
import './StoreMapModal.css';
import L from 'leaflet';

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

// Fix for default markers in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface StoreMapModalProps {
  store: Store;
  onClose: () => void;
}

const StoreMapModal: React.FC<StoreMapModalProps> = ({ store, onClose }) => {
  // Check if store has location data - use the separate latitude/longitude fields
  if (!store.latitude || !store.longitude) {
    return (
      <div className="store-map-modal-overlay">
        <div className="store-map-modal">
          <div className="store-map-modal-header">
            <h3>{store.name} - Location</h3>
            <button className="close-btn" onClick={onClose}>×</button>
          </div>
          <div className="store-map-modal-content">
            <div className="no-location">
              <p>📍 No location data available for this store.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const position: [number, number] = [
    store.latitude,
    store.longitude
  ];

  return (
    <div className="store-map-modal-overlay">
      <div className="store-map-modal">
        <div className="store-map-modal-header">
          <h3>{store.name} - Location</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="store-map-modal-content">
          <div className="store-info-summary">
            <p><strong>📍 Address:</strong> {store.address}</p>
                            <p><strong>🏪 Brand:</strong> {formatStoreTypeName(store.store_type)}</p>
            {store.phone && <p><strong>📞 Phone:</strong> {store.phone}</p>}
            {store.opening_hours && <p><strong>🕐 Hours:</strong> {store.opening_hours}</p>}
          </div>
          <div className="map-container">
            <MapContainer
              center={position}
              zoom={16}
              style={{ height: '400px', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={position}>
                <Popup>
                  <div className="store-popup">
                    <h4>{store.name}</h4>
                    <p>{store.address}</p>
                    {store.phone && <p>📞 {store.phone}</p>}
                    <p className={`status ${store.is_active ? 'active' : 'inactive'}`}>
                      {store.is_active ? '✅ Active' : '❌ Inactive'}
                    </p>
                  </div>
                </Popup>
              </Marker>
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoreMapModal; 