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

type UserAny = Record<string, any>;

export default function GestorReuniones() {
  const [startDate, setStartDate] = useState(dayjs().startOf("week").add(1, "day"));
  const [endDate, setEndDate] = useState(dayjs().startOf("week").add(7, "day"));
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [usuarios, setUsuarios] = useState<UserAny[]>([]);

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

  const displayName = (u: UserAny) => u?.nombre || u?.firstName || u?.name || u?.email || 'Usuario';

  const generateWeekSchedule = () => {
    const days: any[] = [];
    for (let i = 0; i < 7; i++) {
      const date = dayjs(startDate).add(i, "day");
      const weekday = date.day();
      const dayEntry = {
        date: date.format("YYYY-MM-DD"),
        day: date.format("dddd"),
        locations: locations
          .filter(loc => selectedLocations.includes(loc.id) && loc.days.includes(weekday))
          .map(loc => {
            const participantes = usuarios.slice(0, loc.max);
            const pairs: any[] = [];
            for (let j = 0; j < participantes.length; j += 2) {
              pairs.push(participantes.slice(j, j + 2));
            }
            return { ...loc, participantes, pairs };
          }),
      };
      days.push(dayEntry);
    }
    return days;
  };

  return (
    <div className="p-6 max-w-6xl mx-auto bg-slate-900 text-white min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-center">Gestor de Reuniones PPEAM</h1>

      <div className="bg-slate-800 p-4 rounded shadow mb-6">
        <h2 className="text-2xl mb-2">Crear Semana</h2>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block font-medium">Inicio (Lunes)</label>
            <input type="date" className="w-full text-black rounded" value={startDate.format("YYYY-MM-DD")} onChange={e => setStartDate(dayjs(e.target.value))} />
          </div>
          <div>
            <label className="block font-medium">Fin (Domingo)</label>
            <input type="date" className="w-full text-black rounded" value={endDate.format("YYYY-MM-DD")} onChange={e => setEndDate(dayjs(e.target.value))} />
          </div>
        </div>
        <h3 className="text-xl font-semibold mb-2">Ubicaciones</h3>
        <div className="grid md:grid-cols-2 gap-3">
          {locations.map(loc => (
            <label key={loc.id} className="border p-3 rounded shadow bg-slate-800 text-white flex items-start gap-3">
              <input
                type="checkbox"
                checked={selectedLocations.includes(loc.id)}
                onChange={() => toggleLocation(loc.id)}
              />
              <div>
                <div className="font-semibold">{loc.name}</div>
                <div className="text-sm text-gray-400">Máx. {loc.max} participantes</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      <div className="bg-slate-800 p-4 rounded shadow mb-6">
        <h2 className="text-xl mb-2">Matriz Semanal</h2>
        {generateWeekSchedule().map(dia => (
          <div key={dia.date} className="mb-4">
            <h3 className="text-lg font-semibold text-blue-300">{dia.day} – {dia.date}</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {dia.locations.map((loc: any) => (
                <div key={loc.id} className="bg-slate-700 p-3 rounded">
                  <h4 className="font-bold">{loc.name}</h4>
                  {loc.pairs.map((pair: any[], i: number) => (
                    <div key={i} className="text-sm bg-slate-900 p-2 my-1 rounded">
                      Pareja {i + 1}: {pair.map(p => displayName(p)).join(" & ")}
                    </div>
                  ))}
                  {loc.participantes.length === 0 && <p className="text-sm italic text-gray-400">Sin asignados</p>}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
  
