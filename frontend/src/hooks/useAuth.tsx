import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import * as apiClient from "../lib/api";

// -----------------------------
// useAuth.tsx
// - Provee un contexto de autenticación para la app
// - Maneja login/logout y estado del token en localStorage
// - Usa las funciones de `frontend/src/lib/api.ts` para comunicarse con el backend
// -----------------------------

// Tipo del usuario que almacenamos en el frontend (minimal)
export interface AuthUser {
  id?: string;
  email?: string | undefined;
  displayName?: string | undefined;
  // Campos usados por la app en varios componentes
  firstName?: string | undefined;
  lastName?: string | undefined;
  isActive?: boolean | undefined;
  createdAt?: string | undefined;
}

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
    const token = localStorage.getItem("authToken");
    if (token) {
      // Si existe token asumimos sesión válida. No intentamos decodificar el JWT
      // aquí para evitar dependencias adicionales; podríamos obtener perfil
      // desde /auth/me si el backend lo expone.
      setUser({ email: undefined });
    } else {
      setUser(null);
    }
    setIsLoading(false);
  }, []);

  // Login: llama a la API y actualiza el estado
  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      await apiClient.login(email, password);
      // apiClient.login guarda el token en localStorage
      // Guardamos un perfil mínimo (email) en el contexto
      setUser({ email });
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
