import React from 'react';
import { render, screen } from '@testing-library/react';
import StoreMap from './StoreMap';

// Mock Leaflet plugins CSS imports
jest.mock('leaflet-fullscreen/dist/leaflet.fullscreen.css', () => ({}));
jest.mock('leaflet-fullscreen/dist/Leaflet.fullscreen.min.js', () => ({}));

// Mock Leaflet since it requires DOM and canvas
jest.mock('leaflet', () => ({
  Icon: class MockIcon {
    constructor(options) {
      this.options = options;
    }
    static Default = {
      prototype: {
        _getIconUrl: jest.fn()
      },
      mergeOptions: jest.fn()
    }
  },
  divIcon: jest.fn((options) => ({ options })),
  marker: jest.fn(() => ({ 
    addTo: jest.fn(() => ({ 
      bindPopup: jest.fn(() => ({ openPopup: jest.fn() }))
    }))
  })),
  circle: jest.fn(() => ({ addTo: jest.fn() })),
  control: {
    fullscreen: jest.fn(() => ({ addTo: jest.fn() }))
  },
  Control: {
    extend: jest.fn((options) => {
      return function() {
        return {
          onAdd: options.onAdd,
          addTo: jest.fn()
        };
      };
    })
  },
  DomUtil: {
    create: jest.fn(() => ({
      innerHTML: '',
      href: '',
      title: '',
      className: '',
      setAttribute: jest.fn(),
      classList: {
        add: jest.fn(),
        remove: jest.fn()
      }
    }))
  },
  DomEvent: {
    on: jest.fn(),
    preventDefault: jest.fn()
  }
}));

// Mock react-leaflet components with LayersControl sub-components
jest.mock('react-leaflet', () => ({
  MapContainer: ({ children, ...props }) => <div data-testid="map-container" {...props}>{children}</div>,
  TileLayer: (props) => <div data-testid="tile-layer" {...props} />,
  Marker: ({ children, ...props }) => <div data-testid="marker" {...props}>{children}</div>,
  Popup: ({ children, ...props }) => <div data-testid="popup" {...props}>{children}</div>,
  LayersControl: Object.assign(
    ({ children, ...props }) => <div data-testid="layers-control" {...props}>{children}</div>,
    {
      BaseLayer: ({ children, ...props }) => <div data-testid="base-layer" {...props}>{children}</div>,
      Overlay: ({ children, ...props }) => <div data-testid="overlay-layer" {...props}>{children}</div>
    }
  ),
  ScaleControl: (props) => <div data-testid="scale-control" {...props} />
}));

