import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import UsersPage from './pages/UsersPage';
import UserRegister from './pages/UserRegister';

function App() {
  const isAuthenticated = () => {
    return !!localStorage.getItem('token') || !!localStorage.getItem('access_token');
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#0b0f1a] text-slate-200">
        {/* Navegación principal */}
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
              </div>
            </div>
            <div className="text-sm text-slate-400">
              Sistema de Gestión de Congregación
            </div>
          </div>
        </nav>

        {/* Rutas */}
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated() ? <Navigate to="/users" replace /> : <LoginPage />
            }
          />
          <Route
            path="/users"
            element={
              isAuthenticated() ? <UsersPage /> : <Navigate to="/login" replace />
            }
          />
          <Route
            path="/register"
            element={<UserRegister />}
          />
          <Route
            path="/"
            element={
              <div className="p-8 text-center max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                  Bienvenido a Nexo PPEAM
                </h1>
                <p className="text-slate-400 mb-8">
                  Sistema integral de gestión para congregaciones. Administra usuarios, contactos y más.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                </div>
              </div>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
