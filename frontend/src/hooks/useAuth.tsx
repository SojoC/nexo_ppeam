/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useEffect, useState } from 'react';
import { api, login as apiLogin, logout as apiLogout } from '../lib/api';

// Tipo simple para el usuario autenticado
export interface AuthUser {
	id?: string;
	email?: string;
	firstName?: string;
	lastName?: string;
	isActive?: boolean;
	createdAt?: string;
}

interface AuthContextValue {
	user: AuthUser | null;
	isAuthenticated: boolean;
	login: (email: string, password: string) => Promise<void>;
	logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [user, setUser] = useState<AuthUser | null>(null);

		const fetchMe = async () => {
			try {
				const resp = await api.get('/auth/me');
				setUser(resp.data);
			} catch {
				// Si falla, limpiamos el usuario
				setUser(null);
			}
		};

	useEffect(() => {
		// Al montar, si ya hay token en localStorage, intentar poblar el usuario
		const token = localStorage.getItem('access_token');
		if (token) {
			fetchMe();
		}
	}, []);

	const login = async (email: string, password: string) => {
		// Usa la función del cliente API para loguear y luego poblar /auth/me
		await apiLogin(email, password);
		await fetchMe();
	};

	const logout = () => {
		apiLogout();
		setUser(null);
	};

	return (
		<AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
			{children}
		</AuthContext.Provider>
	);
};

export function useAuth() {
	const ctx = useContext(AuthContext);
	if (!ctx) {
		throw new Error('useAuth must be used within an AuthProvider');
	}
	return ctx;
}

// No default export to keep fast-refresh compatibility (only component exports allowed)
