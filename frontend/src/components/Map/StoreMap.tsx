import React, { useRef, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, LayersControl, ScaleControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-fullscreen/dist/leaflet.fullscreen.css';
import 'leaflet-fullscreen/dist/Leaflet.fullscreen.min.js';
import './StoreMap.css';

interface StoreMapProps {
  stores?: any[];
  center?: [number, number];
  zoom?: number;
  height?: string;
  onMapClick?: ((event: any) => void) | null;
  selectedStore?: any | null;
  showLayerControl?: boolean;
  showScaleControl?: boolean;
  showAdvancedControls?: boolean;
  enableClustering?: boolean;
  onLocationFound?: ((location: { lat: number; lng: number; accuracy: number }) => void) | null;
  onLocationError?: ((errorMessage: string) => void) | null;
}

interface MapControlsProps {
  onLocationFound?: ((location: { lat: number; lng: number; accuracy: number }) => void) | null;
  onLocationError?: ((errorMessage: string) => void) | null;
}

// Fix for default markers in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Create custom icons for different store states
const createStoreIcon = (isActive: boolean) => {
  return new L.Icon({
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41],
    className: isActive ? 'store-marker-active' : 'store-marker-inactive'
  });
};

// Custom component to add advanced controls
const MapControls: React.FC<MapControlsProps> = ({ onLocationFound, onLocationError }) => {

  useEffect(() => {
    // Get map instance
    const mapContainer = document.querySelector('.leaflet-container') as any;
    if (mapContainer && mapContainer._leaflet_map) {
      const map = mapContainer._leaflet_map;

      // Add fullscreen control
      if ((L.control as any).fullscreen) {
        (L.control as any).fullscreen({
          position: 'topright'
        }).addTo(map);
      }

      // Create custom locate control
      const CustomLocateControl = L.Control.extend({
        onAdd: function(map: any) {
          const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom-locate');
          
          const button = L.DomUtil.create('a', 'leaflet-control-locate-btn', container);
          button.innerHTML = '📍';
          button.href = '#';
          button.title = 'Find my location';
          button.setAttribute('role', 'button');
          button.setAttribute('aria-label', 'Find my location');

          L.DomEvent.on(button, 'click', (e) => {
            L.DomEvent.preventDefault(e);
            
            if (!navigator.geolocation) {
              onLocationError && onLocationError('Geolocation is not supported by this browser');
              return;
            }

            button.innerHTML = '⏳';
            button.classList.add('loading');

            navigator.geolocation.getCurrentPosition(
              (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const accuracy = position.coords.accuracy;

                // Center map on user location
                map.setView([lat, lng], 16);

                // Add location marker
                const locationMarker = L.marker([lat, lng], {
                  icon: L.divIcon({
                    className: 'user-location-marker',
                    html: '<div class="user-location-dot"></div>',
                    iconSize: [16, 16],
                    iconAnchor: [8, 8]
                  })
                }).addTo(map);

                // Add accuracy circle
                const accuracyCircle = L.circle([lat, lng], {
                  radius: accuracy,
                  fillColor: '#667eea',
                  fillOpacity: 0.2,
                  color: '#667eea',
                  opacity: 0.5,
                  weight: 2
                }).addTo(map);

                locationMarker.bindPopup(`
                  <div class="user-location-popup">
                    <strong>Your Location</strong><br>
                    Accuracy: ±${Math.round(accuracy)}m
                  </div>
                `).openPopup();

                button.innerHTML = '📍';
                button.classList.remove('loading');
                button.classList.add('active');

                onLocationFound && onLocationFound({ lat, lng, accuracy });

                // Remove markers after 10 seconds
                setTimeout(() => {
                  map.removeLayer(locationMarker);
                  map.removeLayer(accuracyCircle);
                  button.classList.remove('active');
                }, 10000);
              },
              (error) => {
                button.innerHTML = '📍';
                button.classList.remove('loading');
                
                let errorMsg = 'Failed to get location';
                switch (error.code) {
                  case error.PERMISSION_DENIED:
                    errorMsg = 'Location access denied by user';
                    break;
                  case error.POSITION_UNAVAILABLE:
                    errorMsg = 'Location information unavailable';
                    break;
                  case error.TIMEOUT:
                    errorMsg = 'Location request timed out';
                    break;
                  default:
                    errorMsg = 'Unknown location error';
                    break;
                }
                
                onLocationError && onLocationError(errorMsg);
              },
              {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
              }
            );
          });

          return container;
        }
      });

      // Add custom locate control to map
      new CustomLocateControl({ position: 'topright' }).addTo(map);
    }
  }, [onLocationFound, onLocationError]);

  return null;
};

