import { useEffect, useMemo, useState } from "react";
import dayjs, { Dayjs } from "dayjs";
import "dayjs/locale/es";
import { usersAPI } from "../services/api";

dayjs.locale("es");

// Lugares disponibles (puedes editar estos nombres / tamaños)
const locations = [
  { id: "1", name: "PARQUE LA GUARICHA", max: 8, days: [6, 0] }, // sáb / dom
  { id: "2", name: "PLAZA AYACUCHO", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
  { id: "3", name: "PLAZA BALANCÍN", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
  { id: "4", name: "PLAZA ESTUDIANTE", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
  { id: "5", name: "PLAZA PIAR", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
  { id: "6", name: "TERMINAL", max: 6, days: [0, 1, 2, 3, 4, 5, 6] },
];

type User = {
  id?: string;
  nombre?: string;
  apellido?: string;
  telefono?: string;
  congregacion?: string;
};

// Cada fila de la carta tipo imagen 1
type SlotRow = {
  time: string;
  pub1?: User;
  pub2?: User;
};

// Configuración editable por día (lugar, contacto, nota)
type DayConfig = {
  place: string;
  contact: string;
  note: string;
  locationId: string; // qué lugar se está usando ese día
  customTimes?: string[]; // horarios personalizados para la carta de ese día
};

// ==========================
// Helpers
// ==========================

// Construye la matriz de semanas para el calendario mensual
function buildMonthMatrix(base: Dayjs): Dayjs[][] {
  const startOfMonth = base.startOf("month");
  const endOfMonth = base.endOf("month");

  const start = startOfMonth.startOf("week"); // según locale (es → lunes)
  const end = endOfMonth.endOf("week");

  const weeks: Dayjs[][] = [];
  let cursor = start;

  while (cursor.isBefore(end) || cursor.isSame(end, "day")) {
    const weekIndex = weeks.length - 1;
    if (weeks.length === 0 || weeks[weekIndex].length === 7) {
      weeks.push([]);
    }
    weeks[weeks.length - 1].push(cursor);
    cursor = cursor.add(1, "day");
  }
  return weeks;
}

// Time slots por defecto que se verán en la tabla (puedes ajustarlos a tu diseño)
const TIME_SLOTS = [
  "8:55 AM",
  "9:20 AM",
  "9:45 AM",
  "10:10 AM",
  "10:35 AM",
  "11:00 AM",
];

// Genera filas Pub1 / Pub2 para un lugar concreto
function buildSlots(usuarios: User[], max: number, times: string[] = TIME_SLOTS): SlotRow[] {
  const participantes = usuarios.slice(0, max); // aquí luego podemos meter lógica avanzada
  const rows: SlotRow[] = [];

  for (let i = 0; i < participantes.length && i / 2 < times.length; i += 2) {
    const slotIndex = i / 2;
    rows.push({
      time: times[slotIndex],
      pub1: participantes[i],
      pub2: participantes[i + 1],
    });
  }

  // Si quieres forzar siempre todas las horas, aun sin gente:
  while (rows.length < times.length) {
    rows.push({
      time: times[rows.length],
    });
  }

  return rows;
}

// ==========================
// Componente principal
// ==========================

export default function GestorReuniones() {
  const [usuarios, setUsuarios] = useState<User[]>([]);
  const [currentMonth, setCurrentMonth] = useState<Dayjs>(() => dayjs());
  const [selectedDate, setSelectedDate] = useState<Dayjs>(() => dayjs());
  const [dayConfigs, setDayConfigs] = useState<Record<string, DayConfig>>({});

  // Lugar seleccionado en el selector (arriba de la carta)
  const [selectedLocationId, setSelectedLocationId] = useState<string>("1");

  // Cargar usuarios desde el backend (como ya hacías)
  useEffect(() => {
    let mounted = true;
    usersAPI
      .getAll()
      .then((data) => {
        if (!mounted) return;
        setUsuarios(Array.isArray(data) ? data : []);
      })
      .catch(() => setUsuarios([]));

    return () => {
      mounted = false;
    };
  }, []);

  // Matriz de semanas para el calendario mensual
  const monthMatrix = useMemo(
    () => buildMonthMatrix(currentMonth),
    [currentMonth]
  );

  // Lugar elegido para el calendario (selector superior)
  const calendarSelectedLocation =
    locations.find((l) => l.id === selectedLocationId) || locations[0];

  // clave única por día: YYYY-MM-DD
  const selectedKey = selectedDate.format("YYYY-MM-DD");

  // Configuración guardada (en memoria) para el día actual
  const currentDayConfig: DayConfig =
    dayConfigs[selectedKey] || {
      place: "",
      contact: "",
      note: "",
      locationId: selectedLocationId,
    };

  // Lugar elegido para la carta
  const selectedLocation =
    locations.find((l) => l.id === currentDayConfig.locationId) ||
    locations[0];

  // Filas de la tabla para ese lugar
  const slotRows = useMemo(
    () => buildSlots(usuarios, selectedLocation.max, currentDayConfig.customTimes || TIME_SLOTS),
    [usuarios, selectedLocation.max]
  );

  const handleTimeChange = (index: number, value: string) => {
    setDayConfigs((prev) => {
      const prevCfg = prev[selectedKey] || { ...currentDayConfig };
      const times = (prevCfg.customTimes || TIME_SLOTS).slice();
      times[index] = value;
      return {
        ...prev,
        [selectedKey]: {
          ...prevCfg,
          customTimes: times,
        },
      };
    });
  };

  const handleConfigChange = (field: keyof DayConfig, value: string) => {
    setDayConfigs((prev) => ({
      ...prev,
      [selectedKey]: {
        ...currentDayConfig,
        [field]: value,
      },
    }));
  };

  const handleLocationChange = (value: string) => {
    setSelectedLocationId(value);
    setDayConfigs((prev) => ({
      ...prev,
      [selectedKey]: {
        ...currentDayConfig,
        locationId: value,
      },
    }));
  };

  // ========================== RENDER ==========================

  return (
    <div className="min-h-screen bg-[#050816] text-slate-100 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Encabezado */}
        <header className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold mb-1 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Gestor de Reuniones — Calendario
            </h1>
            <p className="text-slate-400">
              Selecciona un día del calendario y edita la carta de programación
              para ese día (lugar, parejas, nota, contacto).
            </p>
          </div>
        </header>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* ==================== COLUMNA IZQUIERDA: CALENDARIO ==================== */}
          <div className="lg:col-span-1">
            <div className="bg-slate-900/80 border border-slate-700 rounded-2xl p-4 shadow-lg">
              {/* Header del mes */}
              <div className="flex items-center justify-between mb-4">
                <button
                  className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm"
                  onClick={() =>
                    setCurrentMonth((prev) => prev.subtract(1, "month"))
                  }
                >
                  ← Anterior
                </button>
                {/* Selector global de lugar: elegir lugar antes del día */}
                <div className="mx-4">
                  <label className="text-xs text-slate-300 block">Lugar</label>
                  <select
                    value={selectedLocationId}
                    onChange={(e) => setSelectedLocationId(e.target.value)}
                    className="bg-slate-800 text-xs text-slate-100 rounded px-2 py-1 border border-slate-700"
                  >
                    {locations.map((loc) => (
                      <option key={loc.id} value={loc.id}>
                        {loc.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="text-center">
                  <div className="font-semibold">
                    {currentMonth.format("MMMM YYYY").toUpperCase()}
                  </div>
                  <div className="text-xs text-slate-400">
                    Día seleccionado: {" "}
                    <span className="font-medium text-indigo-300">
                      {selectedDate.format("dddd D [de] MMMM")}
                    </span>
                  </div>
                </div>
                <button
                  className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm"
                  onClick={() =>
                    setCurrentMonth((prev) => prev.add(1, "month"))
                  }
                >
                  Siguiente →
                </button>
              </div>

              {/* Cabecera de días de la semana */}
              <div className="grid grid-cols-7 text-xs font-semibold text-center text-slate-400 mb-2">
                {["L", "M", "X", "J", "V", "S", "D"].map((d) => (
                  <div key={d} className="py-1">
                    {d}
                  </div>
                ))}
              </div>

              {/* Celdas del calendario */}
              <div className="grid grid-cols-7 gap-1 text-sm">
                {monthMatrix.map((week, wIdx) =>
                  week.map((date) => {
                    const isCurrentMonth =
                      date.month() === currentMonth.month();
                    const isSelected = date.isSame(selectedDate, "day");
                    const isToday = date.isSame(dayjs(), "day");
                    const isWeekend = [0, 6].includes(date.day()); // dom / sáb

                    const allowedForCalendar = calendarSelectedLocation.days.includes(
                      date.day()
                    );

                    const classes = [
                      "aspect-square rounded-lg flex items-center justify-center border text-xs transition",
                      isSelected
                        ? "bg-indigo-600 text-white border-indigo-400 shadow-lg"
                        : isToday
                        ? "border-indigo-500/70 text-indigo-300 bg-slate-800/80"
                        : isCurrentMonth
                        ? "border-slate-700 bg-slate-900 hover:bg-slate-800"
                        : "border-slate-800 bg-slate-950/70 text-slate-500",
                      isWeekend && !isSelected ? "font-semibold" : "",
                    ];

                    if (!allowedForCalendar && !isSelected) {
                      classes.push("opacity-40 cursor-not-allowed");
                    }

                    return (
                      <button
                        key={date.format("YYYY-MM-DD") + wIdx}
                        onClick={() => {
                          if (!allowedForCalendar) return;
                          setSelectedDate(date);
                          // si no hay config para este día, prellenar con el lugar del selector
                          const key = date.format("YYYY-MM-DD");
                          setDayConfigs((prev) => {
                            if (prev[key]) return prev;
                            return {
                              ...prev,
                              [key]: {
                                place: "",
                                contact: "",
                                note: "",
                                locationId: selectedLocationId,
                              },
                            };
                          });
                        }}
                        className={classes.join(" ")}
                        title={
                          allowedForCalendar
                            ? undefined
                            : `No disponible para ${calendarSelectedLocation.name}`
                        }
                      >
                        {date.date()}
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          </div>

          {/* ==================== COLUMNA DERECHA: CARTA DEL DÍA ==================== */}
          <div className="lg:col-span-2">
            <div className="bg-slate-900/90 border border-slate-700 rounded-2xl p-6 shadow-lg space-y-6">
              {/* Encabezado tipo carta */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm font-semibold text-center">
                <div className="bg-indigo-700 text-white rounded-lg py-2">
                  <div>DÍA</div>
                  <div className="mt-1 capitalize">
                    {selectedDate.format("dddd")}
                  </div>
                </div>
                <div className="bg-indigo-700 text-white rounded-lg py-2">
                  <div>FECHA</div>
                  <div className="mt-1">
                    {selectedDate.format("DD/MM/YYYY")}
                  </div>
                </div>
                <div className="bg-indigo-700 text-white rounded-lg py-2">
                  <div>LUGAR</div>
                  <div className="mt-1">
                    <select
                      className="w-full bg-indigo-800 text-xs rounded border border-indigo-300 px-2 py-1"
                      value={currentDayConfig.locationId}
                      onChange={(e) => handleLocationChange(e.target.value)}
                    >
                      {locations.map((loc) => (
                        <option key={loc.id} value={loc.id}>
                          {loc.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Campo de texto para nombre libre del lugar (ej: GUARICHA TARDE) */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="md:col-span-3">
                  <label className="block text-slate-300 mb-1">
                    Nombre específico del lugar (ej: GUARICHA TARDE)
                  </label>
                  <input
                    type="text"
                    className="w-full rounded-lg bg-slate-800 border border-slate-600 px-3 py-2 text-sm"
                    value={currentDayConfig.place}
                    onChange={(e) =>
                      handleConfigChange("place", e.target.value)
                    }
                    placeholder="Ej. GUARICHA TARDE"
                  />
                </div>
              </div>

              {/* Tabla Pub1 / Inicio / Pub2 (como imagen 1) */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-slate-800 text-slate-100">
                      <th className="border border-slate-700 px-2 py-1 w-1/3">
                        Pub 1
                      </th>
                      <th className="border border-slate-700 px-2 py-1 w-1/3">
                        Inicio
                      </th>
                      <th className="border border-slate-700 px-2 py-1 w-1/3">
                        Pub 2
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {slotRows.map((slot, idx) => (
                      <tr
                        key={idx}
                        className={
                          idx % 2 === 0 ? "bg-slate-900" : "bg-slate-800/70"
                        }
                      >
                        <td className="border border-slate-700 px-2 py-1">
                          {slot.pub1
                            ? `${slot.pub1.nombre ?? ""} ${
                                slot.pub1.apellido ?? ""
                              }`
                            : "—"}
                        </td>
                        <td className="border border-slate-700 px-2 py-1 text-center">
                          {slot.time}
                        </td>
                        <td className="border border-slate-700 px-2 py-1">
                          {slot.pub2
                            ? `${slot.pub2.nombre ?? ""} ${
                                slot.pub2.apellido ?? ""
                              }`
                            : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Persona de contacto + nota (parte inferior de la carta) */}
              {/* Editar horas (time slots) */}
              <div className="mt-2 bg-slate-800/60 p-3 rounded-md">
                <div className="text-xs text-slate-300 font-medium mb-2">Editar horas (modifica las horas para este día)</div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  {(currentDayConfig.customTimes || TIME_SLOTS).map((t, i) => (
                    <input
                      key={i}
                      value={t}
                      onChange={(e) => handleTimeChange(i, e.target.value)}
                      className="w-full rounded bg-slate-900 border border-slate-700 px-2 py-1 text-sm"
                    />
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="md:col-span-2">
                  <label className="block text-slate-300 mb-1">
                    Persona de contacto
                  </label>
                  <input
                    type="text"
                    className="w-full rounded-lg bg-slate-800 border border-slate-600 px-3 py-2 text-sm"
                    value={currentDayConfig.contact}
                    onChange={(e) =>
                      handleConfigChange("contact", e.target.value)
                    }
                    placeholder="Ej. García, Dimas 0414-XXXXX"
                  />
                </div>
                <div className="md:col-span-1">
                  <label className="block text-slate-300 mb-1">
                    Nota inferior
                  </label>
                  <input
                    type="text"
                    className="w-full rounded-lg bg-slate-800 border border-slate-600 px-3 py-2 text-sm"
                    value={currentDayConfig.note}
                    onChange={(e) =>
                      handleConfigChange("note", e.target.value)
                    }
                    placeholder="Ej. Confirme su participación"
                  />
                </div>
              </div>

              <p className="text-xs text-slate-400 italic">
                * De momento esta configuración se mantiene sólo en memoria del
                navegador. Para guardarla definitivamente habría que crear un
                endpoint en el backend (podemos hacerlo en otro paso).
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
  
