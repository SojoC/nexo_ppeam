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