const StoreMap: React.FC<StoreMapProps> = ({ 
  stores = [], 
  center = [10.8231, 106.6297], // Ho Chi Minh City coordinates
  zoom = 12,
  height = '400px',
  onMapClick = null,
  selectedStore = null,
  showLayerControl = true,
  showScaleControl = true,
  showAdvancedControls = true,
  enableClustering = false,
  onLocationFound = null,
  onLocationError = null
}) => {
  
  const mapContainerStyle = {
    height: height,
    width: '100%',
    zIndex: 1
  };

  return (
    <div className="store-map">
      <MapContainer
        center={center}
        zoom={zoom}
        style={mapContainerStyle}
        scrollWheelZoom={true}
        zoomControl={true}
      >
        {showLayerControl ? (
          <LayersControl position="topright">
            <LayersControl.BaseLayer checked name="OpenStreetMap">
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                maxZoom={19}
                minZoom={3}
              />
            </LayersControl.BaseLayer>
            
            <LayersControl.BaseLayer name="Satellite">
              <TileLayer
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                attribution='&copy; <a href="https://www.esri.com/">Esri</a>, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community'
                maxZoom={19}
                minZoom={3}
              />
            </LayersControl.BaseLayer>
            
            <LayersControl.BaseLayer name="Terrain">
              <TileLayer
                url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
                maxZoom={17}
                minZoom={3}
              />
            </LayersControl.BaseLayer>
            
            <LayersControl.BaseLayer name="CartoDB Light">
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                maxZoom={19}
                minZoom={3}
              />
            </LayersControl.BaseLayer>
            
            <LayersControl.BaseLayer name="CartoDB Dark">
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                maxZoom={19}
                minZoom={3}
              />
            </LayersControl.BaseLayer>
          </LayersControl>
        ) : (
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            maxZoom={19}
            minZoom={3}
          />
        )}

        {/* Scale Control */}
        {showScaleControl && (
          <ScaleControl position="bottomleft" />
        )}

        {/* Advanced Controls */}
        {showAdvancedControls && (
          <MapControls 
            onLocationFound={onLocationFound}
            onLocationError={onLocationError}
          />
        )}
        
        {stores && stores.length > 0 && stores.map((store) => (
          <Marker 
            key={store.id} 
            position={[store.latitude, store.longitude]}
            icon={createStoreIcon(store.is_active)}
          >
            <Popup maxWidth={300} className="store-popup">
              <div className="store-popup-content">
                <div className="store-popup-header">
                  <h4 className="store-name">{store.name}</h4>
                  <span className={`store-status-badge ${store.is_active ? 'active' : 'inactive'}`}>
                    {store.is_active ? '🟢 Active' : '🔴 Inactive'}
                  </span>
                </div>
                
                <div className="store-popup-details">
                  <div className="popup-row">
                    <span className="popup-icon">📍</span>
                    <span className="popup-label">Address:</span>
                    <span className="popup-value">{store.address}</span>
                  </div>
                  
                  <div className="popup-row">
                    <span className="popup-icon">🗺️</span>
                    <span className="popup-label">District:</span>
                    <span className="popup-value">{store.district_name}</span>
                  </div>
                  
                  <div className="popup-row">
                    <span className="popup-icon">🏪</span>
                    <span className="popup-label">Type:</span>
                    <span className="popup-value">{store.store_type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}</span>
                  </div>
                  
                  {store.phone && (
                    <div className="popup-row">
                      <span className="popup-icon">📞</span>
                      <span className="popup-label">Phone:</span>
                      <span className="popup-value">
                        <a href={`tel:${store.phone}`}>{store.phone}</a>
                      </span>
                    </div>
                  )}
                  
                  {store.email && (
                    <div className="popup-row">
                      <span className="popup-icon">📧</span>
                      <span className="popup-label">Email:</span>
                      <span className="popup-value">
                        <a href={`mailto:${store.email}`}>{store.email}</a>
                      </span>
                    </div>
                  )}
                  
                  {store.opening_hours && (
                    <div className="popup-row">
                      <span className="popup-icon">🕐</span>
                      <span className="popup-label">Hours:</span>
                      <span className="popup-value">{store.opening_hours}</span>
                    </div>
                  )}
                  
                  {store.rating && (
                    <div className="popup-row">
                      <span className="popup-icon">⭐</span>
                      <span className="popup-label">Rating:</span>
                      <span className="popup-value">{store.rating}/5</span>
                    </div>
                  )}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {selectedStore && (
          <Marker 
            position={[selectedStore.latitude, selectedStore.longitude]}
            icon={new L.Icon({
              iconUrl: require('leaflet/dist/images/marker-icon.png'),
              iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
              shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowSize: [41, 41],
              className: 'selected-store-marker'
            })}
          >
            <Popup>
              <div>
                <h4>{selectedStore.name}</h4>
                <p><strong>Address:</strong> {selectedStore.address}</p>
                <p><strong>District:</strong> {selectedStore.district_name}</p>
                <p><strong>Selected Store</strong></p>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
};

export default StoreMap; 