import React from "react";

// ==========================
// RegisterForm — Formulario de registro modular profesional
// - Layout por secciones que aprovecha el espacio horizontal
// - Componentes reutilizables SectionCard, Label, Input, Select
// - Grid responsive para distribuir campos optimamente
// ==========================

export type RegisterFormData = {
  nombre: string;
  edad?: number | null;
  fecha_nacimiento?: string | null;
  sexo?: string | null;
  estado_civil?: string | null;
  fecha_bautismo?: string | null;
  privilegio?: string | null;
  telefono?: string | null;
  congregacion?: string | null;
  ciudad?: string | null;
  email?: string | null;
};

interface RegisterFormProps {
  formData: RegisterFormData;
  onChange: (field: keyof RegisterFormData, value: string | number | null) => void;
  onSubmit: () => void;
  onClear: () => void;
  isEditing: boolean;
  selectedId?: string | null;
}

// Opciones para select de estado civil
const civil = ["soltero", "casado", "divorciado", "viudo"] as const;

function SectionCard({ 
  title, 
  children, 
  actions 
}: { 
  title: string; 
  children: React.ReactNode; 
  actions?: React.ReactNode 
}) {
  return (
    <section className="bg-[#0b0f1a] border border-[#223048] rounded-xl shadow-sm mb-4">
      <header className="flex items-center justify-between px-4 py-3 border-b border-[#223048]">
        <h3 className="text-slate-200 font-medium text-sm tracking-tight">{title}</h3>
        {actions}
      </header>
      <div className="p-4">{children}</div>
    </section>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <label className="block text-xs uppercase tracking-wider text-slate-400 mb-1">
      {children}
    </label>
  );
}

function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={[
        "w-full rounded-xl px-3 py-2 text-sm",
        "bg-[#0b1222] border border-[#2a3b5f] text-slate-200",
        "placeholder:text-slate-500",
        "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
        props.className || "",
      ].join(" ")}
    />
  );
}

function Select({ 
  children, 
  ...rest 
}: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...rest}
      className={[
        "w-full rounded-xl px-3 py-2 text-sm",
        "bg-[#0b1222] border border-[#2a3b5f] text-slate-200",
        "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
      ].join(" ")}
    >
      {children}
    </select>
  );
}

function ToolbarButton({ 
  children, 
  onClick, 
  variant = "solid" as const,
  type = "button" as const
}: { 
  children: React.ReactNode; 
  onClick?: () => void; 
  variant?: "solid" | "ghost" | "danger" | "warn";
  type?: "button" | "submit";
}) {
  const base = "px-3 py-2 rounded-xl text-sm transition active:scale-[.98]";
  const styles = {
    solid: "bg-indigo-600 hover:bg-indigo-500 text-white",
    ghost: "border border-[#2a3b5f] hover:bg-[#101a31] text-slate-200",
    danger: "bg-red-600 hover:bg-red-500 text-white",
    warn: "bg-amber-600 hover:bg-amber-500 text-white",
  }[variant];
  
  return (
    <button type={type} onClick={onClick} className={`${base} ${styles}`}>
      {children}
    </button>
  );
}

