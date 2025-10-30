import { useCallback, useEffect, useState } from 'react';
import { usersAPI } from '../services/api';
import type { User, UserInput } from '../types';

export function useUsersManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<User | null>(null);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await usersAPI.getAll();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar usuarios');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const createUser = async (input: UserInput) => {
    setLoading(true);
    setError(null);
    try {
      const created = await usersAPI.create(input);
      setUsers(prev => [created, ...prev]);
      return created;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al crear usuario');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateUser = async (id: string, input: UserInput) => {
    setLoading(true);
    setError(null);
    try {
      const updated = await usersAPI.update(id, input);
      setUsers(prev => prev.map(u => (u.id === id ? updated : u)));
      setSelected(null);
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al actualizar usuario');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (id: string) => {
    if (!confirm('¿Estás seguro de eliminar este usuario?')) return;
    setLoading(true);
    setError(null);
    try {
      await usersAPI.delete(id);
      setUsers(prev => prev.filter(u => u.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al eliminar usuario');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const selectUser = (user: User | null) => {
    setSelected(user);
  };

  const clearSelection = () => setSelected(null);

  return {
    users,
    loading,
    error,
    selected,
    loadUsers,
    createUser,
    updateUser,
    deleteUser,
    selectUser,
    clearSelection,
  } as const;
}

export default useUsersManagement;
