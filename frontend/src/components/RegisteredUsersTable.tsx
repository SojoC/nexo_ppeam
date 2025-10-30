import React from "react";

// ==========================
// RegisteredUsersTable — Tabla de usuarios registrados
// - Renderiza lista de usuarios con acciones de edición y eliminación
// - Diseño responsive con scroll horizontal en móviles
// - Manejo de estados de carga y datos vacíos
// ==========================

type User = {
  id: string;
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
};

interface RegisteredUsersTableProps {
  users: User[];
  loading: boolean;
  onEdit: (user: User) => void;
  onDelete: (userId: string) => void;
}

function SectionCard({ 
  title, 
  children, 
  actions 
}: { 
  title: string; 
  children: React.ReactNode; 
  actions?: React.ReactNode 
}) {
  return (
    <section className="bg-[#0f172a] border border-[#223048] rounded-2xl shadow-sm">
      <header className="flex items-center justify-between px-5 py-4 border-b border-[#223048]">
        <h3 className="text-slate-200 font-semibold tracking-tight">{title}</h3>
        {actions}
      </header>
      <div className="p-0">{children}</div>
    </section>
  );
}

function TableButton({ 
  children, 
  onClick, 
  variant = "ghost" as const
}: { 
  children: React.ReactNode; 
  onClick?: () => void; 
  variant?: "ghost" | "danger";
}) {
  const base = "px-2 py-1 rounded-lg text-xs transition active:scale-[.98]";
  const styles = {
    ghost: "border border-[#2a3b5f] hover:bg-[#101a31] text-slate-300",
    danger: "bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-600/30",
  }[variant];
  
  return (
    <button onClick={onClick} className={`${base} ${styles}`}>
      {children}
    </button>
  );
}

function LoadingRow() {
  return (
    <tr className="animate-pulse">
      <td colSpan={8} className="px-6 py-4">
        <div className="flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="ml-2 text-sm text-slate-400">Cargando usuarios...</span>
        </div>
      </td>
    </tr>
  );
}

function EmptyRow() {
  return (
    <tr>
      <td colSpan={8} className="px-6 py-8 text-center">
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 bg-slate-700 rounded-full flex items-center justify-center mb-3">
            <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            </svg>
          </div>
          <h3 className="text-slate-300 font-medium mb-1">No hay usuarios registrados</h3>
          <p className="text-slate-500 text-sm">Comienza agregando el primer usuario</p>
        </div>
      </td>
    </tr>
  );
}

export default function RegisteredUsersTable({
  users,
  loading,
  onEdit,
  onDelete
}: RegisteredUsersTableProps) {
  
  const handleEdit = (user: User) => {
    onEdit(user);
  };

  const handleDelete = (userId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar este usuario?')) {
      onDelete(userId);
    }
  };

  const formatDate = (dateString?: string | null): string => {
    if (!dateString) return "-";
    try {
      return new Date(dateString).toLocaleDateString("es-ES");
    } catch {
      return "-";
    }
  };

  return (
    <SectionCard
      title="Usuarios Registrados"
      actions={
        <span className="text-xs text-slate-400">
          {users.length} usuario{users.length !== 1 ? "s" : ""}
        </span>
      }
    >
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-[#0b1222] border-b border-[#223048]">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Nombre
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Edad
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Sexo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Congregación
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Privilegio
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Fecha Baut.
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#223048]">
            {loading && <LoadingRow />}
            
            {!loading && users.length === 0 && <EmptyRow />}
            
            {!loading && users.map((user) => (
              <tr 
                key={user.id} 
                className="hover:bg-[#0b1222] transition-colors"
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white text-xs font-medium">
                      {user.nombre.charAt(0).toUpperCase()}
                    </div>
                    <div className="ml-3">
                      <div className="text-sm font-medium text-slate-200">
                        {user.nombre}
                      </div>
                      {user.telefono && (
                        <div className="text-xs text-slate-400">
                          {user.telefono}
                        </div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                  {user.email || "-"}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                  {user.edad ?? "-"}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                  {user.sexo || "-"}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-slate-300">
                    {user.congregacion || "-"}
                  </div>
                  {user.ciudad && (
                    <div className="text-xs text-slate-500">
                      {user.ciudad}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {user.privilegio ? (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100/10 text-indigo-400 border border-indigo-500/20">
                      {user.privilegio}
                    </span>
                  ) : (
                    <span className="text-slate-500 text-sm">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                  {formatDate(user.fecha_bautismo)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex space-x-2">
                    <TableButton
                      variant="ghost"
                      onClick={() => handleEdit(user)}
                    >
                      Editar
                    </TableButton>
                    <TableButton
                      variant="danger"
                      onClick={() => handleDelete(user.id)}
                    >
                      Eliminar
                    </TableButton>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}