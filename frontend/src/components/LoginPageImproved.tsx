import { Card } from './ui/Card';
import { LoginForm } from './LoginForm';

interface LoginPageProps {
  onLoginSuccess?: () => void;
}

export function LoginPageImproved({ onLoginSuccess }: LoginPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b0f1a] via-[#111827] to-[#1e293b] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Efectos de fondo mejorados */}
      <div className="absolute inset-0">
        {/* Círculos de fondo */}
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-purple-500/20 to-indigo-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        
        {/* Puntos decorativos */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-10 left-10 w-1 h-1 bg-white rounded-full"></div>
          <div className="absolute top-20 right-20 w-1 h-1 bg-white rounded-full"></div>
          <div className="absolute bottom-20 left-20 w-1 h-1 bg-white rounded-full"></div>
        </div>
      </div>
      
      <div className="relative w-full max-w-lg z-10">
        {/* Header mejorado con animaciones */}
        <div className="text-center mb-10">
          {/* Logo animado */}
          <div className="mb-6 flex justify-center">
            <div className="relative">
              <div className="w-20 h-20 bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 rounded-3xl flex items-center justify-center shadow-2xl transform hover:scale-105 transition-all duration-300">
                <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.9 1 3 1.9 3 3V21C3 22.1 3.9 23 5 23H19C20.1 23 21 22.1 21 21V9M19 9H14V4H19V9Z"/>
                </svg>
              </div>
              {/* Anillo decorativo */}
              <div className="absolute -inset-2 bg-gradient-to-r from-indigo-500/30 to-purple-500/30 rounded-full blur-md animate-spin-slow"></div>
            </div>
          </div>
          
          {/* Título con gradiente animado */}
          <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4 animate-fade-in">
            Nexo PPEAM
          </h1>
          
          {/* Subtítulos */}
          <div className="space-y-2">
            <p className="text-xl text-slate-300 font-medium">
              Sistema de Gestión Integral
            </p>
            <p className="text-slate-400">
              Administra tu congregación de forma eficiente y moderna
            </p>
          </div>
        </div>
        
        {/* Tarjeta de login mejorada */}
        <Card className="p-8 bg-[#1f2937]/90 backdrop-blur-xl border border-[#374151]/50 shadow-2xl hover:shadow-3xl transition-all duration-300">
          {/* Header del formulario */}
          <div className="mb-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-2">Bienvenido</h2>
            <p className="text-slate-400">Ingresa tus credenciales para continuar</p>
          </div>
          
          {/* Formulario de login */}
          <LoginForm onSuccess={onLoginSuccess} />
          
          {/* Separador */}
          <div className="my-8 flex items-center">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[#374151] to-transparent"></div>
            <span className="px-4 text-xs text-slate-500 uppercase tracking-wider">Información</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[#374151] to-transparent"></div>
          </div>
          
          {/* Credenciales de demo */}
          <div className="space-y-4">
            <div className="text-center">
              <p className="text-sm text-slate-400 mb-3">Credenciales de prueba disponibles:</p>
            </div>
            
            {/* Tarjetas de credenciales */}
            <div className="grid gap-3">
              <div className="bg-[#111827]/70 p-4 rounded-xl border border-[#374151]/30 hover:border-indigo-500/30 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-indigo-400">Administrador</p>
                    <p className="text-xs text-slate-500 mt-1">Acceso completo al sistema</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-400 font-mono">admin@nexo.com</p>
                    <p className="text-xs text-slate-400 font-mono">administrador2025</p>
                  </div>
                </div>
              </div>
              
              <div className="bg-[#111827]/70 p-4 rounded-xl border border-[#374151]/30 hover:border-purple-500/30 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-400">Mirian Marquez</p>
                    <p className="text-xs text-slate-500 mt-1">Precursora regular</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-400 font-mono">mirianmarquez@gmail.com</p>
                    <p className="text-xs text-slate-400 font-mono">mirian123</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Características del sistema */}
          <div className="mt-8 pt-6 border-t border-[#374151]/50">
            <p className="text-xs text-slate-500 text-center mb-4">Características del sistema:</p>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="flex items-center gap-2 text-slate-400">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Gestión de usuarios</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Sistema seguro</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <span>Interfaz moderna</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                <span>Tiempo real</span>
              </div>
            </div>
          </div>
        </Card>
        
        {/* Footer mejorado */}
        <div className="text-center mt-8 space-y-2">
          <p className="text-slate-500 text-sm">
            © 2025 Nexo PPEAM. Sistema de gestión integral para congregaciones.
          </p>
          <div className="flex justify-center gap-4 text-xs text-slate-600">
            <span>Versión 2.0</span>
            <span>•</span>
            <span>Arquitectura moderna</span>
            <span>•</span>
            <span>React + FastAPI</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Añadir estilos CSS personalizados para animaciones
const customStyles = `
  @keyframes spin-slow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @keyframes fade-in {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .animate-spin-slow {
    animation: spin-slow 8s linear infinite;
  }
  
  .animate-fade-in {
    animation: fade-in 1s ease-out;
  }
`;

// Inyectar estilos si no existen
if (typeof window !== 'undefined' && !document.getElementById('login-page-styles')) {
  const style = document.createElement('style');
  style.id = 'login-page-styles';
  style.textContent = customStyles;
  document.head.appendChild(style);
}