// Hook personalizado para autenticación con manejo completo de estado
// Incluye login, logout, registro, verificación de tokens y estado persistente

import { useState, useEffect, useCallback, useContext, createContext, useRef } from 'react';
import { 
  login as apiLogin, 
  register as apiRegister,
  logout as apiLogout,
  isAuthenticated,
  getErrorMessage 
} from '../lib/api';

// ==================== TIPOS ====================

interface User {
  id: string;
  email: string;
  display_name: string;
  provider: string;
  role: string;
  active: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, displayName?: string) => Promise<boolean>;
  logout: () => void;
  clearError: () => void;
  refreshAuth: () => Promise<void>;
}

interface UseAuthOptions {
  /** Persistir sesión en localStorage */
  persist?: boolean;
  /** Auto-refresh del token antes de expirar */
  autoRefresh?: boolean;
  /** Redirigir a esta ruta al hacer logout */
  logoutRedirect?: string;
}

// ==================== CONTEXT ====================

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuthContext = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext debe usarse dentro de AuthProvider');
  }
  return context;
};

// ==================== PROVIDER ====================

interface AuthProviderProps {
  children: React.ReactNode;
  options?: UseAuthOptions;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children, options = {} }) => {
  const authValue = useAuth(options);
  
  return (
    <AuthContext.Provider value={authValue}>
      {children}
    </AuthContext.Provider>
  );
};

// ==================== HOOK PRINCIPAL ====================

