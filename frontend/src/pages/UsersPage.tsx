import Navbar from '../components/Navbar';
import UserForm from '../components/UserForm';
import UserTable from '../components/UserTable';
import { useUsers } from '../hooks/useUsers';

export default function UsersPage() {
  const {
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
  } = useUsers();

  const handleSubmit = async (data: {
    name: string;
    email: string;
    age: number;
    phone: string;
    tags: string;
  }) => {
    if (editingUser) {
      await updateUser(editingUser.id, data);
    } else {
      await createUser(data);
    }
  };

  return (
    <div style={styles.container}>
      <Navbar />
      
      <div style={styles.content}>
        <UserForm
          editingUser={editingUser}
          onSubmit={handleSubmit}
          onCancel={cancelEdit}
          loading={loading}
          error={error}
          success={success}
        />

        <UserTable
          users={users}
          loading={loading}
          onEdit={startEdit}
          onDelete={deleteUser}
          onRefresh={loadUsers}
        />
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#0b1220',
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '32px 20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
  },
};
