// Componentes UI reutilizables con diseño oscuro y moderno
export { Button, type ButtonVariant, type ButtonSize } from './Button.tsx';
export { Input } from './Input.tsx';

// Tipos comunes para componentes futuros
export type AlertType = 'info' | 'success' | 'warning' | 'error';

export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