export default function RegisterForm({
  formData,
  onChange,
  onSubmit,
  onClear,
  isEditing,
  selectedId
}: RegisterFormProps) {
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Manejo especial para campos numéricos
    if (name === "edad") {
      onChange(name, value ? Number(value) : null);
    } else {
      onChange(name as keyof RegisterFormData, value || null);
    }
  };

  // Evitar warning de unused parameter
  console.log("Editing:", isEditing, selectedId);

  return (
    <div className="space-y-4">
      {/* Sección: Datos Personales */}
      <SectionCard title="Datos Personales">
        <div className="space-y-3">
          
          <div>
            <Label>Nombre Completo *</Label>
            <Input
              type="text"
              name="nombre"
              value={formData.nombre || ""}
              onChange={handleInputChange}
              placeholder="Juan Pérez González"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Email</Label>
              <Input
                type="email"
                name="email"
                value={formData.email || ""}
                onChange={handleInputChange}
                placeholder="juan@email.com"
              />
            </div>

            <div>
              <Label>Teléfono</Label>
              <Input
                type="tel"
                name="telefono"
                value={formData.telefono || ""}
                onChange={handleInputChange}
                placeholder="300 123 4567"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Edad</Label>
              <Input
                type="number"
                name="edad"
                value={formData.edad ?? ""}
                onChange={handleInputChange}
                min="1"
                max="120"
                placeholder="25"
              />
            </div>

            <div>
              <Label>Sexo</Label>
              <Select
                name="sexo"
                value={formData.sexo || ""}
                onChange={handleInputChange}
              >
                <option value="">Seleccionar...</option>
                <option value="masculino">Masculino</option>
                <option value="femenino">Femenino</option>
              </Select>
            </div>
          </div>

          <div>
            <Label>Fecha de Nacimiento</Label>
            <Input
              type="date"
              name="fecha_nacimiento"
              value={formData.fecha_nacimiento || ""}
              onChange={handleInputChange}
            />
          </div>

          <div>
            <Label>Estado Civil</Label>
            <Select
              name="estado_civil"
              value={formData.estado_civil || ""}
              onChange={handleInputChange}
            >
              <option value="">Seleccionar...</option>
              {civil.map((estado) => (
                <option key={estado} value={estado}>
                  {estado.charAt(0).toUpperCase() + estado.slice(1)}
                </option>
              ))}
            </Select>
          </div>

        </div>
      </SectionCard>

      {/* Sección: Información Congregacional */}
      <SectionCard title="Información Congregacional">
        <div className="space-y-3">

          <div>
            <Label>Congregación</Label>
            <Input
              type="text"
              name="congregacion"
              value={formData.congregacion || ""}
              onChange={handleInputChange}
              placeholder="Congregación Norte"
            />
          </div>

          <div>
            <Label>Ciudad</Label>
            <Input
              type="text"
              name="ciudad"
              value={formData.ciudad || ""}
              onChange={handleInputChange}
              placeholder="Bogotá, Colombia"
            />
          </div>

          <div>
            <Label>Privilegio</Label>
            <Select
              name="privilegio"
              value={formData.privilegio || ""}
              onChange={handleInputChange}
            >
              <option value="">Sin privilegio</option>
              <option value="anciano">Anciano</option>
              <option value="siervo ministerial">Siervo Ministerial</option>
              <option value="precursor regular">Precursor Regular</option>
              <option value="precursor auxiliar">Precursor Auxiliar</option>
              <option value="precursor especial">Precursor Especial</option>
              <option value="betelita">Betelita</option>
              <option value="misionero">Misionero</option>
            </Select>
          </div>

          <div>
            <Label>Fecha de Bautismo</Label>
            <Input
              type="date"
              name="fecha_bautismo"
              value={formData.fecha_bautismo || ""}
              onChange={handleInputChange}
            />
          </div>
        </div>
      </SectionCard>

      {/* Sección: Acciones */}
      <SectionCard title="Acciones">
        <div className="flex gap-3">
          <ToolbarButton 
            variant="solid"
            onClick={onSubmit}
            type="button"
          >
            {isEditing ? "Actualizar Usuario" : "Registrar Usuario"}
          </ToolbarButton>
          
          <ToolbarButton 
            variant="ghost"
            onClick={onClear}
            type="button"
          >
            Limpiar Formulario
          </ToolbarButton>
        </div>
      </SectionCard>

      {/* Sección: Datos Personales */}
      <SectionCard title="Datos Personales">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <Label>Nombre</Label>
            <Input
              name="nombre"
              value={formData.nombre || ""}
              onChange={handleInputChange}
              placeholder="Ej: Carlos Sojo"
            />
          </div>
          
          <div>
            <Label>Email</Label>
            <Input
              name="email"
              type="email"
              value={formData.email || ""}
              onChange={handleInputChange}
              placeholder="correo@dominio.com"
            />
          </div>
          
          <div>
            <Label>Teléfono</Label>
            <Input
              name="telefono"
              value={formData.telefono || ""}
              onChange={handleInputChange}
              placeholder="+58 412 000 0000"
            />
          </div>
          
          <div>
            <Label>Sexo</Label>
            <Select 
              name="sexo" 
              value={formData.sexo || ""} 
              onChange={handleInputChange}
            >
              <option value="">Seleccione…</option>
              <option value="M">Masculino</option>
              <option value="F">Femenino</option>
            </Select>
          </div>
          
          <div>
            <Label>Estado civil</Label>
            <Select 
              name="estado_civil" 
              value={formData.estado_civil || ""} 
              onChange={handleInputChange}
            >
              <option value="">Seleccione…</option>
              {civil.map((c) => (
                <option key={c} value={c}>
                  {c.charAt(0).toUpperCase() + c.slice(1)}
                </option>
              ))}
            </Select>
          </div>
          
          <div>
            <Label>Edad</Label>
            <Input
              name="edad"
              type="number"
              value={formData.edad ?? ""}
              onChange={handleInputChange}
              placeholder="Ej: 35"
            />
          </div>
          
          <div>
            <Label>Fecha nacimiento</Label>
            <Input
              name="fecha_nacimiento"
              type="date"
              value={formData.fecha_nacimiento || ""}
              onChange={handleInputChange}
            />
          </div>
        </div>
      </SectionCard>

      {/* Sección: Datos Congregacionales */}
      <SectionCard title="Datos Congregación / Espirituales">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <Label>Congregación</Label>
            <Input
              name="congregacion"
              value={formData.congregacion || ""}
              onChange={handleInputChange}
              placeholder="Monagas 1"
            />
          </div>
          
          <div>
            <Label>Ciudad</Label>
            <Input
              name="ciudad"
              value={formData.ciudad || ""}
              onChange={handleInputChange}
              placeholder="Maturín"
            />
          </div>
          
          <div>
            <Label>Privilegio</Label>
            <Input
              name="privilegio"
              value={formData.privilegio || ""}
              onChange={handleInputChange}
              placeholder="Publicador / SM / Anciano"
            />
          </div>
          
          <div>
            <Label>Fecha bautismo</Label>
            <Input
              name="fecha_bautismo"
              type="date"
              value={formData.fecha_bautismo || ""}
              onChange={handleInputChange}
            />
          </div>
        </div>
      </SectionCard>
    </div>
  );
}