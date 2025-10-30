// ==========================
// UserRegister — Página principal del sistema de registro de usuarios
// - Arquitectura limpia con componentes modulares
// - Separación de responsabilidades usando custom hooks
// - Diseño moderno responsive con grid layout
// ==========================


import { useUsersRegister } from "../hooks/useUsersRegister";
import RegisterForm from "../components/RegisterForm";
import RegisteredUsersTable from "../components/RegisteredUsersTable";
import FeedbackAlert from "../components/FeedbackAlert";
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
    <div className="min-h-screen bg-[#0b0f1a] text-slate-200 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Encabezado */}
        <header className="text-center">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Sistema de Registro de Usuarios
          </h1>
          <p className="text-slate-400">
            Gestiona la información completa de los miembros de la congregación
          </p>
        </header>

        {/* Mensaje de feedback */}
        {message && (
          <FeedbackAlert
            type={messageType}
            message={message}
            onClose={clearMessage}
            autoClose
            duration={5000}
          />
        )}

        {/* Layout principal con grid responsive */}
        <div className="grid grid-cols-1 xl:grid-cols-5 gap-8">
          
          {/* Formulario de registro - ocupa 3 columnas */}
          <div className="xl:col-span-3">
            <RegisterForm
              formData={formData}
              onChange={handleFormChange}
              onSubmit={handleFormSubmit}
              onClear={clearForm}
              isEditing={isEditing}
              selectedId={selectedId}
            />
          </div>

          {/* Tabla de usuarios - ocupa 2 columnas */}
          <div className="xl:col-span-2">
            <RegisteredUsersTable
              users={users}
              loading={loading}
              onEdit={handleUserEdit}
              onDelete={handleUserDelete}
            />
          </div>
        </div>
      </div>
    </div>
  );
}