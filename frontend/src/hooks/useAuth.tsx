import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import * as apiClient from "../lib/api";
import type { AuthUser } from "../types";

// -----------------------------
// useAuth.tsx
// - Provee un contexto de autenticación para la app
// - Maneja login/logout y estado del token en localStorage
// - Usa las funciones de `frontend/src/lib/api.ts` para comunicarse con el backend
// -----------------------------

// Usamos el tipo centralizado `AuthUser` de `src/types.ts`

// Interfaz del contexto de Auth
export interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  // Operaciones principales
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  logout: () => void;
}

// Contexto exportado (se puede importar desde otros componentes)
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider que envuelve la app y mantiene el estado de autenticación
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Comprobar token al montar el provider
  useEffect(() => {
    const initialize = async () => {
      const token = localStorage.getItem("authToken");
      if (!token) {
        // No hay token guardado
        setUser(null);
        setIsLoading(false);
        return;
      }

      // Si hay token, intentamos obtener el perfil real desde /auth/me
      try {
        const resp = await apiClient.api.get('/auth/me');
        // Resp.data puede tener distintos campos según el backend; mapeamos defensivamente
        const data = resp.data || {};
        setUser({
          id: data.id || data.user_id || undefined,
          email: data.email || undefined,
          displayName: data.display_name || data.displayName || undefined,
          firstName: data.first_name || data.firstName || undefined,
          lastName: data.last_name || data.lastName || undefined,
          isActive: typeof data.is_active === 'boolean' ? data.is_active : data.isActive,
          createdAt: data.created_at || data.createdAt || undefined,
        });
      } catch (error) {
        // Si la petición falla (token inválido/expirado), limpiamos el token
        // y dejamos un debug para diagnóstico en desarrollo
        // (no mostramos el error al usuario desde aquí)
  console.debug('Auth initialize error:', error);
        localStorage.removeItem('authToken');
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    void initialize();
  }, []);

  // Login: llama a la API y actualiza el estado
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // Llamamos al endpoint de login que guarda el token en localStorage
      await apiClient.login(email, password);

      // Tras login exitoso, pedimos el perfil completo al backend
      try {
        const resp = await apiClient.api.get('/auth/me');
        const data = resp.data || {};
        setUser({
          id: data.id || data.user_id || undefined,
          email: data.email || email,
          displayName: data.display_name || data.displayName || undefined,
          firstName: data.first_name || data.firstName || undefined,
          lastName: data.last_name || data.lastName || undefined,
          isActive: typeof data.is_active === 'boolean' ? data.is_active : data.isActive,
          createdAt: data.created_at || data.createdAt || undefined,
        });
      } catch (error) {
        // Si no existe /auth/me o falla, nos quedamos con un perfil mínimo
  console.debug('Auth login: /auth/me error:', error);
        setUser({ email });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Registro sencillo: llama al endpoint y deja el login como siguiente paso
  const register = async (email: string, password: string, displayName?: string) => {
    setIsLoading(true);
    try {
      await apiClient.registerAuth(email, password, displayName);
      // No iniciamos sesión automáticamente; el usuario puede hacer login
    } finally {
      setIsLoading(false);
    }
  };

  // Logout: limpiar token y estado de usuario
  const logout = () => {
    apiClient.logout();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook conveniente para consumir el contexto
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
