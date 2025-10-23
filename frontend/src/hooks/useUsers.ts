import { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';
import type { User } from '../types';

interface UserFormData {
  name: string;
  email: string;
  age: number;
  phone: string;
  tags: string;
}

export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const loadUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await usersAPI.getAll();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar usuarios');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const createUser = async (data: UserFormData) => {
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await usersAPI.create(data);
      setSuccess('Usuario creado exitosamente');
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al crear usuario');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateUser = async (id: string, data: UserFormData) => {
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await usersAPI.update(id, data);
      setSuccess('Usuario actualizado exitosamente');
      setEditingUser(null);
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al actualizar usuario');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (id: string) => {
    if (!confirm('¿Estás seguro de eliminar este usuario?')) return;
    
    setError('');
    setSuccess('');
    try {
      await usersAPI.delete(id);
      setSuccess('Usuario eliminado exitosamente');
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al eliminar usuario');
    }
  };

  const startEdit = (user: User) => {
    setEditingUser(user);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const cancelEdit = () => {
    setEditingUser(null);
  };

  return {
    users,
    loading,
    error,
    success,
    editingUser,
    loadUsers,
    createUser,
    updateUser,
    deleteUser,
    startEdit,
    cancelEdit,
  };
}
