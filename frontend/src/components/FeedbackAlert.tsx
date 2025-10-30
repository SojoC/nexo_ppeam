import React from "react";

// ==========================
// FeedbackAlert — Componente para mostrar mensajes de éxito/error
// - Diseño consistente con el tema dark
// - Iconos apropiados para cada tipo de mensaje
// - Auto-dismiss opcional
// ==========================

type AlertType = "success" | "error" | "info" | "warning";

interface FeedbackAlertProps {
  type: AlertType;
  message: string;
  onClose?: () => void;
  autoClose?: boolean;
  duration?: number; // en milisegundos
}

function AlertIcon({ type }: { type: AlertType }) {
  const iconClasses = "w-5 h-5";
  
  switch (type) {
    case "success":
      return (
        <svg className={`${iconClasses} text-green-400`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      );
    case "error":
      return (
        <svg className={`${iconClasses} text-red-400`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      );
    case "warning":
      return (
        <svg className={`${iconClasses} text-amber-400`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      );
    case "info":
    default:
      return (
        <svg className={`${iconClasses} text-blue-400`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
  }
}

export default function FeedbackAlert({
  type,
  message,
  onClose,
  autoClose = false,
  duration = 5000
}: FeedbackAlertProps) {
  
  // Auto-close timer
  React.useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [autoClose, onClose, duration]);
  
  const alertStyles = {
    success: "bg-green-900/20 border-green-700/30 text-green-200",
    error: "bg-red-900/20 border-red-700/30 text-red-200",
    warning: "bg-amber-900/20 border-amber-700/30 text-amber-200",
    info: "bg-blue-900/20 border-blue-700/30 text-blue-200",
  };

  return (
    <div className={`
      rounded-xl border p-4 mb-6 flex items-start space-x-3
      ${alertStyles[type]}
    `}>
      <div className="flex-shrink-0 mt-0.5">
        <AlertIcon type={type} />
      </div>
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">
          {message}
        </p>
      </div>
      
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 text-slate-400 hover:text-slate-200 transition-colors"
          aria-label="Cerrar alerta"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}