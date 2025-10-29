import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helpText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helpText,
  leftIcon,
  rightIcon,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  const inputClasses = [
    'w-full bg-[#0f172a] border rounded-xl px-3 py-2 text-slate-200 placeholder-slate-500 transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
    error ? 'border-red-500' : 'border-[#334155]',
    leftIcon ? 'pl-7' : '',
    rightIcon ? 'pr-7' : '',
    className
  ].join(' ');
  
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-slate-200 mb-1">
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none text-slate-400">
            {leftIcon}
          </div>
        )}
        
        <input
          id={inputId}
          className={inputClasses}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-slate-400">
            {rightIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p className="mt-1 text-sm text-red-400">{error}</p>
      )}
      
      {helpText && !error && (
        <p className="mt-1 text-sm text-slate-400">{helpText}</p>
      )}
    </div>
  );
};