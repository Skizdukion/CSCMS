export interface Store {
  id?: number;
  name: string;
  address: string;
  phone?: string;
  email?: string;
  location?: {
    latitude: number;
    longitude: number;
  };
  latitude?: number;
  longitude?: number;
  store_type: 'convenience' | 'gas_station' | 'supermarket' | 'pharmacy' | 'other';
  district?: string;
  district_obj?: number;
  city: string;
  opening_hours?: string;
  is_active: boolean;
  rating?: number;
  created_at?: string;
  updated_at?: string;
}

export interface District {
  id: number;
  name: string;
  code: string;
  city: string;
  district_type: 'urban' | 'suburban' | 'rural' | 'industrial' | 'tourist' | 'other';
  is_active: boolean;
}

export interface StoreFormData {
  name: string;
  address: string;
  phone: string;
  email: string;
  latitude: string;
  longitude: string;
  store_type: string;
  district: string;
  city: string;
  opening_hours: string;
  is_active: boolean;
  rating: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

// Search filter interfaces
export interface StoreSearchFilters {
  search?: string;
  district?: string;
  store_type?: string;
  is_active?: boolean;
  inventory_item?: string;
  sort_by_nearby?: boolean;
  latitude?: number;
  longitude?: number;
  radius_km?: number;
  page?: number;
  limit?: number;
}

export interface InventorySearchFilters {
  item_name?: string;
  category?: string;
  available_only?: boolean;
  store_id?: number;
  latitude?: number;
  longitude?: number;
  radius_km?: number;
  page?: number;
  limit?: number;
}

// Item interface
export interface Item {
  id?: number;
  name: string;
  description?: string;
  category: 'beverages' | 'snacks' | 'dairy' | 'frozen' | 'household' | 'personal_care' | 'other';
  brand?: string;
  barcode?: string;
  is_active: boolean;
  store_count?: number;
  available_stores?: number;
  created_at?: string;
  updated_at?: string;
}

// Inventory interface (relationship between items and stores)
export interface Inventory {
  id?: number;
  store: number;
  store_name?: string;
  store_address?: string;
  item: number;
  item_name?: string;
  item_category?: string;
  is_available: boolean;
  stock_status?: 'available' | 'unavailable';
  created_at?: string;
  updated_at?: string;
}

// Location interface for geolocation
export interface UserLocation {
  latitude: number;
  longitude: number;
  accuracy?: number;
} 