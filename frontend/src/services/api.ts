import { Store, District, StoreFormData, ApiResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Generic API request handler
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        data: null as T,
        message: data.message || 'An error occurred',
        errors: data.errors || {},
      };
    }

    return {
      success: true,
      data: data.data || data,
      message: data.message,
    };
  } catch (error) {
    console.error('API Request Error:', error);
    return {
      success: false,
      data: null as T,
      message: error instanceof Error ? error.message : 'Network error occurred',
      errors: {},
    };
  }
}

// Store API functions
export const storeApi = {
  // Get all stores with optional filtering
  getStores: async (params?: { 
    search?: string; 
    district?: string; 
    status?: string; 
    page?: number; 
    limit?: number; 
  }): Promise<ApiResponse<{ results: Store[]; count: number; next: string | null; previous: string | null }>> => {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.district) queryParams.append('district', params.district);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    
    const queryString = queryParams.toString();
    const endpoint = `/stores/${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<{ results: Store[]; count: number; next: string | null; previous: string | null }>(endpoint);
  },

  // Advanced search with multiple filters
  searchStores: async (params: {
    search?: string;
    district?: string;
    store_type?: string;
    is_active?: boolean;
    inventory_item?: string;
    latitude?: number;
    longitude?: number;
    radius_km?: number;
    sort_by_distance?: boolean;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ results: Store[]; count: number; next: string | null; previous: string | null }>> => {
    const queryParams = new URLSearchParams();
    
    if (params.search) queryParams.append('search', params.search);
    if (params.district) queryParams.append('district', params.district);
    if (params.store_type) queryParams.append('store_type', params.store_type);
    if (params.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());
    if (params.inventory_item) queryParams.append('inventory_item', params.inventory_item);
    if (params.sort_by_distance !== undefined) queryParams.append('sort_by_distance', params.sort_by_distance.toString());
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    
    // If location search is requested, use the search endpoint with location parameters
    if (params.latitude && params.longitude) {
      queryParams.append('latitude', params.latitude.toString());
      queryParams.append('longitude', params.longitude.toString());
      if (params.radius_km) {
        queryParams.append('radius_km', params.radius_km.toString());
      }
      if (params.sort_by_distance !== undefined) {
        queryParams.append('sort_by_distance', params.sort_by_distance.toString());
      } else {
        queryParams.append('sort_by_distance', 'true');
      }
      
      const queryString = queryParams.toString();
      const endpoint = `/stores/search/${queryString ? `?${queryString}` : ''}`;
      return apiRequest<{ results: Store[]; count: number; next: string | null; previous: string | null }>(endpoint);
    }
    
    // If any advanced filters are used, use the search endpoint
    if (params.inventory_item || params.store_type || params.district || params.is_active !== undefined) {
      const queryString = queryParams.toString();
      const endpoint = `/stores/search/${queryString ? `?${queryString}` : ''}`;
      return apiRequest<{ results: Store[]; count: number; next: string | null; previous: string | null }>(endpoint);
    }
    
    // Otherwise use the basic search endpoint
    const queryString = queryParams.toString();
    const endpoint = `/stores/${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<{ results: Store[]; count: number; next: string | null; previous: string | null }>(endpoint);
  },

  // Get single store by ID
  getStore: async (id: number): Promise<ApiResponse<Store>> => {
    return apiRequest<Store>(`/stores/${id}/`);
  },

  // Create new store
  createStore: async (storeData: StoreFormData): Promise<ApiResponse<Store>> => {
    // Convert form data to API format
    const apiData = {
      name: storeData.name,
      address: storeData.address,
      phone: storeData.phone || null,
      email: storeData.email || null,
      location: {
        type: 'Point',
        coordinates: [parseFloat(storeData.longitude), parseFloat(storeData.latitude)]
      },
      store_type: storeData.store_type,
      district: storeData.district,
      city: storeData.city,
      opening_hours: storeData.opening_hours || null,
      is_active: storeData.is_active,
      rating: storeData.rating ? parseFloat(storeData.rating) : null,
    };

    return apiRequest<Store>('/stores/', {
      method: 'POST',
      body: JSON.stringify(apiData),
    });
  },

  // Update existing store
  updateStore: async (id: number, storeData: StoreFormData): Promise<ApiResponse<Store>> => {
    // Convert form data to API format
    const apiData = {
      name: storeData.name,
      address: storeData.address,
      phone: storeData.phone || null,
      email: storeData.email || null,
      location: {
        type: 'Point',
        coordinates: [parseFloat(storeData.longitude), parseFloat(storeData.latitude)]
      },
      store_type: storeData.store_type,
      district: storeData.district,
      city: storeData.city,
      opening_hours: storeData.opening_hours || null,
      is_active: storeData.is_active,
      rating: storeData.rating ? parseFloat(storeData.rating) : null,
    };

    return apiRequest<Store>(`/stores/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(apiData),
    });
  },

  // Delete store
  deleteStore: async (id: number): Promise<ApiResponse<null>> => {
    return apiRequest<null>(`/stores/${id}/`, {
      method: 'DELETE',
    });
  },


};

// District API functions
export const districtApi = {
  // Get all districts
  getDistricts: async (): Promise<ApiResponse<{ results: District[]; count: number; next: string | null; previous: string | null }>> => {
    return apiRequest<{ results: District[]; count: number; next: string | null; previous: string | null }>('/districts/');
  },

  // Get district by ID
  getDistrict: async (id: number): Promise<ApiResponse<District>> => {
    return apiRequest<District>(`/districts/${id}/`);
  },
};

// Inventory API functions
export const inventoryApi = {
  // Search inventory items
  searchInventory: async (params: {
    item_name?: string;
    category?: string;
    available_only?: boolean;
    store_id?: number;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ results: any[]; count: number; next: string | null; previous: string | null }>> => {
    const queryParams = new URLSearchParams();
    
    if (params.item_name) queryParams.append('item_name', params.item_name);
    if (params.category) queryParams.append('category', params.category);
    if (params.available_only !== undefined) queryParams.append('available_only', params.available_only.toString());
    if (params.store_id) queryParams.append('store', params.store_id.toString());
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    
    const queryString = queryParams.toString();
    const endpoint = `/inventory/search/${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<{ results: any[]; count: number; next: string | null; previous: string | null }>(endpoint);
  },

  // Get inventory items near location
  searchNearbyInventory: async (params: {
    latitude: number;
    longitude: number;
    radius_km: number;
    category?: string;
    item_name?: string;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ results: any[]; count: number; next: string | null; previous: string | null }>> => {
    const queryParams = new URLSearchParams();
    
    queryParams.append('latitude', params.latitude.toString());
    queryParams.append('longitude', params.longitude.toString());
    queryParams.append('radius_km', params.radius_km.toString());
    
    if (params.category) queryParams.append('category', params.category);
    if (params.item_name) queryParams.append('item_name', params.item_name);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    
    const queryString = queryParams.toString();
    const endpoint = `/inventory/nearby/${queryString ? `?${queryString}` : ''}`;
    
    return apiRequest<{ results: any[]; count: number; next: string | null; previous: string | null }>(endpoint);
  },

  // Get available inventory items for filtering
  getAvailableItems: async (): Promise<ApiResponse<{ items: string[] }>> => {
    return apiRequest<{ items: string[] }>('/inventory/available-items/');
  },
};

// Export individual functions for convenience
export const { getStores, getStore, createStore, updateStore, deleteStore, searchStores } = storeApi;
export const { getDistricts, getDistrict } = districtApi;
export const { searchInventory, searchNearbyInventory, getAvailableItems } = inventoryApi; 