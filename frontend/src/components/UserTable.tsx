import type { User } from '../types';

interface UserTableProps {
  users: User[];
  loading: boolean;
  onEdit: (user: User) => void;
  onDelete: (id: string) => void;
  onRefresh: () => void;
}

export default function UserTable({
  users,
  loading,
  onEdit,
  onDelete,
  onRefresh,
}: UserTableProps) {
  if (loading && users.length === 0) {
    return (
      <div style={styles.card}>
        <p style={styles.loadingText}>Cargando usuarios...</p>
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <div style={styles.card}>
        <p style={styles.emptyText}>No hay usuarios registrados</p>
      </div>
    );
  }

  return (
    <div style={styles.card}>
      <div style={styles.cardHeader}>
        <h2 style={styles.cardTitle}>Lista de Usuarios</h2>
        <button onClick={onRefresh} style={styles.refreshButton}>
          Actualizar
        </button>
      </div>

      <div style={styles.tableContainer}>
        <table style={styles.table}>
          <thead>
            <tr style={styles.tableHeader}>
              <th style={styles.th}>Nombre</th>
              <th style={styles.th}>Email</th>
              <th style={styles.th}>Edad</th>
              <th style={styles.th}>Teléfono</th>
              <th style={styles.th}>Tags</th>
              <th style={styles.th}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} style={styles.tableRow}>
                <td style={styles.td}>{user.name}</td>
                <td style={styles.td}>{user.email}</td>
                <td style={styles.td}>{user.age}</td>
                <td style={styles.td}>{user.phone}</td>
                <td style={styles.td}>
                  <div style={styles.tagsContainer}>
                    {user.tags.map((tag, idx) => (
                      <span key={idx} style={styles.tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                </td>
                <td style={styles.td}>
                  <div style={styles.actionButtons}>
                    <button onClick={() => onEdit(user)} style={styles.editButton}>
                      Editar
                    </button>
                    <button
                      onClick={() => onDelete(user.id)}
                      style={styles.deleteButton}
                    >
                      Eliminar
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  card: {
    backgroundColor: '#1e293b',
    borderRadius: '16px',
    padding: '32px',
    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  cardTitle: {
    fontSize: '24px',
    fontWeight: '600',
    color: '#f1f5f9',
    margin: 0,
  },
  refreshButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '600',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: '#22c55e',
    color: '#ffffff',
    cursor: 'pointer',
  },
  loadingText: {
    textAlign: 'center',
    color: '#94a3b8',
    fontSize: '16px',
  },
  emptyText: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: '16px',
  },
  tableContainer: {
    overflowX: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  tableHeader: {
    backgroundColor: '#0f172a',
  },
  th: {
    padding: '12px',
    textAlign: 'left',
    fontSize: '14px',
    fontWeight: '600',
    color: '#cbd5e1',
    borderBottom: '2px solid #334155',
  },
  tableRow: {
    borderBottom: '1px solid #334155',
  },
  td: {
    padding: '12px',
    fontSize: '14px',
    color: '#e2e8f0',
  },
  tagsContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '6px',
  },
  tag: {
    padding: '4px 10px',
    fontSize: '12px',
    borderRadius: '12px',
    backgroundColor: '#334155',
    color: '#cbd5e1',
  },
  actionButtons: {
    display: 'flex',
    gap: '8px',
  },
  editButton: {
    padding: '6px 14px',
    fontSize: '13px',
    fontWeight: '500',
    borderRadius: '6px',
    border: 'none',
    backgroundColor: '#2563eb',
    color: '#ffffff',
    cursor: 'pointer',
  },
  deleteButton: {
    padding: '6px 14px',
    fontSize: '13px',
    fontWeight: '500',
    borderRadius: '6px',
    border: 'none',
    backgroundColor: '#dc2626',
    color: '#ffffff',
    cursor: 'pointer',
  },
};
