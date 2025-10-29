import React, { useMemo, useState } from "react";
import { useUsersRegister } from "../hooks/useUsersRegister";
import { FeedbackAlert } from "../components/FeedbackAlert";

// ==========================
// UserRegisterModern — Layout profesional de 3 columnas exacto al modelo
// - Sidebar de acciones (1/3) + Formulario y tabla (2/3)  
// - Estilo oscuro moderno que aprovecha el espacio horizontal
// - Conectado al sistema real de backend con useUsersRegister
// ==========================

const civil = ["soltero", "casado", "divorciado", "viudo"] as const;

function SectionCard({ title, children, actions }: { title: string; children: React.ReactNode; actions?: React.ReactNode }) {
  return (
    // Card container: fondo oscuro, borde sutil y bordes redondeados
    <section className="bg-[#0f172a] border border-[#223048] rounded-2xl shadow-sm">
      {/* Header con título y acciones pequeñas */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-[#223048]">
        <h3 className="text-slate-200 font-semibold tracking-tight">{title}</h3>
        {actions}
      </header>
      {/* Cuerpo del card con padding consistente */}
      <div className="p-6">{children}</div>
    </section>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1">{children}</label>;
}

function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={[
        // ancho completo con esquinas suaves
        "w-full rounded-xl px-3 py-2 text-sm",
        // fondo ligeramente más claro que el fondo principal para contraste
        "bg-[#0b1222] border border-[#2a3b5f] text-slate-200",
        // color del placeholder y estilos de focus accesibles
        "placeholder:text-slate-500",
        "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
        props.className || "",
      ].join(" ")}
    />
  );
}

function Select({ children, ...rest }: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...rest}
      className={[
        "w-full rounded-xl px-3 py-2 text-sm",
        "bg-[#0b1222] border border-[#2a3b5f] text-slate-200",
        "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
      ].join(" ")}
    >
      {children}
    </select>
  );
}

function ToolbarButton({ children, onClick, variant = "solid" as const }: { children: React.ReactNode; onClick?: () => void; variant?: "solid" | "ghost" | "danger" | "warn" }) {
  const base = "px-3 py-2 rounded-xl text-sm transition active:scale-[.98]";
  const styles = {
    solid: "bg-indigo-600 hover:bg-indigo-500 text-white",
    ghost: "border border-[#2a3b5f] hover:bg-[#101a31] text-slate-200",
    danger: "bg-red-600 hover:bg-red-500 text-white",
    warn: "bg-amber-600 hover:bg-amber-500 text-white",
  }[variant];
  return (
    <button onClick={onClick} className={`${base} ${styles}`}>
      {children}
    </button>
  );
}