export const useAuth = (options: UseAuthOptions = {}): AuthContextType => {
  const {
    persist = true,
    autoRefresh = true,
    logoutRedirect = '/login'
  } = options;

  // ==================== ESTADO ====================
  
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    loading: true, // true inicialmente para verificar token existente
    error: null
  });

  // Refs para evitar memory leaks
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  // ==================== UTILIDADES ====================
  
  const setStateIfMounted = useCallback((newState: Partial<AuthState>) => {
    if (mountedRef.current) {
      setState(prev => ({ ...prev, ...newState }));
    }
  }, []);

  const clearError = useCallback(() => {
    setStateIfMounted({ error: null });
  }, [setStateIfMounted]);

  const saveToStorage = useCallback((token: string, user: User) => {
    if (persist) {
      try {
        localStorage.setItem('access_token', token);
        localStorage.setItem('user_data', JSON.stringify(user));
      } catch (error) {
        console.warn('Error guardando en localStorage:', error);
      }
    }
  }, [persist]);

  const clearStorage = useCallback(() => {
    if (persist) {
      try {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
      } catch (error) {
        console.warn('Error limpiando localStorage:', error);
      }
    }
  }, [persist]);

  const loadFromStorage = useCallback((): { token: string | null; user: User | null } => {
    if (!persist) return { token: null, user: null };

    try {
      const token = localStorage.getItem('access_token');
      const userData = localStorage.getItem('user_data');
      
      if (token && userData) {
        const user = JSON.parse(userData);
        return { token, user };
      }
    } catch (error) {
      console.warn('Error cargando desde localStorage:', error);
      clearStorage();
    }

    return { token: null, user: null };
  }, [persist, clearStorage]);

  // ==================== FUNCIONES DE TOKEN ====================
  
  const decodeToken = useCallback((token: string): any | null => {
    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      return decoded;
    } catch (error) {
      return null;
    }
  }, []);

  const isTokenExpired = useCallback((token: string): boolean => {
    const decoded = decodeToken(token);
    if (!decoded || !decoded.exp) return true;
    
    const now = Math.floor(Date.now() / 1000);
    return decoded.exp <= now;
  }, [decodeToken]);

  const getTokenTimeToExpiry = useCallback((token: string): number => {
    const decoded = decodeToken(token);
    if (!decoded || !decoded.exp) return 0;
    
    const now = Math.floor(Date.now() / 1000);
    return Math.max(0, decoded.exp - now);
  }, [decodeToken]);

  // ==================== ACCIONES DE AUTENTICACIÓN ====================
  
  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    try {
      setStateIfMounted({ loading: true, error: null });
      
      const response = await apiLogin(email, password);
      
      if (response.access_token) {
        // Simular obtención de datos de usuario (en un caso real vendría del token o API)
        const userData: User = {
          id: email,
          email: email,
          display_name: email.split('@')[0],
          provider: 'password',
          role: 'user',
          active: true
        };

        saveToStorage(response.access_token, userData);
        
        setStateIfMounted({
          user: userData,
          token: response.access_token,
          isAuthenticated: true,
          loading: false,
          error: null
        });

        // Configurar auto-refresh si está habilitado
        if (autoRefresh) {
          scheduleTokenRefresh(response.access_token);
        }

        return true;
      }

      return false;
      
    } catch (err: any) {
      const errorMessage = getErrorMessage(err);
      setStateIfMounted({ 
        loading: false, 
        error: errorMessage,
        isAuthenticated: false,
        user: null,
        token: null
      });
      clearStorage();
      return false;
    }
  }, [setStateIfMounted, saveToStorage, clearStorage, autoRefresh]);

  const register = useCallback(async (
    email: string, 
    password: string, 
    displayName?: string
  ): Promise<boolean> => {
    try {
      setStateIfMounted({ loading: true, error: null });
      
      const response = await apiRegister(email, password, displayName);
      
      if (response.id) {
        // Auto-login después del registro exitoso
        return await login(email, password);
      }

      return false;
      
    } catch (err: any) {
      const errorMessage = getErrorMessage(err);
      setStateIfMounted({ 
        loading: false, 
        error: errorMessage 
      });
      return false;
    }
  }, [setStateIfMounted, login]);

  const logout = useCallback(() => {
    // Limpiar timeout de refresh
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
      refreshTimeoutRef.current = null;
    }

    // Limpiar estado
    setStateIfMounted({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      error: null
    });

    // Limpiar storage
    clearStorage();

    // Llamar API logout (opcional, para logs del servidor)
    apiLogout().catch(console.warn);

    // Redirigir si se especifica
    if (logoutRedirect && typeof window !== 'undefined') {
      window.location.href = logoutRedirect;
    }
  }, [setStateIfMounted, clearStorage, logoutRedirect]);

  const refreshAuth = useCallback(async (): Promise<void> => {
    const { token, user } = loadFromStorage();
    
    if (!token || !user) {
      setStateIfMounted({
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null
      });
      return;
    }

    // Verificar si el token sigue siendo válido
    if (isTokenExpired(token)) {
      logout();
      return;
    }

    // Token válido, restaurar sesión
    setStateIfMounted({
      user,
      token,
      isAuthenticated: true,
      loading: false,
      error: null
    });

    // Programar auto-refresh si está habilitado
    if (autoRefresh) {
      scheduleTokenRefresh(token);
    }
  }, [loadFromStorage, setStateIfMounted, isTokenExpired, logout, autoRefresh]);

  // ==================== AUTO-REFRESH ====================
  
  const scheduleTokenRefresh = useCallback((token: string) => {
    if (!autoRefresh) return;

    // Limpiar timeout anterior
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }

    const timeToExpiry = getTokenTimeToExpiry(token);
    
    // Programar refresh 5 minutos antes de expirar (mínimo 1 minuto)
    const refreshIn = Math.max(60, (timeToExpiry - 300)) * 1000;

    if (refreshIn > 0) {
      refreshTimeoutRef.current = setTimeout(async () => {
        try {
          // Aquí iría la lógica de refresh del token
          // Por ahora, solo validamos que siga siendo válido
          const currentToken = localStorage.getItem('access_token');
          if (currentToken && isTokenExpired(currentToken)) {
            logout();
          }
        } catch (error) {
          console.warn('Error en auto-refresh:', error);
          logout();
        }
      }, refreshIn);
    }
  }, [autoRefresh, getTokenTimeToExpiry, isTokenExpired, logout]);

  // ==================== EFECTOS ====================
  
  // Inicialización: cargar estado desde localStorage
  useEffect(() => {
    refreshAuth();
  }, []); // Solo al montar

  // Cleanup al desmontar
  useEffect(() => {
    mountedRef.current = true;
    
    return () => {
      mountedRef.current = false;
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, []);

  // Listener para cambios de localStorage (múltiples tabs)
  useEffect(() => {
    if (!persist) return;

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token' && e.newValue === null) {
        // Token removido en otra tab
        logout();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [persist, logout]);

  // ==================== RETURN ====================
  
  return {
    ...state,
    login,
    register,
    logout,
    clearError,
    refreshAuth
  };
};

// ==================== HOOKS AUXILIARES ====================

/**
 * Hook para verificar si el usuario tiene permisos específicos
 */
export const usePermissions = () => {
  const { user } = useAuthContext();
  
  const hasRole = useCallback((requiredRole: string): boolean => {
    if (!user) return false;
    return user.role === requiredRole || user.role === 'admin';
  }, [user]);

  const hasAnyRole = useCallback((roles: string[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role) || user.role === 'admin';
  }, [user]);

  const isAdmin = useCallback((): boolean => {
    return user?.role === 'admin' || false;
  }, [user]);

  const isActive = useCallback((): boolean => {
    return user?.active || false;
  }, [user]);

  return {
    hasRole,
    hasAnyRole,
    isAdmin,
    isActive,
    currentRole: user?.role || null
  };
};

/**
 * Hook para componentes que requieren autenticación
 */
export const useRequireAuth = (redirectTo: string = '/login') => {
  const { isAuthenticated, loading } = useAuthContext();

  useEffect(() => {
    if (!loading && !isAuthenticated && typeof window !== 'undefined') {
      window.location.href = redirectTo;
    }
  }, [isAuthenticated, loading, redirectTo]);

  return { isAuthenticated, loading };
};