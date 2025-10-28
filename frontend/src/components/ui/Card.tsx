import React from 'react';

interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

interface CardProps extends BaseComponentProps {
  title?: string;
  description?: string;
  actions?: React.ReactNode;
  padding?: 'sm' | 'md' | 'lg';
}

export const Card: React.FC<CardProps> = ({
  title,
  description,
  actions,
  padding = 'md',
  children,
  className = ''
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };
  
  const cardClasses = [
    'bg-[#111827] rounded-2xl shadow-xl border border-[#1f2937]',
    paddingClasses[padding],
    className
  ].join(' ');
  
  return (
    <div className={cardClasses}>
      {(title || description || actions) && (
        <div className="flex justify-between items-start mb-4">
          <div>
            {title && (
              <h3 className="text-xl font-bold text-slate-200 mb-1">
                {title}
              </h3>
            )}
            {description && (
              <p className="text-sm text-slate-400">
                {description}
              </p>
            )}
          </div>
          
          {actions && (
            <div className="flex space-x-2">
              {actions}
            </div>
          )}
        </div>
      )}
      
      {children}
    </div>
  );
};