import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

// Tipos para autenticación
export interface AuthUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api/v2';

// Función para hacer peticiones HTTP
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = localStorage.getItem('authToken');
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  const response = await fetch(url, config);
  
  if (!response.ok) {
    let errorMessage = `Error ${response.status}`;
    
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // Si no se puede parsear el JSON, usar mensaje por defecto
    }
    
    throw new Error(errorMessage);
  }
  
  return response.json();
}

// Crear el contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider de autenticación
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Función para guardar token y usuario
  const setAuth = (token: string, user: AuthUser) => {
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
    setAuthState({
      user,
      token,
      isAuthenticated: true,
      isLoading: false,
    });
  };

  // Función para limpiar autenticación
  const clearAuth = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  };

  // Login
  const login = async (credentials: LoginCredentials) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      const response = await apiRequest<{ access_token: string; user: AuthUser }>(
        '/auth/login',
        {
          method: 'POST',
          body: JSON.stringify(credentials),
        }
      );
      
      setAuth(response.access_token, response.user);
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  // Register
  const register = async (data: RegisterData) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      
      const response = await apiRequest<{ access_token: string; user: AuthUser }>(
        '/auth/register',
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
      
      setAuth(response.access_token, response.user);
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  };

  // Logout
  const logout = () => {
    clearAuth();
  };

  // Refresh token
  const refreshToken = useCallback(async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        clearAuth();
        return;
      }

      const response = await apiRequest<{ user: AuthUser }>('/auth/me');
      
      setAuthState(prev => ({
        ...prev,
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      }));
    } catch (error) {
      console.error('Error refreshing token:', error);
      clearAuth();
    }
  }, []); // Sin dependencias porque clearAuth no cambia

  // Verificar autenticación al inicializar
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('authToken');
      const savedUser = localStorage.getItem('user');

      if (token && savedUser) {
        try {
          const user = JSON.parse(savedUser);
          setAuthState({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
          });
          
          // Verificar que el token sigue siendo válido
          await refreshToken();
        } catch (error) {
          console.error('Error parsing saved user or verifying token:', error);
          clearAuth();
        }
      } else {
        setAuthState(prev => ({ ...prev, isLoading: false }));
      }
    };

    initializeAuth();
  }, []); // refreshToken se define arriba, no cambia

  // Auto-refresh token cada 30 minutos
  useEffect(() => {
    if (authState.isAuthenticated) {
      const interval = setInterval(refreshToken, 30 * 60 * 1000); // 30 minutos
      return () => clearInterval(interval);
    }
  }, [authState.isAuthenticated, refreshToken]);

  const contextValue: AuthContextType = {
    ...authState,
    login,
    register,
    logout,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook para usar el contexto de autenticación
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
}

// Hook para proteger rutas
export function useRequireAuth() {
  const auth = useAuth();
  
  useEffect(() => {
    if (!auth.isLoading && !auth.isAuthenticated) {
      // Redirigir al login o mostrar mensaje
      window.location.href = '/login';
    }
  }, [auth.isLoading, auth.isAuthenticated]);

  return auth;
}