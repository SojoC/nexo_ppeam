import React, { useState } from 'react';
import { login as apiLogin, getErrorMessage } from '../lib/api';
import { useNavigate } from 'react-router-dom';

interface LoginFormProps {
	onSuccess?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const navigate = useNavigate();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError(null);
		try {
			await apiLogin(email, password);
			// Si el usuario pasó onSuccess lo ejecutamos, si no redirigimos a /users
			if (onSuccess) {
				onSuccess();
			} else {
				navigate('/users');
			}
		} catch (err) {
			setError(getErrorMessage(err));
		} finally {
			setLoading(false);
		}
	};

	return (
		<form onSubmit={handleSubmit} className="space-y-4">
			{error && <div className="text-sm text-red-400">{error}</div>}

			<div>
				<label className="text-xs text-slate-400">Email</label>
				<input
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					className="w-full mt-1 p-3 rounded bg-[#0b1020] border border-[#263141] text-slate-200"
					type="email"
					required
				/>
			</div>

			<div>
				<label className="text-xs text-slate-400">Contraseña</label>
				<input
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					className="w-full mt-1 p-3 rounded bg-[#0b1020] border border-[#263141] text-slate-200"
					type="password"
					required
				/>
			</div>

			<div className="flex justify-end">
				<button
					type="submit"
					className="px-4 py-2 rounded bg-indigo-500 hover:bg-indigo-600 text-white disabled:opacity-50"
					disabled={loading}
				>
					{loading ? 'Entrando...' : 'Entrar'}
				</button>
			</div>
		</form>
	);
};

export default LoginForm;
