export type MessageType = "success" | "error" | "info" | "warning";

export interface FeedbackAlertProps {
  message: string;
  type: MessageType;
  onClose: () => void;
}

export function FeedbackAlert({ message, type, onClose }: FeedbackAlertProps) {
  if (!message) return null;

  const getAlertStyles = () => {
    const baseStyles = "mb-4 px-4 py-3 rounded-md border transition-all duration-300";
    
    switch (type) {
      case "success":
        return `${baseStyles} bg-green-900/20 border-green-600 text-green-300`;
      case "error":
        return `${baseStyles} bg-red-900/20 border-red-600 text-red-300`;
      case "warning":
        return `${baseStyles} bg-yellow-900/20 border-yellow-600 text-yellow-300`;
      case "info":
      default:
        return `${baseStyles} bg-blue-900/20 border-blue-600 text-blue-300`;
    }
  };

  const getIcon = () => {
    switch (type) {
      case "success":
        return (
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case "error":
        return (
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case "warning":
        return (
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case "info":
      default:
        return (
          <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  return (
    <div className={getAlertStyles()}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium">{message}</p>
        </div>
        <div className="flex-shrink-0 ml-4">
          <button
            onClick={onClose}
            className="inline-flex text-gray-400 hover:text-gray-200 focus:outline-none focus:text-gray-200 transition-colors duration-150"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
