import Navbar from '../components/Navbar';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import useUsersManagement from '../hooks/useUsersManagement';

const schema = z.object({
  name: z.string().min(2, 'Nombre requerido'),
  email: z.string().email('Email inválido'),
  phone: z.string().optional(),
  city: z.string().optional(),
  congregation: z.string().optional(),
  privilege: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

export default function UsersPage() {
  const { users, selected, createUser, updateUser, deleteUser, selectUser, loadUsers } = useUsersManagement();

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    // Map form to API shape: combine city/congregation/privilege into tags
    const payload = {
      name: data.name,
      email: data.email,
      age: 0,
      phone: data.phone || '',
      city: data.city || undefined,
      congregation: data.congregation || undefined,
      privilege: data.privilege || undefined,
    };

    try {
      if (selected) {
        await updateUser(selected.id, payload);
      } else {
        await createUser(payload);
      }
      reset();
      await loadUsers();
    } catch {
      // error handled in hook
    }
  };

  const handleEdit = (id: string) => {
    const u = users.find(x => x.id === id);
    if (!u) return;
    selectUser(u);
    // try to prefill fields (basic split of tags)
    const [city, congregation, privilege] = (u.tags || []).slice(0,3);
    reset({ name: u.name, email: u.email, phone: u.phone, city: city || '', congregation: congregation || '', privilege: privilege || '' });
  };

  return (
    <div className="min-h-screen bg-[#0b1220] text-slate-200">
      <Navbar />
      <main className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column: form */}
          <div className="bg-[#111827] p-6 rounded-2xl border border-[#1e293b] shadow">
            <h2 className="text-xl font-semibold mb-4">{selected ? 'Editar Usuario' : 'Crear Usuario'}</h2>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="text-sm text-slate-400 block mb-1">Nombre</label>
                <input {...register('name')} className="w-full rounded-md bg-[#0b1220] border border-[#263141] px-3 py-2" />
                {errors.name && <p className="text-xs text-rose-500">{errors.name.message}</p>}
              </div>
              <div>
                <label className="text-sm text-slate-400 block mb-1">Correo</label>
                <input {...register('email')} className="w-full rounded-md bg-[#0b1220] border border-[#263141] px-3 py-2" />
                {errors.email && <p className="text-xs text-rose-500">{errors.email.message}</p>}
              </div>
              <div>
                <label className="text-sm text-slate-400 block mb-1">Teléfono</label>
                <input {...register('phone')} className="w-full rounded-md bg-[#0b1220] border border-[#263141] px-3 py-2" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                <input {...register('city')} placeholder="Ciudad" className="rounded-md bg-[#0b1220] border border-[#263141] px-3 py-2" />
                <input {...register('congregation')} placeholder="Congregación" className="rounded-md bg-[#0b1220] border border-[#263141] px-3 py-2" />
                <input {...register('privilege')} placeholder="Privilegio" className="rounded-md bg-[#0b1220] border border-[#263141] px-3 py-2" />
              </div>

              <div className="flex gap-3">
                <button type="submit" disabled={isSubmitting} className="flex-1 py-2 rounded bg-indigo-600 hover:bg-indigo-500">{selected ? 'Actualizar' : 'Crear'}</button>
                <button type="button" onClick={() => { reset(); selectUser(null); }} className="py-2 px-4 rounded border border-[#263141]">Limpiar</button>
              </div>
            </form>
          </div>

          {/* Right columns: table (span 2) */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Lista de Usuarios</h2>
              <div className="w-1/3">
                <input placeholder="Buscar..." className="w-full rounded-md bg-[#0b1220] border border-[#263141] px-3 py-2" />
              </div>
            </div>

            <div className="bg-[#111827] p-4 rounded-2xl border border-[#1e293b] shadow overflow-x-auto">
              <table className="min-w-full text-left">
                <thead>
                  <tr className="text-sm text-slate-400 border-b border-[#263141]">
                    <th className="px-3 py-2">Nombre</th>
                    <th className="px-3 py-2">Correo</th>
                    <th className="px-3 py-2">Teléfono</th>
                    <th className="px-3 py-2">Ciudad</th>
                    <th className="px-3 py-2">Congregación</th>
                    <th className="px-3 py-2">Privilegio</th>
                    <th className="px-3 py-2">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id} className="border-b border-[#0f172a] hover:bg-[#0f172a]/40">
                      <td className="px-3 py-2">{u.name}</td>
                      <td className="px-3 py-2">{u.email}</td>
                      <td className="px-3 py-2">{u.phone}</td>
                      {/* Attempt to read city/congregation/privilege from tags */}
                      {(() => {
                        const parts = u.tags || [];
                        return (
                          <>
                            <td className="px-3 py-2">{parts[0] || '-'}</td>
                            <td className="px-3 py-2">{parts[1] || '-'}</td>
                            <td className="px-3 py-2">{parts[2] || '-'}</td>
                          </>
                        );
                      })()}
                      <td className="px-3 py-2">
                        <div className="flex gap-2">
                          <button onClick={() => handleEdit(u.id)} className="px-3 py-1 bg-indigo-600 rounded text-white">Editar</button>
                          <button onClick={() => deleteUser(u.id)} className="px-3 py-1 bg-red-600 rounded text-white">Eliminar</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
