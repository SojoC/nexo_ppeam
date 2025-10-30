import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
	className?: string;
	children?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ className = '', children, ...rest }) => {
	return (
		<div className={`rounded-lg ${className}`} {...rest}>
			{children}
		</div>
	);
};

export default Card;
