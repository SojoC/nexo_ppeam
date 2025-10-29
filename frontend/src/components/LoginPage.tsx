import { Card } from './ui/Card';
import { LoginForm } from './LoginForm';

interface LoginPageProps {
  onLoginSuccess?: () => void;
}

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b0f1a] via-[#111827] to-[#1e293b] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Efectos de fondo mejorados */}
      <div className="absolute inset-0">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-purple-500/20 to-indigo-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
      </div>
      
      <div className="relative w-full max-w-lg z-10">
        {/* Header compacto */}
        <div className="text-center mb-6">
          <div className="mb-3 flex justify-center">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 rounded-lg flex items-center justify-center shadow-lg">
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.9 1 3 1.9 3 3V21C3 22.1 3.9 23 5 23H19C20.1 23 21 22.1 21 21V9M19 9H14V4H19V9Z"/>
              </svg>
            </div>
          </div>
          
          <h1 className="text-xl font-bold text-white mb-1">
            Nexo PPEAM
          </h1>
          
          <div className="space-y-0.5">
            <p className="text-sm text-slate-300">
              Sistema de Gestión Integral
            </p>
            <p className="text-slate-400 text-xs">
              Administra tu congregación
            </p>
          </div>
        </div>
        
        {/* Tarjeta de login compacta */}
        <Card className="p-6 bg-[#1f2937]/90 backdrop-blur-xl border border-[#374151]/50 shadow-2xl">
          <div className="mb-4 text-center">
            <h2 className="text-lg font-bold text-white mb-1">Bienvenido</h2>
            <p className="text-slate-400 text-xs">Ingresa tus credenciales para continuar</p>
          </div>
          
          <LoginForm onSuccess={onLoginSuccess} />
          
          {/* Separador */}
          <div className="my-6 flex items-center">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[#374151] to-transparent"></div>
            <span className="px-3 text-xs text-slate-500 uppercase tracking-wider">Credenciales</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[#374151] to-transparent"></div>
          </div>
          
          {/* Credenciales de demo compactas */}
          <div className="space-y-2">
            <div className="bg-[#111827]/70 p-3 rounded-lg border border-[#374151]/30 hover:border-indigo-500/30 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-indigo-400">Administrador</p>
                  <p className="text-xs text-slate-500">Acceso completo</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-400 font-mono">admin@nexo.com</p>
                  <p className="text-xs text-slate-400 font-mono">administrador2025</p>
                </div>
              </div>
            </div>
            
            <div className="bg-[#111827]/70 p-3 rounded-lg border border-[#374151]/30 hover:border-purple-500/30 transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-purple-400">Mirian Marquez</p>
                  <p className="text-xs text-slate-500">Precursora regular</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-400 font-mono">mirianmarquez@gmail.com</p>
                  <p className="text-xs text-slate-400 font-mono">mirian123</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
        
        {/* Footer compacto */}
        <div className="text-center mt-6">
          <p className="text-slate-500 text-xs">
            © 2025 Nexo PPEAM. Sistema de gestión integral.
          </p>
          <div className="flex justify-center gap-2 text-xs text-slate-600 mt-1">
            <span>v2.0</span>
            <span>•</span>
            <span>React + FastAPI</span>
          </div>
        </div>
      </div>
    </div>
  );
}