export default function UserRegisterModern() {
  const {
    users,
    loading,
    message,
    messageType,
    formData,
    selectedId,
    createNewUser,
    updateUser,
    deleteUser,
    selectUserForEdit,
    clearForm,
    clearMessage,
    updateFormField,
  } = useUsersRegister();

  // Texto de búsqueda para filtrar la tabla
  const [searchQuery, setSearchQuery] = useState("");

  // Filtro de búsqueda simple
  const filtered = useMemo(() => {
    const term = searchQuery.trim().toLowerCase();
    if (!term) return users;
    return users.filter((u) =>
      [u.nombre, u.email, u.congregacion, u.ciudad]
        .filter(Boolean)
        .some((v) => (v || "").toLowerCase().includes(term))
    );
  }, [searchQuery, users]);

  // Maneja cambios en inputs y selects del formulario. Convierte 'edad' a number cuando aplica.
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    const parsed = name === "edad" && value ? Number(value) : value;
    updateFormField(name as keyof typeof formData, parsed);
  };

  // Agregar nuevo usuario: delega al hook useUsersRegister
  const handleAdd = async () => {
    await createNewUser(formData);
  };

  // Actualizar usuario seleccionado
  const handleEdit = async () => {
    if (!selectedId) return;
    await updateUser(selectedId, formData);
  };

  // Eliminar usuario seleccionado (llama al repositorio)
  const handleDelete = async () => {
    if (!selectedId) return;
    await deleteUser(selectedId);
  };

  // Cargar datos del usuario en el formulario para editar
  const selectForEdit = (u: typeof users[0]) => {
    selectUserForEdit(u);
  };

  // Página completa: fondo oscuro y texto claro
  return (
    <div className="min-h-screen bg-[#0b0f1a] text-slate-200">
      {/* Mensaje de feedback (toast flotante) */}
      <FeedbackAlert
        message={message}
        type={messageType}
        onClose={clearMessage}
      />

      {/* Top bar */}
      {/* Barra superior con título y acciones globales */}
      <header className="border-b border-[#20304d] bg-[#0c1220]/80 backdrop-blur supports-[backdrop-filter]:bg-[#0c1220]/60">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold tracking-tight">Sistema de Registro de Usuarios</h1>
          <div className="hidden md:flex items-center gap-3">
            <Input placeholder="Buscar por nombre, email…" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            <ToolbarButton variant="ghost">Exportar</ToolbarButton>
          </div>
        </div>
      </header>

      {/* Main layout */}
  {/* Layout principal con 3 columnas en pantallas grandes */}
  <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Columna izquierda: acciones (sticky) */}
  {/* Sidebar izquierdo: acciones y resumen (sticky) */}
  <div className="lg:col-span-1 h-max lg:sticky lg:top-6 space-y-6">
          <SectionCard
            title="Acciones"
            actions={
              <span className="text-xs text-slate-400">{selectedId ? `Editando: ${selectedId}` : "Nuevo registro"}</span>
            }
          >
            <div className="grid grid-cols-2 gap-3">
              <ToolbarButton onClick={handleAdd}>Agregar</ToolbarButton>
              <ToolbarButton onClick={handleEdit} variant="warn">
                Editar
              </ToolbarButton>
              <ToolbarButton onClick={handleDelete} variant="danger">
                Eliminar
              </ToolbarButton>
              <ToolbarButton onClick={clearForm} variant="ghost">
                Limpiar
              </ToolbarButton>
            </div>
            <div className="mt-4 md:hidden">
              <Label>Buscar</Label>
              <Input placeholder="Nombre, email…" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </div>
          </SectionCard>

          <SectionCard title="Resumen">
            {/* Estadísticas rápidas */}
            <div className="text-sm text-slate-300 grid grid-cols-2 gap-2">
              <div className="opacity-70">Total registros</div>
              <div className="text-right font-medium">{users.length}</div>
              <div className="opacity-70">Filtrados</div>
              <div className="text-right font-medium">{filtered.length}</div>
            </div>
          </SectionCard>
        </div>

        {/* Columna derecha: formulario + tabla (2/3) */}
  {/* Area principal: formulario + tabla */}
  <div className="lg:col-span-2 space-y-6">
          <SectionCard title="Datos Personales">
            {/* Formulario de datos personales dividido en 3 columnas en pantallas grandes */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <Label>Nombre</Label>
                <Input name="nombre" value={formData.nombre} onChange={handleChange} placeholder="Ej: Carlos Sojo" />
              </div>
              <div>
                <Label>Email</Label>
                <Input name="email" type="email" value={formData.email || ""} onChange={handleChange} placeholder="correo@dominio.com" />
              </div>
              <div>
                <Label>Teléfono</Label>
                <Input name="telefono" value={formData.telefono || ""} onChange={handleChange} placeholder="+58 412 000 0000" />
              </div>
              <div>
                <Label>Sexo</Label>
                <Select name="sexo" value={formData.sexo || ""} onChange={handleChange}>
                  <option value="">Seleccione…</option>
                  <option value="masculino">Masculino</option>
                  <option value="femenino">Femenino</option>
                </Select>
              </div>
              <div>
                <Label>Estado civil</Label>
                <Select name="estado_civil" value={formData.estado_civil || ""} onChange={handleChange}>
                  <option value="">Seleccione…</option>
                  {civil.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label>Edad</Label>
                <Input name="edad" type="number" value={formData.edad ?? ""} onChange={handleChange} placeholder="Ej: 35" />
              </div>
              <div>
                <Label>Fecha nacimiento</Label>
                <Input name="fecha_nacimiento" type="date" value={formData.fecha_nacimiento || ""} onChange={handleChange} />
              </div>
            </div>
          </SectionCard>

          <SectionCard title="Datos Congregación / Espirituales">
            {/* Campos relacionados a congregación y datos espirituales */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <Label>Congregación</Label>
                <Input name="congregacion" value={formData.congregacion || ""} onChange={handleChange} placeholder="Monagas 1" />
              </div>
              <div>
                <Label>Ciudad</Label>
                <Input name="ciudad" value={formData.ciudad || ""} onChange={handleChange} placeholder="Maturín" />
              </div>
              <div>
                <Label>Privilegio</Label>
                <Input name="privilegio" value={formData.privilegio || ""} onChange={handleChange} placeholder="Publicador / SM / Anciano" />
              </div>
              <div>
                <Label>Fecha bautismo</Label>
                <Input name="fecha_bautismo" type="date" value={formData.fecha_bautismo || ""} onChange={handleChange} />
              </div>
            </div>
          </SectionCard>

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
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="text-center py-8 text-slate-400">
                        Cargando usuarios...
                      </td>
                    </tr>
                  ) : filtered.length === 0 ? (
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
                            <ToolbarButton variant="ghost" onClick={() => selectForEdit(u)}>Editar</ToolbarButton>
                            <ToolbarButton variant="danger" onClick={() => { selectForEdit(u); handleDelete(); }}>Eliminar</ToolbarButton>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </SectionCard>
        </div>
      </main>
    </div>
  );
}