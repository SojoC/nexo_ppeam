import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import UsersPage from './pages/UsersPage';
import UserRegister from './pages/UserRegister';
import { LoginPage as NewLoginPage } from './components/LoginPage';
import { Button } from './components/ui';

// Componente de navegación mejorado
function Navigation() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav className="bg-[#111827] border-b border-[#1f2937] p-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex gap-6">
          <Link to="/" className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Nexo PPEAM
          </Link>
          <div className="flex gap-4">
            <Link to="/register" className="hover:text-indigo-400 transition-colors">
              Registro de Usuarios
            </Link>
            <Link to="/users" className="hover:text-indigo-400 transition-colors">
              Gestión CRUD
            </Link>
            <Link to="/auth-demo" className="hover:text-indigo-400 transition-colors">
              Demo Auth v2
            </Link>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              <span className="text-sm text-slate-400">
                Hola, {(user as any)?.firstName || 'Usuario'}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={logout}
              >
                Cerrar Sesión
              </Button>
            </>
          ) : (
            <Link to="/auth-demo">
              <Button variant="primary" size="sm">
                Iniciar Sesión v2
              </Button>
            </Link>
          )}
          
          <div className="text-sm text-slate-400">
            Sistema de Gestión de Congregación
          </div>
        </div>
      </div>
    </nav>
  );
}

// Dashboard mejorado para usuarios autenticados
function Dashboard() {
  const { user } = useAuth();

  return (
    <div className="p-8 text-center max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
        Bienvenido, {user?.firstName}!
      </h1>
      <p className="text-slate-400 mb-8">
        Sistema integral de gestión para congregaciones con autenticación avanzada.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/register"
          className="p-6 bg-[#111827] border border-[#1f2937] rounded-xl hover:border-indigo-500 transition-colors"
        >
          <h3 className="text-xl font-semibold mb-2">📋 Registro de Usuarios</h3>
          <p className="text-slate-400">
            Sistema completo de CRUD para gestionar información de miembros
          </p>
        </Link>
        
        <Link
          to="/users"
          className="p-6 bg-[#111827] border border-[#1f2937] rounded-xl hover:border-indigo-500 transition-colors"
        >
          <h3 className="text-xl font-semibold mb-2">👥 Gestión CRUD</h3>
          <p className="text-slate-400">
            Interfaz original de gestión de usuarios
          </p>
        </Link>
        
        <div className="p-6 bg-[#111827] border border-green-500/30 rounded-xl">
          <h3 className="text-xl font-semibold mb-2 text-green-400">✅ Auth v2 Activo</h3>
          <p className="text-slate-400">
            Sistema de autenticación mejorado con hooks y contexto
          </p>
        </div>
      </div>
      
      {/* Información del usuario */}
      <div className="mt-8 p-6 bg-[#111827] border border-[#1f2937] rounded-xl">
        <h3 className="text-lg font-semibold mb-4 text-slate-200">Tu Información</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
          <div>
            <span className="text-slate-400">Email:</span>
            <span className="ml-2 text-slate-200">{user?.email}</span>
          </div>
          <div>
            <span className="text-slate-400">Nombre:</span>
            <span className="ml-2 text-slate-200">{user?.firstName} {user?.lastName}</span>
          </div>
          <div>
            <span className="text-slate-400">Estado:</span>
            <span className={`ml-2 ${user?.isActive ? 'text-green-400' : 'text-red-400'}`}>
              {user?.isActive ? 'Activo' : 'Inactivo'}
            </span>
          </div>
          <div>
            <span className="text-slate-400">Miembro desde:</span>
            <span className="ml-2 text-slate-200">
              {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Página de inicio mejorada
function HomePage() {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Dashboard />;
  }

  return (
    <div className="p-8 text-center max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
        Bienvenido a Nexo PPEAM
      </h1>
      <p className="text-slate-400 mb-8">
        Sistema integral de gestión para congregaciones. Administra usuarios, contactos y más.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/register"
          className="p-6 bg-[#111827] border border-[#1f2937] rounded-xl hover:border-indigo-500 transition-colors"
        >
          <h3 className="text-xl font-semibold mb-2">📋 Registro de Usuarios</h3>
          <p className="text-slate-400">
            Sistema completo de CRUD para gestionar información de miembros
          </p>
        </Link>
        
        <Link
          to="/users"
          className="p-6 bg-[#111827] border border-[#1f2937] rounded-xl hover:border-indigo-500 transition-colors"
        >
          <h3 className="text-xl font-semibold mb-2">👥 Gestión CRUD</h3>
          <p className="text-slate-400">
            Interfaz original de gestión de usuarios con autenticación
          </p>
        </Link>
        
        <Link
          to="/auth-demo"
          className="p-6 bg-[#111827] border border-purple-500/30 rounded-xl hover:border-purple-500 transition-colors"
        >
          <h3 className="text-xl font-semibold mb-2">� Sistema Auth v2</h3>
          <p className="text-slate-400">
            Nueva implementación con hooks, contexto y arquitectura limpia
          </p>
        </Link>
      </div>
    </div>
  );
}

// Componente principal con autenticación
function AppContent() {
  // Función de compatibilidad con el sistema anterior
  const isLegacyAuthenticated = () => {
    return !!localStorage.getItem('token') || !!localStorage.getItem('access_token');
  };

  return (
    <div className="min-h-screen bg-[#0b0f1a] text-slate-200">
      <Navigation />
      
      <Routes>
        {/* Nueva ruta de autenticación v2 */}
        <Route
          path="/auth-demo"
          element={<NewLoginPage />}
        />
        
        {/* Rutas originales con compatibilidad */}
        <Route
          path="/login"
          element={
            isLegacyAuthenticated() ? <Navigate to="/users" replace /> : <LoginPage />
          }
        />
        <Route
          path="/users"
          element={
            isLegacyAuthenticated() ? <UsersPage /> : <Navigate to="/login" replace />
          }
        />
        <Route
          path="/register"
          element={<UserRegister />}
        />
        
        {/* Página de inicio mejorada */}
        <Route path="/" element={<HomePage />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
