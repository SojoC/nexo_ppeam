// Página: Registro de Usuario (oscura, moderna) with CRUD.
// - Muestra un formulario con todas las columnas pedidas.
// - Lista usuarios existentes y permite seleccionar uno para editar.
// - Comentarios muy detallados para entender cada línea.

import { useEffect, useState } from "react";
import {
  createUser,
  listUsers,
  updateUser,
  deleteUser,
  getErrorMessage,
  type UserPayload,
  type User,
} from "../lib/api";

export default function UserRegister() {
  // -------------------- ESTADO --------------------
  // Lista de usuarios que trae el backend
  const [users, setUsers] = useState<User[]>([]);
  // Formulario controlado: guarda los valores que el usuario escribe
  const [form, setForm] = useState<UserPayload>({
    nombre: "",
    edad: undefined,
    fecha_nacimiento: "",
    sexo: "",
    estado_civil: "",
    fecha_bautismo: "",
    privilegio: "",
    telefono: "",
    congregacion: "",
    ciudad: "",
    email: "",
  });
  // ID del usuario seleccionado (para modo edición)
  const [selectedId, setSelectedId] = useState<string | null>(null);
  // Mensaje de feedback (éxito/error/información)
  const [msg, setMsg] = useState<string>("");
  // Estado de carga para deshabilitar botones durante operaciones
  const [loading, setLoading] = useState<boolean>(false);

  // -------------------- EFECTOS --------------------
  // Al cargar la página, obtener la lista inicial de usuarios
  useEffect(() => {
    loadUsers();
  }, []);

  // Función helper para cargar usuarios y manejar errores
  const loadUsers = async () => {
    try {
      const data = await listUsers();
      setUsers(data);
    } catch (error) {
      setMsg(`❌ Error al cargar usuarios: ${getErrorMessage(error)}`);
    }
  };

  // -------------------- HANDLERS --------------------
  // Maneja cambios de cualquier input del formulario
  const onChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;

    // Si el campo es "edad", convertimos a número cuando corresponda
    if (name === "edad") {
      setForm((f) => ({ ...f, edad: value ? Number(value) : undefined }));
      return;
    }
    setForm((f) => ({ ...f, [name]: value }));
  };

  // Limpia el formulario a los valores por defecto
  const clearForm = () => {
    setSelectedId(null);
    setForm({
      nombre: "",
      edad: undefined,
      fecha_nacimiento: "",
      sexo: "",
      estado_civil: "",
      fecha_bautismo: "",
      privilegio: "",
      telefono: "",
      congregacion: "",
      ciudad: "",
      email: "",
    });
    setMsg("");
  };

  // Agregar (CREATE)
  const handleAdd = async () => {
    if (!form.nombre.trim()) {
      setMsg("⚠️ El nombre es obligatorio");
      return;
    }

    setLoading(true);
    try {
      const created = await createUser(form);
      setMsg(`✅ Usuario creado: ${created.nombre} (ID: ${created.id})`);
      await loadUsers(); // Refrescar lista
      clearForm();
    } catch (error) {
      setMsg(`❌ Error al crear usuario: ${getErrorMessage(error)}`);
    } finally {
      setLoading(false);
    }
  };

  // Editar (UPDATE)
  const handleEdit = async () => {
    if (!selectedId) {
      setMsg("ℹ️ Selecciona un usuario para editar.");
      return;
    }
    if (!form.nombre.trim()) {
      setMsg("⚠️ El nombre es obligatorio");
      return;
    }

    setLoading(true);
    try {
      const updated = await updateUser(selectedId, form);
      setMsg(`✏️ Usuario actualizado: ${updated.nombre} (ID: ${updated.id})`);
      await loadUsers(); // Refrescar lista
      clearForm();
    } catch (error) {
      setMsg(`❌ Error al actualizar usuario: ${getErrorMessage(error)}`);
    } finally {
      setLoading(false);
    }
  };

  // Eliminar (DELETE)
  const handleDelete = async () => {
    if (!selectedId) {
      setMsg("ℹ️ Selecciona un usuario para eliminar.");
      return;
    }

    const confirmDelete = confirm(
      "¿Estás seguro de eliminar este usuario? Esta acción no se puede deshacer."
    );
    if (!confirmDelete) return;

    setLoading(true);
    try {
      await deleteUser(selectedId);
      setMsg(`🗑️ Usuario eliminado correctamente`);
      await loadUsers(); // Refrescar lista
      clearForm();
    } catch (error) {
      setMsg(`❌ Error al eliminar usuario: ${getErrorMessage(error)}`);
    } finally {
      setLoading(false);
    }
  };

  // Seleccionar para edición: carga datos al formulario
  const selectForEdit = (u: User) => {
    setSelectedId(u.id);
    // Copiamos sólo los campos del formulario (sin el id)
    setForm({
      nombre: u.nombre || "",
      edad: u.edad ?? undefined,
      fecha_nacimiento: u.fecha_nacimiento || "",
      sexo: u.sexo || "",
      estado_civil: u.estado_civil || "",
      fecha_bautismo: u.fecha_bautismo || "",
      privilegio: u.privilegio || "",
      telefono: u.telefono || "",
      congregacion: u.congregacion || "",
      ciudad: u.ciudad || "",
      email: u.email || "",
    });
    setMsg(`📝 Usuario seleccionado para edición: ${u.nombre}`);
  };

  // -------------------- UI --------------------
  return (
    <div className="min-h-screen bg-[#0b0f1a] text-slate-200 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Encabezado */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Sistema de Registro de Usuarios
          </h1>
          <p className="text-slate-400">
            Gestiona la información completa de los miembros de la congregación
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Formulario - 2/3 del ancho en pantallas grandes */}
          <div className="xl:col-span-2">
            <div className="bg-[#111827] rounded-2xl p-8 shadow-2xl border border-[#1f2937]">
              <h2 className="text-2xl font-semibold mb-6 flex items-center gap-3">
                <span className="p-2 bg-indigo-600 rounded-lg">📋</span>
                {selectedId ? "Editar Usuario" : "Nuevo Usuario"}
              </h2>

              {/* GRID de campos: 2 columnas en pantallas grandes */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Nombre */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Nombre Completo <span className="text-red-400">*</span>
                  </label>
                  <input
                    name="nombre"
                    value={form.nombre || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                    placeholder="Ej: Carlos Alberto Sojo"
                    required
                  />
                </div>

                {/* Edad */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Edad
                  </label>
                  <input
                    name="edad"
                    type="number"
                    min="0"
                    max="120"
                    value={form.edad ?? ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                    placeholder="Ej: 35"
                  />
                </div>

                {/* Fecha de nacimiento */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Fecha de Nacimiento
                  </label>
                  <input
                    name="fecha_nacimiento"
                    type="date"
                    value={form.fecha_nacimiento || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                  />
                </div>

                {/* Sexo */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Sexo
                  </label>
                  <select
                    name="sexo"
                    value={form.sexo || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                  >
                    <option value="">Seleccione…</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>

                {/* Estado civil */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Estado Civil
                  </label>
                  <select
                    name="estado_civil"
                    value={form.estado_civil || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                  >
                    <option value="">Seleccione…</option>
                    <option value="soltero">Soltero(a)</option>
                    <option value="casado">Casado(a)</option>
                    <option value="divorciado">Divorciado(a)</option>
                    <option value="viudo">Viudo(a)</option>
                  </select>
                </div>

                {/* Fecha bautismo */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Fecha de Bautismo
                  </label>
                  <input
                    name="fecha_bautismo"
                    type="date"
                    value={form.fecha_bautismo || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                  />
                </div>

                {/* Privilegio */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Privilegio de Servicio
                  </label>
                  <select
                    name="privilegio"
                    value={form.privilegio || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                  >
                    <option value="">Seleccione…</option>
                    <option value="Publicador">Publicador</option>
                    <option value="Precursor Auxiliar">Precursor Auxiliar</option>
                    <option value="Precursor Regular">Precursor Regular</option>
                    <option value="Siervo Ministerial">Siervo Ministerial</option>
                    <option value="Anciano">Anciano</option>
                  </select>
                </div>

                {/* Teléfono */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Teléfono
                  </label>
                  <input
                    name="telefono"
                    type="tel"
                    value={form.telefono || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                    placeholder="+58 412 123 4567"
                  />
                </div>

                {/* Congregación */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Congregación
                  </label>
                  <input
                    name="congregacion"
                    value={form.congregacion || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                    placeholder="Ej: Monagas 1"
                  />
                </div>

                {/* Ciudad */}
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Ciudad
                  </label>
                  <input
                    name="ciudad"
                    value={form.ciudad || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                    placeholder="Ej: Maturín"
                  />
                </div>

                {/* Email */}
                <div className="lg:col-span-2">
                  <label className="block text-sm font-medium mb-2 text-slate-300">
                    Correo Electrónico
                  </label>
                  <input
                    name="email"
                    type="email"
                    value={form.email || ""}
                    onChange={onChange}
                    className="w-full bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-colors"
                    placeholder="ejemplo@correo.com"
                  />
                </div>
              </div>

              {/* Botonera CRUD */}
              <div className="mt-8 flex flex-wrap gap-4">
                <button
                  onClick={handleAdd}
                  disabled={loading}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[.98] transition-all font-medium"
                >
                  <span>➕</span>
                  {loading ? "Creando..." : "Agregar Usuario"}
                </button>
                <button
                  onClick={handleEdit}
                  disabled={loading}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-yellow-600 hover:bg-yellow-500 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[.98] transition-all font-medium"
                >
                  <span>✏️</span>
                  {loading ? "Actualizando..." : "Actualizar"}
                </button>
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[.98] transition-all font-medium"
                >
                  <span>🗑️</span>
                  {loading ? "Eliminando..." : "Eliminar"}
                </button>
                <button
                  onClick={clearForm}
                  disabled={loading}
                  className="flex items-center gap-2 px-6 py-3 rounded-xl border border-slate-500 hover:bg-[#0f172a] disabled:opacity-50 transition-all font-medium"
                >
                  <span>🧹</span>
                  Limpiar
                </button>
              </div>

              {/* Estado selección */}
              <div className="mt-4 text-sm text-slate-400 bg-[#0f172a] border border-[#334155] rounded-xl px-4 py-2">
                {selectedId ? (
                  <span className="text-yellow-400">📝 Modo edición - ID: {selectedId}</span>
                ) : (
                  <span className="text-green-400">➕ Modo creación - Nuevo usuario</span>
                )}
              </div>
            </div>
          </div>

          {/* Lista de usuarios - 1/3 del ancho */}
          <div className="xl:col-span-1">
            <div className="bg-[#111827] rounded-2xl p-6 shadow-2xl border border-[#1f2937] h-fit">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <span className="p-1.5 bg-purple-600 rounded-lg">👥</span>
                  Usuarios ({users.length})
                </h2>
                <button
                  onClick={loadUsers}
                  disabled={loading}
                  className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                  title="Refrescar lista"
                >
                  🔄
                </button>
              </div>

              {users.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">👤</div>
                  <div className="text-slate-400 text-sm">No hay usuarios registrados aún.</div>
                  <div className="text-slate-500 text-xs mt-1">
                    Crea el primer usuario usando el formulario.
                  </div>
                </div>
              ) : (
                <div className="space-y-3 max-h-[70vh] overflow-y-auto">
                  {users.map((u) => (
                    <div
                      key={u.id}
                      className={`p-4 rounded-xl border transition-all cursor-pointer hover:shadow-lg ${
                        selectedId === u.id
                          ? "bg-indigo-900/30 border-indigo-500 shadow-indigo-500/20"
                          : "bg-[#0f172a] border-[#334155] hover:border-[#475569]"
                      }`}
                      onClick={() => selectForEdit(u)}
                    >
                      <div className="font-semibold text-sm mb-1">
                        {u.nombre || "(Sin nombre)"}
                      </div>
                      <div className="text-xs text-slate-400 space-y-1">
                        {u.email && (
                          <div className="flex items-center gap-1">
                            <span>📧</span>
                            <span>{u.email}</span>
                          </div>
                        )}
                        {u.telefono && (
                          <div className="flex items-center gap-1">
                            <span>📱</span>
                            <span>{u.telefono}</span>
                          </div>
                        )}
                        {u.congregacion && (
                          <div className="flex items-center gap-1">
                            <span>🏛️</span>
                            <span>{u.congregacion}</span>
                          </div>
                        )}
                        {u.privilegio && (
                          <div className="flex items-center gap-1">
                            <span>⭐</span>
                            <span className="text-yellow-400">{u.privilegio}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Mensajes de feedback */}
        {msg && (
          <div className="mt-6 max-w-4xl mx-auto">
            <div className="bg-[#111827] border border-[#334155] rounded-xl px-6 py-4 shadow-lg">
              <div className="text-sm leading-relaxed">{msg}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}