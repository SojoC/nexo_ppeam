import React, { useState } from 'react';
import dayjs from 'dayjs';

type Location = {
  id: string;
  name: string;
  max: number;
  days: number[];
};

const locations: Location[] = [
  { id: '1', name: 'PARQUE LA GUARICHA', max: 8, days: [6, 0] },
  { id: '2', name: 'PLAZA AYACUCHO', max: 6, days: [0,1,2,3,4,5,6] },
  { id: '3', name: 'PLAZA BALANCÍN', max: 6, days: [0,1,2,3,4,5,6] },
  { id: '4', name: 'PLAZA ESTUDIANTE', max: 6, days: [0,1,2,3,4,5,6] },
  { id: '5', name: 'PLAZA PIAR', max: 6, days: [0,1,2,3,4,5,6] },
  { id: '6', name: 'TERMINAL', max: 6, days: [0,1,2,3,4,5,6] },
];

type Assigned = {
  id: string;
  name: string;
};

type DayEntry = {
  date: string;
  day: string;
  locations: Array<{
    id: string;
    name: string;
    max: number;
    assigned: Assigned[];
    pairs: Array<[Assigned, Assigned] | Assigned[]>;
  }>;
};

function GestorReuniones() {
  const [startDate, setStartDate] = useState(dayjs().startOf('week').add(1, 'day'));
  const [endDate, setEndDate] = useState(dayjs().startOf('week').add(7, 'day'));
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [seedCounter, setSeedCounter] = useState(1);

  const toggleLocation = (id: string) => {
    setSelectedLocations(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const generateWeekSchedule = (): DayEntry[] => {
    const days: DayEntry[] = [];
    for (let i = 0; i < 7; i++) {
      const date = dayjs(startDate).add(i, 'day');
      const weekday = date.day();
      const dayEntry: DayEntry = {
        date: date.format('YYYY-MM-DD'),
        day: date.format('dddd'),
        locations: locations
          .filter(loc => selectedLocations.includes(loc.id) && loc.days.includes(weekday))
          .map(loc => ({ id: loc.id, name: loc.name, max: loc.max, assigned: [], pairs: [] })),
      };
      days.push(dayEntry);
    }
    return days;
  };

  const [schedule, setSchedule] = useState<DayEntry[]>(generateWeekSchedule());

  const regenerate = () => setSchedule(generateWeekSchedule());

  // Demo helper: add a mock participant to a day/location
  const addMockParticipant = (dateIndex: number, locationId: string) => {
    setSchedule(prev => {
      const copy = JSON.parse(JSON.stringify(prev)) as DayEntry[];
      const day = copy[dateIndex];
      if (!day) return prev;
      const loc = day.locations.find(l => l.id === locationId);
      if (!loc) return prev;
      if (loc.assigned.length >= loc.max) return prev; // full
      const newPerson: Assigned = { id: `${dateIndex}-${locationId}-${seedCounter}`, name: `Persona ${seedCounter}` };
      setSeedCounter(s => s + 1);
      loc.assigned.push(newPerson);
      // if reached capacity and max is even, form pairs
      if (loc.assigned.length === loc.max) {
        const pairs: Array<[Assigned, Assigned]> = [];
        for (let i = 0; i < loc.assigned.length; i += 2) {
          const a = loc.assigned[i];
          const b = loc.assigned[i+1] ?? { id: `dummy-${i}`, name: 'Sin pareja' } as Assigned;
          pairs.push([a, b]);
        }
        loc.pairs = pairs;
      }
      return copy;
    });
  };

  return (
    <div className="p-6 max-w-6xl mx-auto bg-slate-900 text-white min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-center">Gestor de Reuniones Semanales</h1>

      <div className="bg-slate-800 p-4 rounded shadow mb-6">
        <h2 className="text-2xl mb-2">Crear Semana de Actividades</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block font-medium">Fecha Inicio (Lunes)</label>
            <input type="date" className="w-full text-black rounded" value={startDate.format('YYYY-MM-DD')} onChange={e => setStartDate(dayjs(e.target.value))} />
          </div>
          <div>
            <label className="block font-medium">Fecha Fin (Domingo)</label>
            <input type="date" className="w-full text-black rounded" value={endDate.format('YYYY-MM-DD')} onChange={e => setEndDate(dayjs(e.target.value))} />
          </div>
        </div>

        <h3 className="text-xl font-semibold mb-2">Seleccionar Ubicaciones</h3>
        <div className="grid md:grid-cols-2 gap-3">
          {locations.map(loc => (
            <label key={loc.id} className="border p-3 rounded shadow bg-slate-800 text-white flex items-start gap-3">
              <input type="checkbox" checked={selectedLocations.includes(loc.id)} onChange={() => toggleLocation(loc.id)} />
              <div>
                <div className="font-semibold">{loc.name}</div>
                <div className="text-sm text-slate-400">Máx. {loc.max} participantes</div>
              </div>
            </label>
          ))}
        </div>

        <div className="mt-4">
          <button className="px-4 py-2 bg-indigo-600 rounded" onClick={regenerate}>Generar vista preliminar</button>
        </div>
      </div>

      <div className="bg-slate-800 p-4 rounded shadow">
        <h2 className="text-xl mb-2">Vista Preliminar (Interactiva)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {schedule.map((day, di) => (
            <div key={day.date} className="p-3 bg-slate-700 rounded">
              <div className="flex justify-between items-center mb-2">
                <div>
                  <div className="font-semibold">{day.day}</div>
                  <div className="text-sm text-slate-400">{day.date}</div>
                </div>
                <div className="text-sm text-slate-400">{day.locations.length} ubicaciones</div>
              </div>

              {day.locations.length === 0 && (
                <div className="text-sm text-slate-400">No hay ubicaciones seleccionadas para este día</div>
              )}

              <div className="grid gap-2">
                {day.locations.map(loc => (
                  <div key={loc.id} className="p-2 bg-slate-800 rounded border">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-semibold">{loc.name}</div>
                        <div className="text-sm text-slate-400">{loc.assigned.length} de {loc.max} participantes</div>
                      </div>
                      <div className="flex gap-2">
                        <button className="px-2 py-1 bg-green-600 rounded text-sm" onClick={() => addMockParticipant(di, loc.id)}>Agregar participante (demo)</button>
                      </div>
                    </div>

                    {loc.assigned.length > 0 && (
                      <div className="mt-2 text-sm">
                        <div className="font-medium">Asistentes:</div>
                        <ul className="list-disc ml-5">
                          {loc.assigned.map(a => <li key={a.id}>{a.name}</li>)}
                        </ul>
                      </div>
                    )}

                    {loc.pairs && loc.pairs.length > 0 && (
                      <div className="mt-2 text-sm">
                        <div className="font-medium">Parejas asignadas:</div>
                        <ul className="list-decimal ml-5">
                          {loc.pairs.map((p: any, idx: number) => (
                            <li key={idx}>{Array.isArray(p) ? `${p[0]?.name} + ${p[1]?.name}` : JSON.stringify(p)}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default GestorReuniones;
