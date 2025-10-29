import React from "react";

// ==========================
// RegisteredUsersTable — Tabla moderna con diseño responsivo profesional
// - Estilo moderno con border-separate y spacing optimizado
// - Layout adaptativo: oculta columnas en móviles y muestra info clave
// - Acciones inline con botones estilizados
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
  loading?: boolean;
  searchQuery?: string;
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
      <div className="p-5">{children}</div>
    </section>
  );
}

function ToolbarButton({ 
  children, 
  onClick, 
  variant = "ghost" as const
}: { 
  children: React.ReactNode; 
  onClick?: () => void; 
  variant?: "ghost" | "danger";
}) {
  const base = "px-3 py-2 rounded-xl text-sm transition active:scale-[.98]";
  const styles = {
    ghost: "border border-[#2a3b5f] hover:bg-[#101a31] text-slate-200",
    danger: "bg-red-600 hover:bg-red-500 text-white",
  }[variant];
  
  return (
    <button onClick={onClick} className={`${base} ${styles}`}>
      {children}
    </button>
  );
}

export default function RegisteredUsersTable({
  users,
  loading = false,
  searchQuery = "",
  onEdit,
  onDelete
}: RegisteredUsersTableProps) {
  
  // Filtro de búsqueda simple
  const filtered = React.useMemo(() => {
    const term = searchQuery.trim().toLowerCase();
    if (!term) return users;
    return users.filter((u) =>
      [u.nombre, u.email, u.congregacion, u.ciudad]
        .filter(Boolean)
        .some((v) => (v || "").toLowerCase().includes(term))
    );
  }, [searchQuery, users]);

  const handleEdit = (user: User) => {
    onEdit(user);
  };

  const handleDelete = (userId: string, userName: string) => {
    if (window.confirm(`¿Está seguro de eliminar a ${userName}?`)) {
      onDelete(userId);
    }
  };

  if (loading) {
    return (
      <SectionCard
        title="Registros"
        actions={<span className="text-xs text-slate-400">Cargando...</span>}
      >
        <div className="text-center py-8">
          <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          <span className="text-sm text-slate-400">Cargando usuarios...</span>
        </div>
      </SectionCard>
    );
  }

  return (
    <SectionCard
      title="Registros"
      actions={<span className="text-xs text-slate-400">{filtered.length} resultado(s)</span>}
    >
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm border-separate border-spacing-y-2">
          <thead>
            <tr className="text-left text-slate-400">
              <th className="px-3 py-2">Nombre</th>
              <th className="px-3 py-2 hidden md:table-cell">Email</th>
              <th className="px-3 py-2 hidden lg:table-cell">Teléfono</th>
              <th className="px-3 py-2 hidden lg:table-cell">Congregación</th>
              <th className="px-3 py-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center py-8 text-slate-400">
                  {users.length === 0 
                    ? "No hay usuarios registrados aún" 
                    : `No se encontraron resultados para "${searchQuery}"`
                  }
                </td>
              </tr>
            ) : (
              filtered.map((u) => (
                <tr key={u.id} className="bg-[#0f172a] border border-[#223048] hover:bg-[#101a31]">
                  <td className="px-3 py-3 rounded-l-xl">
                    <div className="font-medium text-slate-200">{u.nombre || "(sin nombre)"}</div>
                    <div className="text-slate-400 text-xs lg:hidden">{u.email || "sin email"}</div>
                    <div className="text-slate-500 text-xs lg:hidden">{u.telefono || "sin teléfono"}</div>
                  </td>
                  <td className="px-3 py-3 hidden md:table-cell">{u.email || "-"}</td>
                  <td className="px-3 py-3 hidden lg:table-cell">{u.telefono || "-"}</td>
                  <td className="px-3 py-3 hidden lg:table-cell">{u.congregacion || "-"}</td>
                  <td className="px-3 py-3 rounded-r-xl">
                    <div className="flex gap-2">
                      <ToolbarButton variant="ghost" onClick={() => handleEdit(u)}>
                        Editar
                      </ToolbarButton>
                      <ToolbarButton variant="danger" onClick={() => handleDelete(u.id, u.nombre)}>
                        Eliminar
                      </ToolbarButton>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </SectionCard>
  );
}