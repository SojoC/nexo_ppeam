// ==========================
// UserRegister — Página principal del sistema de registro de usuarios
// - Arquitectura limpia con componentes modulares
// - Separación de responsabilidades usando custom hooks
// - Diseño moderno responsive con grid layout
// ==========================


import { useUsersRegister } from "../hooks/useUsersRegister";
import RegisterForm from "../components/RegisterForm";
import RegisteredUsersTable from "../components/RegisteredUsersTable";
import { FeedbackAlert } from "../components/FeedbackAlert";
import type { RegisterFormData } from "../components/RegisterForm";

export default function UserRegister() {
  // -------------------- HOOKS --------------------
  const {
    users,
    loading,
    message,
    messageType,
    formData,
    selectedId,
    isEditing,

    createNewUser,
    updateUser,
    deleteUser,
    selectUserForEdit,
    clearForm,
    clearMessage,
    updateFormField,
  } = useUsersRegister();

  // -------------------- HANDLERS --------------------
  
  // Maneja cambios en los campos del formulario
  const handleFormChange = (field: keyof RegisterFormData, value: string | number | null) => {
    updateFormField(field, value);
  };

  // Maneja envío del formulario (crear o actualizar)
  const handleFormSubmit = async () => {
    if (isEditing && selectedId) {
      await updateUser(selectedId, formData);
    } else {
      await createNewUser(formData);
    }
  };

  // Maneja selección de usuario para editar desde la tabla
  const handleUserEdit = (user: Parameters<typeof selectUserForEdit>[0]) => {
    selectUserForEdit(user);
  };

  // Maneja eliminación de usuario desde la tabla
  const handleUserDelete = async (userId: string) => {
    await deleteUser(userId);
  };

  // -------------------- RENDER --------------------
  return (
    <div className="min-h-screen bg-[#0b0f1a] text-slate-200">
      {/* Mensaje de feedback (toast flotante) */}
      <FeedbackAlert
        message={message}
        type={messageType}
        onClose={clearMessage}
      />

      {/* Layout principal con sidebar moderno */}
      <div className="lg:grid lg:grid-cols-3 lg:gap-0 min-h-screen">
        
        {/* Sidebar izquierdo - Formulario de registro */}
        <div className="lg:col-span-1 bg-[#0f172a] border-r border-[#223048]">
          <div className="h-full flex flex-col">
            
            {/* Header del sidebar */}
            <header className="p-6 border-b border-[#223048]">
              <h2 className="text-xl font-semibold text-slate-200 mb-1">
                {isEditing ? "Editar Usuario" : "Registrar Usuario"}
              </h2>
              <p className="text-sm text-slate-400">
                Gestiona la información de los miembros
              </p>
            </header>

            {/* Formulario scrollable */}
            <div className="flex-1 overflow-y-auto p-6">
              <RegisterForm
                formData={formData}
                onChange={handleFormChange}
                onSubmit={handleFormSubmit}
                onClear={clearForm}
                isEditing={isEditing}
                selectedId={selectedId}
              />
            </div>
          </div>
        </div>

        {/* Área principal - Tabla de usuarios */}
        <div className="lg:col-span-2 flex flex-col">
          
          {/* Top navigation bar */}
          <header className="bg-[#0f172a] border-b border-[#223048] p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-slate-200 mb-1">
                  Sistema de Usuarios
                </h1>
                <p className="text-sm text-slate-400">
                  Total de registros: {users.length}
                </p>
              </div>
              
              {/* Estadísticas rápidas */}
              <div className="flex gap-4">
                <div className="text-center">
                  <div className="text-lg font-semibold text-indigo-400">
                    {users.filter(u => u.privilegio).length}
                  </div>
                  <div className="text-xs text-slate-500">Con privilegio</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-green-400">
                    {users.filter(u => u.fecha_bautismo).length}
                  </div>
                  <div className="text-xs text-slate-500">Bautizados</div>
                </div>
              </div>
            </div>
          </header>

          {/* Contenido principal scrollable */}
          <main className="flex-1 overflow-y-auto p-6 bg-[#0b0f1a]">
            <RegisteredUsersTable
              users={users}
              loading={loading}
              onEdit={handleUserEdit}
              onDelete={handleUserDelete}
            />
          </main>
        </div>
      </div>
    </div>
  );
}