import React, { useCallback, useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './LocationPicker.css';

// Fix for default markers in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface LocationPickerProps {
  latitude?: number;
  longitude?: number;
  onLocationChange: (lat: number, lng: number) => void;
  onLocationDetails?: (details: LocationDetails) => void;
  height?: string;
  zoom?: number;
  center?: [number, number];
}

interface LocationDetails {
  address: string;
  district: string;
  city: string;
  country: string;
}

// Custom marker component that handles map clicks
const LocationMarker: React.FC<{
  position: [number, number] | null;
  onLocationChange: (lat: number, lng: number) => void;
}> = ({ position, onLocationChange }) => {
  const map = useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      onLocationChange(lat, lng);
    },
  });

  return position ? (
    <Marker 
      position={position}
      icon={new L.Icon({
        iconUrl: require('leaflet/dist/images/marker-icon.png'),
        iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
        shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
        className: 'location-picker-marker'
      })}
    />
  ) : null;
};

const LocationPicker: React.FC<LocationPickerProps> = ({
  latitude,
  longitude,
  onLocationChange,
  onLocationDetails,
  height = '300px',
  zoom = 13,
  center = [10.8231, 106.6297] // Ho Chi Minh City
}) => {
  const [position, setPosition] = useState<[number, number] | null>(
    latitude && longitude ? [latitude, longitude] : null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update position when props change
  useEffect(() => {
    if (latitude && longitude) {
      setPosition([latitude, longitude]);
    }
  }, [latitude, longitude]);

  // Reverse geocoding function using backend API
  const reverseGeocode = useCallback(async (lat: number, lng: number) => {
    if (!onLocationDetails) return;

    setIsLoading(true);
    setError(null);

    try {
      // Use our backend API to lookup district by coordinates
      const { districtApi } = await import('../../services/api');
      const response = await districtApi.lookupByCoordinates(lat, lng);
      
      if (!response.success) {
        throw new Error('Failed to lookup district from coordinates');
      }

      const data = response.data;
      
      // Also get address from Nominatim for display purposes (optional)
      let address = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
      try {
        const nominatimResponse = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&accept-language=en`
        );
        if (nominatimResponse.ok) {
          const nominatimData = await nominatimResponse.json();
          if (nominatimData.display_name) {
            address = nominatimData.display_name;
          }
        }
      } catch (nominatimError) {
        // If Nominatim fails, continue with coordinates as address
        console.warn('Nominatim geocoding failed, using coordinates as address');
      }

      const locationDetails: LocationDetails = {
        address: address,
        district: data.district,
        city: data.city,
        country: 'Vietnam'
      };

      onLocationDetails(locationDetails);
    } catch (err) {
      console.error('District lookup error:', err);
      setError('Failed to determine district from location');
    } finally {
      setIsLoading(false);
    }
  }, [onLocationDetails]);

  const handleLocationChange = useCallback((lat: number, lng: number) => {
    const newPosition: [number, number] = [lat, lng];
    setPosition(newPosition);
    onLocationChange(lat, lng);
    
    // Perform reverse geocoding
    reverseGeocode(lat, lng);
  }, [onLocationChange, reverseGeocode]);

  const handleGetCurrentLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      return;
    }

    setIsLoading(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        handleLocationChange(latitude, longitude);
        setIsLoading(false);
      },
      (error) => {
        let errorMessage = 'Failed to get current location';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location access denied by user';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out';
            break;
          default:
            errorMessage = 'Unknown location error';
            break;
        }
        setError(errorMessage);
        setIsLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000
      }
    );
  }, [handleLocationChange]);

  // Determine map center - use position if available, otherwise use provided center
  const mapCenter = position || center;

  return (
    <div className="location-picker">
      <div className="location-picker-header">
        <h4>Pick Location on Map</h4>
        <div className="location-picker-actions">
          <button
            type="button"
            className="btn-locate"
            onClick={handleGetCurrentLocation}
            disabled={isLoading}
            title="Get current location"
          >
            {isLoading ? '⏳' : '📍'} {isLoading ? 'Getting...' : 'Current Location'}
          </button>
        </div>
      </div>

      {error && (
        <div className="location-picker-error">
          {error}
        </div>
      )}

      <div className="location-picker-instruction">
        Click on the map to set the store location
      </div>

      <div className="location-picker-map" style={{ height }}>
        <MapContainer
          center={mapCenter}
          zoom={zoom}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <LocationMarker
            position={position}
            onLocationChange={handleLocationChange}
          />
        </MapContainer>
      </div>

      {position && (
        <div className="location-picker-info">
          <div className="coordinates-display">
            <span className="coord-label">Coordinates:</span>
            <span className="coord-value">
              {position[0].toFixed(6)}, {position[1].toFixed(6)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default LocationPicker; 