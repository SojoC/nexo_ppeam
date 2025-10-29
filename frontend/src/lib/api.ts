// Cliente axios centralizado y helpers para AUTH y USERS.
// Comentarios extensos para entender cada parte.

import axios from "axios";

// Lee la URL de la API del archivo .env (VITE_API_URL=http://localhost:8000)
export const API_URL = import.meta.env.VITE_API_URL as string;

// Instancia axios con baseURL para evitar repetir rutas absolutas
// Por defecto apuntamos a la versión v2 de la API si no está incluida en la URL
const API_BASE = API_URL.endsWith('/api/v2') ? API_URL : `${API_URL.replace(/\/$/, '')}/api/v2`;

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para incluir token JWT automáticamente en todas las requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido, limpiar localStorage
      localStorage.removeItem('authToken');
      // Opcional: redirigir a login
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============== TIPOS TYPESCRIPT ==============

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type RegisterResponse = {
  id: string;
  email: string;
  display_name?: string;
};

export type UserPayload = {
  nombre: string;
  edad?: number | null;
  fecha_nacimiento?: string | null;
  sexo?: string | null;
  estado_civil?: string | null;
  fecha_bautismo?: string | null;
  privilegio?: string | null;
  telefono?: string | null;
  congregacion?: string | null;
  ciudad?: string | null;
  email?: string | null;
};

export type User = UserPayload & {
  id: string;
};

// ============== AUTH API ==============

/**
 * Registrar nuevo usuario en el sistema de autenticación
 * @param email Email del usuario
 * @param password Contraseña en texto plano
 * @param display_name Nombre a mostrar (opcional)
 * @returns Datos del usuario registrado
 */
export async function registerAuth(
  email: string, 
  password: string, 
  display_name?: string
): Promise<RegisterResponse> {
  const response = await api.post('/auth/register', {
    email,
    password,
    display_name,
  });
  return response.data;
}

/**
 * Iniciar sesión con email y contraseña
 * @param email Email del usuario
 * @param password Contraseña
 * @returns Token JWT y tipo
 */
export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await api.post('/auth/login', { email, password });
  
  // Guardar token en localStorage para requests futuras
  if (response.data.access_token) {
    localStorage.setItem('authToken', response.data.access_token);
  }
  
  return response.data;
}

/**
 * Solicitar código OTP por SMS (mock)
 * @param phone Número de teléfono
 * @returns Confirmación del envío
 */
export async function requestSmsOtp(phone: string) {
  const response = await api.post('/auth/sms/request', { phone });
  return response.data;
}

/**
 * Verificar código OTP por SMS (mock)
 * @param phone Número de teléfono
 * @param code Código OTP recibido
 * @returns Token JWT si es válido
 */
export async function verifySmsOtp(phone: string, code: string): Promise<LoginResponse> {
  const response = await api.post('/auth/sms/verify', { phone, code });
  
  // Guardar token en localStorage
  if (response.data.access_token) {
    localStorage.setItem('authToken', response.data.access_token);
  }
  
  return response.data;
}

/**
 * Cerrar sesión (limpiar token local)
 */
export function logout() {
  localStorage.removeItem('authToken');
}

/**
 * Verificar si el usuario está autenticado
 * @returns true si hay token guardado
 */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('authToken');
}

// ============== USERS CRUD ==============

/**
 * Crear nuevo usuario en el sistema
 * @param payload Datos del usuario a crear
 * @returns Usuario creado con ID
 */
export async function createUser(payload: UserPayload): Promise<User> {
  const response = await api.post('/users', payload);
  return response.data;
}

/**
 * Listar usuarios con filtros opcionales
 * @param limit Número máximo de usuarios (default: 50)
 * @param congregacion Filtrar por congregación (opcional)
 * @returns Array de usuarios
 */
export async function listUsers(
  limit: number = 50, 
  congregacion?: string
): Promise<User[]> {
  const params: Record<string, string | number> = { limit };
  if (congregacion) {
    params.congregacion = congregacion;
  }
  
  const response = await api.get('/users', { params });
  return response.data;
}

/**
 * Obtener usuario específico por ID
 * @param id ID del usuario
 * @returns Datos del usuario
 */
export async function getUser(id: string): Promise<User> {
  const response = await api.get(`/users/${id}`);
  return response.data;
}

/**
 * Actualizar usuario existente
 * @param id ID del usuario a actualizar
 * @param payload Datos a actualizar
 * @returns Usuario actualizado
 */
export async function updateUser(id: string, payload: UserPayload): Promise<User> {
  const response = await api.put(`/users/${id}`, payload);
  return response.data;
}

/**
 * Eliminar usuario por ID
 * @param id ID del usuario a eliminar
 * @returns Confirmación de eliminación
 */
export async function deleteUser(id: string): Promise<{ status: string; message: string }> {
  const response = await api.delete(`/users/${id}`);
  return response.data;
}

/**
 * Buscar usuario por número de teléfono
 * @param phone Número de teléfono
 * @returns Usuario encontrado
 */
export async function getUserByPhone(phone: string): Promise<User> {
  const response = await api.get(`/users/by-phone/${phone}`);
  return response.data;
}

/**
 * Obtener estadísticas de usuarios por congregación
 * @returns Estadísticas agrupadas
 */
export async function getUserStats(): Promise<{
  congregaciones: Record<string, number>;
  total_usuarios: number;
}> {
  const response = await api.get('/users/stats/congregaciones');
  return response.data;
}

// ============== ERROR HANDLING ==============

/**
 * Extraer mensaje de error legible desde respuesta de API
 * @param error Error de axios
 * @returns Mensaje de error para mostrar al usuario
 */
export function getErrorMessage(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const axiosError = error as { response?: { data?: { detail?: string; message?: string } } };
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    if (axiosError.response?.data?.message) {
      return axiosError.response.data.message;
    }
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return 'Error desconocido. Revisa la conexión con el servidor.';
}