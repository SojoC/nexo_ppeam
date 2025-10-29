// ==========================
// useUsersRegister — Custom hook para manejo de operaciones CRUD de usuarios
// - Encapsula toda la lógica de estado y operaciones de usuarios del registro
// - Proporciona interface limpia para los componentes
// ==========================

import { useState, useEffect, useCallback } from "react";
import {
  createUser,
  listUsers,
  updateUser,
  deleteUser,
  getErrorMessage,
  type UserPayload,
  type User,
} from "../lib/api";

export type { User, UserPayload };

type MessageType = "success" | "error" | "info";

interface UseUsersRegisterReturn {
  users: User[];
  loading: boolean;
  message: string;
  messageType: MessageType;
  formData: UserPayload;
  selectedId: string | null;
  isEditing: boolean;
  
  // Actions
  loadUsers: () => Promise<void>;
  createNewUser: (userData: UserPayload) => Promise<void>;
  updateUser: (userId: string, userData: UserPayload) => Promise<void>;
  deleteUser: (userId: string) => Promise<void>;
  selectUserForEdit: (user: User) => void;
  clearForm: () => void;
  clearMessage: () => void;
  updateFormField: (field: keyof UserPayload, value: string | number | null) => void;
}

const initialFormState: UserPayload = {
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
};

export function useUsersRegister(): UseUsersRegisterReturn {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string>("");
  const [messageType, setMessageType] = useState<MessageType>("info");
  const [formData, setFormData] = useState<UserPayload>(initialFormState);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Derived state
  const isEditing = Boolean(selectedId);

  // Helper function to show messages
  const showMessage = (msg: string, type: MessageType = "info") => {
    setMessage(msg);
    setMessageType(type);
  };

  const clearMessage = () => {
    setMessage("");
  };

  // Load users from API
  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await listUsers();
      setUsers(data);
    } catch (error) {
      showMessage(`Error al cargar usuarios: ${getErrorMessage(error)}`, "error");
    } finally {
      setLoading(false);
    }
  }, []);

  // Create new user
  const createNewUser = async (userData: UserPayload) => {
    if (!userData.nombre.trim()) {
      showMessage("El nombre es obligatorio", "error");
      return;
    }

    try {
      setLoading(true);
      const created = await createUser(userData);
      showMessage(`Usuario creado: ${created.nombre}`, "success");
      await loadUsers();
      clearForm();
    } catch (error) {
      showMessage(`Error al crear usuario: ${getErrorMessage(error)}`, "error");
    } finally {
      setLoading(false);
    }
  };

  // Update existing user
  const updateExistingUser = async (userId: string, userData: UserPayload) => {
    if (!userData.nombre.trim()) {
      showMessage("El nombre es obligatorio", "error");
      return;
    }

    try {
      setLoading(true);
      const updated = await updateUser(userId, userData);
      showMessage(`Usuario actualizado: ${updated.nombre}`, "success");
      await loadUsers();
      clearForm();
    } catch (error) {
      showMessage(`Error al actualizar usuario: ${getErrorMessage(error)}`, "error");
    } finally {
      setLoading(false);
    }
  };

  // Delete user
  const deleteExistingUser = async (userId: string) => {
    try {
      setLoading(true);
      await deleteUser(userId);
      showMessage("Usuario eliminado correctamente", "success");
      await loadUsers();
      clearForm();
    } catch (error) {
      showMessage(`Error al eliminar usuario: ${getErrorMessage(error)}`, "error");
    } finally {
      setLoading(false);
    }
  };

  // Select user for editing
  const selectUserForEdit = (user: User) => {
    setSelectedId(user.id);
    setFormData({
      nombre: user.nombre || "",
      edad: user.edad ?? undefined,
      fecha_nacimiento: user.fecha_nacimiento || "",
      sexo: user.sexo || "",
      estado_civil: user.estado_civil || "",
      fecha_bautismo: user.fecha_bautismo || "",
      privilegio: user.privilegio || "",
      telefono: user.telefono || "",
      congregacion: user.congregacion || "",
      ciudad: user.ciudad || "",
      email: user.email || "",
    });
    showMessage(`Usuario seleccionado para edición: ${user.nombre}`, "info");
  };

  // Clear form and selection
  const clearForm = () => {
    setSelectedId(null);
    setFormData(initialFormState);
    clearMessage();
  };

  // Update form field
  const updateFormField = (field: keyof UserPayload, value: string | number | null) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // Load users on mount
  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  return {
    users,
    loading,
    message,
    messageType,
    formData,
    selectedId,
    isEditing,
    
    // Actions
    loadUsers,
    createNewUser,
    updateUser: updateExistingUser,
    deleteUser: deleteExistingUser,
    selectUserForEdit,
    clearForm,
    clearMessage,
    updateFormField,
  };
}