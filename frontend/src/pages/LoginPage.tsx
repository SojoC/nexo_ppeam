import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

const loginSchema = z.object({
  email: z.string().email({ message: 'Correo inválido' }),
  password: z.string().min(4, { message: 'Debe contener al menos 4 caracteres' }),
});
type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onBlur',
  });
  const navigate = useNavigate();

  const onSubmit = async (data: LoginFormData) => {
    try {
      const resp = await authAPI.login(data.email, data.password);
      localStorage.setItem('token', resp.access_token);
      navigate('/users');
    } catch (err) {
      console.error('login error', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1f2937] via-[#111827] to-[#0b1120] flex flex-col items-center justify-center py-12 px-6">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-white drop-shadow-md">Nexo PPEAM</h1>
        <p className="text-slate-400 mt-1">Sistema de gestión integral</p>
      </header>
      <div className="w-full max-w-md bg-[#111827] rounded-2xl shadow-2xl border border-[#1e293b] p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Iniciar Sesión</h2>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          {/* Correo */}
          <div className="mb-4">
            <label className="block text-sm text-slate-300 mb-1">Correo electrónico</label>
            <input type="email" {...register('email')} className="w-full rounded-lg bg-[#0f172a] border border-[#334155] px-3 py-2 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="usuario@example.com"/>
            {errors.email && <p className="mt-1 text-xs text-rose-500">{errors.email.message}</p>}
          </div>
          {/* Contraseña */}
          <div className="mb-6">
            <label className="block text-sm text-slate-300 mb-1">Contraseña</label>
            <input type="password" {...register('password')} className="w-full rounded-lg bg-[#0f172a] border border-[#334155] px-3 py-2 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="••••••••"/>
            {errors.password && <p className="mt-1 text-xs text-rose-500">{errors.password.message}</p>}
          </div>
          <button type="submit" className="w-full py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 text-white font-medium transition">Acceder</button>
        </form>
      </div>
      <footer className="mt-8 text-xs text-slate-500">&copy; {new Date().getFullYear()} Nexo PPEAM.</footer>
    </div>
  );
}
