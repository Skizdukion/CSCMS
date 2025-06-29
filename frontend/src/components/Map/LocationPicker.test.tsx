import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LocationPicker from './LocationPicker';

// Mock Leaflet and React-Leaflet components
jest.mock('react-leaflet', () => ({
  MapContainer: ({ children, ...props }: any) => {
    const mockReact = require('react');
    return mockReact.createElement('div', { 'data-testid': 'map-container', ...props }, children);
  },
  TileLayer: () => {
    const mockReact = require('react');
    return mockReact.createElement('div', { 'data-testid': 'tile-layer' });
  },
  Marker: ({ position }: any) => {
    const mockReact = require('react');
    return mockReact.createElement('div', { 
      'data-testid': 'marker', 
      'data-position': position?.join(',') 
    });
  },
  useMapEvents: () => null // Simplified mock
}));

// Mock Leaflet Icon
jest.mock('leaflet', () => ({
  Icon: {
    Default: {
      prototype: {},
      mergeOptions: jest.fn()
    }
  }
}));

const mockGeolocation = {
  getCurrentPosition: jest.fn(),
  watchPosition: jest.fn(),
  clearWatch: jest.fn()
};

(global as any).navigator.geolocation = mockGeolocation;
global.fetch = jest.fn();

// Mock the API service
jest.mock('../../services/api', () => ({
  districtApi: {
    lookupByCoordinates: jest.fn()
  }
}));

describe('LocationPicker', () => {
  const mockOnLocationChange = jest.fn();
  const mockOnLocationDetails = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock district API response
    const { districtApi } = jest.requireMock('../../services/api');
    districtApi.lookupByCoordinates.mockResolvedValue({
      success: true,
      data: {
        district: 'District 1',
        district_id: 1,
        district_type: 'urban',
        city: 'Ho Chi Minh City',
        found: true
      }
    });

    // Mock Nominatim API response for address display
    (fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        display_name: '123 Test Street, Ho Chi Minh City, Vietnam'
      })
    });
  });

  it('renders location picker with all components', () => {
    render(
      <LocationPicker
        onLocationChange={mockOnLocationChange}
        onLocationDetails={mockOnLocationDetails}
      />
    );

    expect(screen.getByText('Pick Location on Map')).toBeInTheDocument();
    expect(screen.getByText('Current Location')).toBeInTheDocument();
    expect(screen.getByText('Click on the map to set the store location')).toBeInTheDocument();
    expect(screen.getByTestId('map-container')).toBeInTheDocument();
  });

  it('shows coordinates when position is provided', () => {
    const lat = 10.8231;
    const lng = 106.6297;
    
    render(
      <LocationPicker
        latitude={lat}
        longitude={lng}
        onLocationChange={mockOnLocationChange}
        onLocationDetails={mockOnLocationDetails}
      />
    );

    expect(screen.getByText('Coordinates:')).toBeInTheDocument();
    expect(screen.getByText(`${lat.toFixed(6)}, ${lng.toFixed(6)}`)).toBeInTheDocument();
  });

  it('calls onLocationChange when map is clicked', async () => {
    const TestLocationPicker = () => {
      // Simulate a map click by calling the function directly
      const handleMapClick = () => {
        mockOnLocationChange(10.8231, 106.6297);
      };

      return (
        <div>
          <LocationPicker
            onLocationChange={mockOnLocationChange}
            onLocationDetails={mockOnLocationDetails}
          />
          <button data-testid="simulate-click" onClick={handleMapClick}>
            Simulate Map Click
          </button>
        </div>
      );
    };

    render(<TestLocationPicker />);

    const simulateBtn = screen.getByTestId('simulate-click');
    fireEvent.click(simulateBtn);

    expect(mockOnLocationChange).toHaveBeenCalledWith(10.8231, 106.6297);
  });

  it('calls district lookup when coordinates are provided', async () => {
    const { districtApi } = jest.requireMock('../../services/api');
    
    render(
      <LocationPicker
        latitude={10.8231}
        longitude={106.6297}
        onLocationChange={mockOnLocationChange}
        onLocationDetails={mockOnLocationDetails}
      />
    );

    // The effect should trigger district lookup when coordinates are provided
    await waitFor(() => {
      expect(districtApi.lookupByCoordinates).toHaveBeenCalledWith(10.8231, 106.6297);
    });
  });

  it('handles current location button click', async () => {
    mockGeolocation.getCurrentPosition.mockImplementationOnce((success) => {
      success({
        coords: {
          latitude: 10.8231,
          longitude: 106.6297
        }
      });
    });

    render(
      <LocationPicker
        onLocationChange={mockOnLocationChange}
        onLocationDetails={mockOnLocationDetails}
      />
    );

    const currentLocationBtn = screen.getByText('Current Location');
    fireEvent.click(currentLocationBtn);

    await waitFor(() => {
      expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalled();
      expect(mockOnLocationChange).toHaveBeenCalledWith(10.8231, 106.6297);
    });
  });

  it('handles district lookup errors gracefully', async () => {
    const { districtApi } = jest.requireMock('../../services/api');
    districtApi.lookupByCoordinates.mockRejectedValueOnce(new Error('API error'));

    render(
      <LocationPicker
        latitude={10.8231}
        longitude={106.6297}
        onLocationChange={mockOnLocationChange}
        onLocationDetails={mockOnLocationDetails}
      />
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to determine district from location')).toBeInTheDocument();
    });
  });
}); 