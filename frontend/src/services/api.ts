import type { User, UserInput, LoginResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper to get token from localStorage
const getToken = (): string | null => {
  return localStorage.getItem('token');
};

// Helper to handle API errors
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
    throw new Error(error.detail || `Error ${response.status}`);
  }
  return response.json();
};

// Auth API
export const authAPI = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
  },
};

// Users API
export const usersAPI = {
  getAll: async (): Promise<User[]> => {
    const token = getToken();
    const response = await fetch(`${API_URL}/users`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return handleResponse(response);
  },

  create: async (userData: UserInput): Promise<User> => {
    const token = getToken();
    const payload = {
      ...userData,
      tags: userData.tags.split(',').map(t => t.trim()).filter(Boolean),
    };
    const response = await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    return handleResponse(response);
  },

  update: async (id: string, userData: UserInput): Promise<User> => {
    const token = getToken();
    const payload = {
      ...userData,
      tags: userData.tags.split(',').map(t => t.trim()).filter(Boolean),
    };
    const response = await fetch(`${API_URL}/users/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    return handleResponse(response);
  },

  delete: async (id: string): Promise<void> => {
    const token = getToken();
    const response = await fetch(`${API_URL}/users/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error al eliminar' }));
      throw new Error(error.detail);
    }
  },
};
