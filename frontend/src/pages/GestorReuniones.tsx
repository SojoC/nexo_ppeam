import { useEffect, useState } from "react";
import dayjs from "dayjs";
import { usersAPI } from "../services/api";

const locations = [
  { id: "1", name: "PARQUE LA GUARICHA", max: 8, days: [6, 0] },
  { id: "2", name: "PLAZA AYACUCHO", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
  { id: "3", name: "PLAZA BALANCÍN", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
  { id: "4", name: "PLAZA ESTUDIANTE", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
  { id: "5", name: "PLAZA PIAR", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
  { id: "6", name: "TERMINAL", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
];

type User = {
  id?: string;
  nombre?: string;
  firstName?: string;
  name?: string;
  email?: string;
  [key: string]: unknown;
};

type DayLocation = {
  id: string;
  name: string;
  max: number;
  participantes: User[];
  pairs: User[][];
  [key: string]: unknown;
};

type DayEntry = {
  date: string;
  day: string;
  locations: DayLocation[];
};

export default function GestorReuniones() {
  const [startDate, setStartDate] = useState(dayjs().startOf("week").add(1, "day"));
  const [endDate, setEndDate] = useState(dayjs().startOf("week").add(7, "day"));
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [usuarios, setUsuarios] = useState<User[]>([]);

  useEffect(() => {
    let mounted = true;
    usersAPI.getAll()
      .then(data => {
        if (!mounted) return;
        setUsuarios(Array.isArray(data) ? data : []);
      })
      .catch(() => setUsuarios([]));
    return () => { mounted = false };
  }, []);

  const toggleLocation = (id: string) => {
    setSelectedLocations(prev => prev.includes(id) ? prev.filter(l => l !== id) : [...prev, id]);
  };

  const displayName = (u: User) => u?.nombre || u?.firstName || u?.name || u?.email || 'Usuario';

  const generateWeekSchedule = (): DayEntry[] => {
    const days: DayEntry[] = [];
    for (let i = 0; i < 7; i++) {
      const date = dayjs(startDate).add(i, "day");
      const weekday = date.day();
      const dayEntry = {
        date: date.format("YYYY-MM-DD"),
        day: date.format("dddd"),
        locations: locations
          .filter(loc => selectedLocations.includes(loc.id) && loc.days.includes(weekday))
          .map((loc): DayLocation => {
            const participantes = usuarios.slice(0, loc.max) as User[];
            const pairs: User[][] = [];
            for (let j = 0; j < participantes.length; j += 2) {
              pairs.push(participantes.slice(j, j + 2));
            }
            return { ...loc, participantes, pairs } as DayLocation;
          }),
      };
      days.push(dayEntry);
    }
    return days;
  };

  const badgeColors = [
    'bg-rose-400/80',
    'bg-amber-300/80',
    'bg-cyan-400/80',
    'bg-violet-400/80',
    'bg-lime-400/80',
  ];

  const getBadgeColor = (i: number) => badgeColors[i % badgeColors.length];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-4xl font-extrabold mb-6 text-center">Gestor de Reuniones Semanales</h1>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: controls */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800 p-6 rounded-2xl shadow border border-slate-700">
              <h2 className="text-2xl font-semibold mb-4">Crear Semana de Actividades</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Fecha Inicio (Lunes)</label>
                  <input type="date" className="w-full text-black rounded-md p-2" value={startDate.format('YYYY-MM-DD')} onChange={e => setStartDate(dayjs(e.target.value))} />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Fecha Fin (Domingo)</label>
                  <input type="date" className="w-full text-black rounded-md p-2" value={endDate.format('YYYY-MM-DD')} onChange={e => setEndDate(dayjs(e.target.value))} />
                </div>
              </div>

              <h3 className="text-lg font-semibold mb-3">Seleccionar Ubicaciones</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {locations.map(loc => {
                  const active = selectedLocations.includes(loc.id);
                  return (
                    <button key={loc.id} onClick={() => toggleLocation(loc.id)} className={`text-left p-3 rounded-lg border transition-shadow flex items-start gap-3 ${active ? 'border-indigo-500 bg-slate-900 shadow-lg' : 'border-slate-700 bg-slate-800 hover:shadow-md'}`}>
                      <input type="checkbox" checked={active} readOnly className="mt-1" />
                      <div className="flex-1">
                        <div className="font-medium">{loc.name}</div>
                        <div className="text-sm text-slate-400">Máx. {loc.max} participantes</div>
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="mt-4 flex gap-3">
                <button className="px-4 py-2 bg-indigo-600 rounded-lg" onClick={() => { /* regenerate preview */ }}>{'Generar'}</button>
                <button className="px-4 py-2 bg-slate-700 rounded-lg" onClick={() => { setSelectedLocations([]); }}>{'Limpiar'}</button>
              </div>
            </div>
          </div>

          {/* Center+Right: preview and matrix */}
          <div className="lg:col-span-2">
            <div className="bg-slate-800 p-6 rounded-2xl shadow border border-slate-700 mb-6">
              <h2 className="text-2xl font-semibold mb-4">Vista Preliminar (Matriz Semanal)</h2>

              <div className="space-y-6">
                {generateWeekSchedule().map((dia) => (
                  <article key={dia.date} className="bg-slate-700 rounded-xl p-4 border border-slate-700 shadow-sm">
                    <div className="mb-3 flex items-start justify-between">
                      <div>
                        <div className="font-semibold">{dia.day}</div>
                        <div className="text-sm text-slate-400">{dia.date}</div>
                      </div>
                      <div className="text-sm text-slate-400">{dia.locations.length} ubicaciones</div>
                    </div>

                    {dia.locations.length === 0 && <div className="text-sm text-slate-400">No hay ubicaciones seleccionadas para este día</div>}

                    <div className="mt-3 space-y-3">
                      {dia.locations.map((loc) => (
                        <div key={loc.id} className="bg-slate-800 p-4 rounded-lg border border-slate-700">
                          <div className="mb-2 flex items-center justify-between">
                            <div className="font-medium">{loc.name}</div>
                            <div className="text-sm text-slate-400">{loc.participantes.length} de {loc.max}</div>
                          </div>

                          {/* Pairs rendered as two-column schedule like image3 */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {loc.pairs.length === 0 && loc.participantes.length === 0 && (
                              <div className="text-sm italic text-slate-400">Sin asignados</div>
                            )}

                            {loc.pairs.map((pair, pi) => (
                              <div key={pi} className="flex gap-2">
                                <div className={`${getBadgeColor(pi)} text-slate-900 flex-1 rounded p-2 text-sm font-medium`}>{displayName(pair[0] ?? ({} as User))}</div>
                                <div className={`${getBadgeColor(pi+1)} text-slate-900 flex-1 rounded p-2 text-sm font-medium`}>{displayName(pair[1] ?? ({} as User))}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
  