describe('StoreMap Component', () => {
  const mockStores = [
    {
      id: 1,
      name: 'Test Store 1',
      address: '123 Test Street',
      district_name: 'District 1',
      store_type: 'Convenience Store',
      is_active: true,
      phone: '0123456789',
      latitude: 10.8231,
      longitude: 106.6297
    },
    {
      id: 2,
      name: 'Test Store 2',
      address: '456 Test Avenue',
      district_name: 'District 2',
      store_type: 'Supermarket',
      is_active: false,
      latitude: 10.8331,
      longitude: 106.6397
    }
  ];

  test('renders map container with default props', () => {
    render(<StoreMap />);
    
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toBeInTheDocument();
    
    // With layer control enabled by default, there are multiple tile layers
    const tileLayers = screen.getAllByTestId('tile-layer');
    expect(tileLayers.length).toBeGreaterThan(0);
  });

  test('renders map with custom center and zoom', () => {
    const customCenter = [10.7769, 106.7009];
    const customZoom = 15;
    
    render(<StoreMap center={customCenter} zoom={customZoom} />);
    
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toBeInTheDocument();
  });

  test('renders store markers when stores are provided', () => {
    render(<StoreMap stores={mockStores} />);
    
    const markers = screen.getAllByTestId('marker');
    expect(markers).toHaveLength(2);
  });

  test('renders popup with store information', () => {
    render(<StoreMap stores={mockStores} />);
    
    const popups = screen.getAllByTestId('popup');
    expect(popups).toHaveLength(2);
    
    // Test first store popup content
    expect(screen.getByText('Test Store 1')).toBeInTheDocument();
    expect(screen.getByText('123 Test Street')).toBeInTheDocument();
    expect(screen.getByText('District 1')).toBeInTheDocument();
    expect(screen.getByText('Convenience Store')).toBeInTheDocument();
    expect(screen.getByText('🟢 Active')).toBeInTheDocument();
    expect(screen.getByText('0123456789')).toBeInTheDocument();
    
    // Test second store popup content (inactive)
    expect(screen.getByText('Test Store 2')).toBeInTheDocument();
    expect(screen.getByText('🔴 Inactive')).toBeInTheDocument();
  });

  test('renders selected store marker when provided', () => {
    const selectedStore = mockStores[0];
    render(<StoreMap stores={mockStores} selectedStore={selectedStore} />);
    
    const markers = screen.getAllByTestId('marker');
    // Should have 2 regular markers + 1 selected marker
    expect(markers).toHaveLength(3);
  });

  test('renders with custom height', () => {
    const customHeight = '600px';
    render(<StoreMap height={customHeight} />);
    
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toBeInTheDocument();
  });

  test('handles empty stores array', () => {
    render(<StoreMap stores={[]} />);
    
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toBeInTheDocument();
    
    // With layer control enabled by default, there are multiple tile layers
    const tileLayers = screen.getAllByTestId('tile-layer');
    expect(tileLayers.length).toBeGreaterThan(0);
    
    // Should not render any markers
    const markers = screen.queryAllByTestId('marker');
    expect(markers).toHaveLength(0);
  });

  test('handles stores without phone numbers', () => {
    const storeWithoutPhone = {
      ...mockStores[0],
      phone: null
    };
    
    render(<StoreMap stores={[storeWithoutPhone]} />);
    
    expect(screen.getByText('Test Store 1')).toBeInTheDocument();
    expect(screen.getByText('123 Test Street')).toBeInTheDocument();
    // Phone should not be rendered
    expect(screen.queryByText('Phone:')).not.toBeInTheDocument();
  });

  test('renders layer control when showLayerControl is true', () => {
    render(<StoreMap showLayerControl={true} />);
    
    const layersControl = screen.getByTestId('layers-control');
    expect(layersControl).toBeInTheDocument();
    
    // Should have multiple base layers
    const baseLayers = screen.getAllByTestId('base-layer');
    expect(baseLayers.length).toBeGreaterThan(1);
  });

  test('renders single tile layer when showLayerControl is false', () => {
    render(<StoreMap showLayerControl={false} />);
    
    const layersControl = screen.queryByTestId('layers-control');
    expect(layersControl).not.toBeInTheDocument();
    
    const tileLayer = screen.getByTestId('tile-layer');
    expect(tileLayer).toBeInTheDocument();
  });

  test('renders scale control when showScaleControl is true', () => {
    render(<StoreMap showScaleControl={true} />);
    
    const scaleControl = screen.getByTestId('scale-control');
    expect(scaleControl).toBeInTheDocument();
  });

  test('does not render scale control when showScaleControl is false', () => {
    render(<StoreMap showScaleControl={false} />);
    
    const scaleControl = screen.queryByTestId('scale-control');
    expect(scaleControl).not.toBeInTheDocument();
  });

  test('renders with all new props', () => {
    const props = {
      stores: mockStores,
      center: [10.7769, 106.7009],
      zoom: 15,
      height: '600px',
      showLayerControl: true,
      showScaleControl: true,
      showAdvancedControls: true,
      enableClustering: false
    };
    
    render(<StoreMap {...props} />);
    
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toBeInTheDocument();
    
    const layersControl = screen.getByTestId('layers-control');
    expect(layersControl).toBeInTheDocument();
    
    const scaleControl = screen.getByTestId('scale-control');
    expect(scaleControl).toBeInTheDocument();
  });

  test('renders different tile layer options', () => {
    render(<StoreMap showLayerControl={true} />);
    
    const baseLayers = screen.getAllByTestId('base-layer');
    expect(baseLayers.length).toBe(5); // OpenStreetMap, Satellite, Terrain, CartoDB Light, CartoDB Dark
  });

  test('renders enhanced popup with additional store details', () => {
    const storeWithAllDetails = {
      id: 3,
      name: 'Full Details Store',
      address: '789 Complete Street',
      district_name: 'District 3',
      store_type: 'gas_station',
      is_active: true,
      phone: '0987654321',
      email: 'store@example.com',
      opening_hours: '24/7',
      rating: 4.5,
      latitude: 10.8431,
      longitude: 106.6497
    };
    
    render(<StoreMap stores={[storeWithAllDetails]} />);
    
    // Test enhanced popup content
    expect(screen.getByText('Full Details Store')).toBeInTheDocument();
    expect(screen.getByText('789 Complete Street')).toBeInTheDocument();
    expect(screen.getByText('District 3')).toBeInTheDocument();
    expect(screen.getByText('Gas Station')).toBeInTheDocument(); // Formatted store type
    expect(screen.getByText('🟢 Active')).toBeInTheDocument();
    expect(screen.getByText('0987654321')).toBeInTheDocument();
    expect(screen.getByText('store@example.com')).toBeInTheDocument();
    expect(screen.getByText('24/7')).toBeInTheDocument();
    expect(screen.getByText('4.5/5')).toBeInTheDocument();
  });

  test('handles stores with minimal information', () => {
    const minimalStore = {
      id: 4,
      name: 'Minimal Store',
      address: '321 Basic Street',
      district_name: 'District 4',
      store_type: 'convenience',
      is_active: false,
      latitude: 10.8531,
      longitude: 106.6597
      // No phone, email, opening_hours, or rating
    };
    
    render(<StoreMap stores={[minimalStore]} />);
    
    // Should render basic information
    expect(screen.getByText('Minimal Store')).toBeInTheDocument();
    expect(screen.getByText('321 Basic Street')).toBeInTheDocument();
    expect(screen.getByText('District 4')).toBeInTheDocument();
    expect(screen.getByText('Convenience')).toBeInTheDocument();
    expect(screen.getByText('🔴 Inactive')).toBeInTheDocument();
    
    // Should not render optional fields
    expect(screen.queryByText('Phone:')).not.toBeInTheDocument();
    expect(screen.queryByText('Email:')).not.toBeInTheDocument();
    expect(screen.queryByText('Hours:')).not.toBeInTheDocument();
    expect(screen.queryByText('Rating:')).not.toBeInTheDocument();
  });
}); 