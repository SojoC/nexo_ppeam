import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { User } from '../types';
import Alert from './Alert';

const userSchema = z.object({
  name: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  email: z.string().email('Email inválido'),
  age: z.number().min(1, 'Edad inválida').max(120, 'Edad inválida'),
  phone: z.string().min(7, 'Teléfono inválido'),
  tags: z.string(),
});

type UserFormData = z.infer<typeof userSchema>;

interface UserFormProps {
  editingUser: User | null;
  onSubmit: (data: UserFormData) => Promise<void>;
  onCancel: () => void;
  loading: boolean;
  error: string;
  success: string;
}

export default function UserForm({
  editingUser,
  onSubmit,
  onCancel,
  loading,
  error,
  success,
}: UserFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
    values: editingUser
      ? {
          name: editingUser.name,
          email: editingUser.email,
          age: editingUser.age,
          phone: editingUser.phone,
          tags: editingUser.tags.join(', '),
        }
      : undefined,
  });

  return (
    <div style={styles.card}>
      <h2 style={styles.cardTitle}>
        {editingUser ? 'Editar Usuario' : 'Crear Usuario'}
      </h2>

      <form onSubmit={handleSubmit(onSubmit)} style={styles.form}>
        <div style={styles.formRow}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Nombre</label>
            <input
              {...register('name')}
              style={styles.input}
              placeholder="Juan Pérez"
            />
            {errors.name && (
              <span style={styles.errorText}>{errors.name.message}</span>
            )}
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              {...register('email')}
              style={styles.input}
              placeholder="juan@example.com"
            />
            {errors.email && (
              <span style={styles.errorText}>{errors.email.message}</span>
            )}
          </div>
        </div>

        <div style={styles.formRow}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Edad</label>
            <input
              type="number"
              {...register('age', { valueAsNumber: true })}
              style={styles.input}
              placeholder="25"
            />
            {errors.age && (
              <span style={styles.errorText}>{errors.age.message}</span>
            )}
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Teléfono</label>
            <input
              {...register('phone')}
              style={styles.input}
              placeholder="+56912345678"
            />
            {errors.phone && (
              <span style={styles.errorText}>{errors.phone.message}</span>
            )}
          </div>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Tags (separadas por coma)</label>
          <input
            {...register('tags')}
            style={styles.input}
            placeholder="admin, moderador, usuario"
          />
          {errors.tags && (
            <span style={styles.errorText}>{errors.tags.message}</span>
          )}
        </div>

        {error && <Alert type="error" message={error} />}
        {success && <Alert type="success" message={success} />}

        <div style={styles.buttonGroup}>
          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.primaryButton,
              ...(loading ? styles.buttonDisabled : {}),
            }}
          >
            {loading
              ? 'Guardando...'
              : editingUser
              ? 'Actualizar Usuario'
              : 'Crear Usuario'}
          </button>
          {editingUser && (
            <button type="button" onClick={onCancel} style={styles.secondaryButton}>
              Cancelar
            </button>
          )}
        </div>
      </form>
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
  cardTitle: {
    fontSize: '24px',
    fontWeight: '600',
    color: '#f1f5f9',
    marginBottom: '24px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  formRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#cbd5e1',
  },
  input: {
    padding: '12px 16px',
    fontSize: '16px',
    borderRadius: '8px',
    border: '1px solid #334155',
    backgroundColor: '#0f172a',
    color: '#f1f5f9',
    outline: 'none',
  },
  errorText: {
    fontSize: '13px',
    color: '#f87171',
  },
  buttonGroup: {
    display: 'flex',
    gap: '12px',
  },
  primaryButton: {
    flex: 1,
    padding: '14px',
    fontSize: '16px',
    fontWeight: '600',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: '#2563eb',
    color: '#ffffff',
    cursor: 'pointer',
  },
  secondaryButton: {
    flex: 1,
    padding: '14px',
    fontSize: '16px',
    fontWeight: '600',
    borderRadius: '8px',
    border: '1px solid #475569',
    backgroundColor: 'transparent',
    color: '#cbd5e1',
    cursor: 'pointer',
  },
  buttonDisabled: {
    backgroundColor: '#64748b',
    cursor: 'not-allowed',
  },
};
