// Types for the application
export interface User {
  id: string;
  name: string;
  email: string;
  age: number;
  phone: string;
  tags: string[];
}

export interface UserInput {
  name: string;
  email: string;
  age: number;
  phone: string;
  tags: string;
}

export interface LoginResponse {
  access_token: string;
  token_type?: string;
}

export interface ApiError {
  detail: string;
}

// Tipos adicionales usados por la nueva UI
export interface UserPayloadV2 {
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
}

export interface UserV2 extends UserPayloadV2 {
  id: string;
  active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AuthUser {
  id?: string;
  email?: string;
  displayName?: string;
  firstName?: string;
  lastName?: string;
  isActive?: boolean;
  createdAt?: string;
}
