import { useNavigate } from 'react-router-dom';

interface NavbarProps {
  title?: string;
}

export default function Navbar({ title = 'Nexo PPEAM' }: NavbarProps) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav className="bg-[#111827] flex justify-between items-center px-6 py-4 border-b border-[#1e293b] shadow">
      <h1 className="text-2xl font-bold text-slate-200">{title}</h1>
      <button onClick={handleLogout} className="px-4 py-2 bg-red-600 hover:bg-red-500 text-sm font-medium text-white rounded-lg transition">Cerrar sesión</button>
    </nav>
  );
}
