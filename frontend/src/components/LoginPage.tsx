import React from 'react';
import { Card } from './ui/Card';
import { LoginForm } from './LoginForm';

interface LoginPageProps {
  onLoginSuccess?: () => void;
}

export function LoginPage({ onLoginSuccess }: LoginPageProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e293b] to-[#0f172a] flex items-center justify-center p-4">
      {/* Fondo decorativo */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"></div>
      </div>
      
      {/* Contenedor principal */}
      <div className="relative w-full max-w-md">
        <Card className="backdrop-blur-sm bg-[#111827]/80 border-[#1f2937]/50">
          <LoginForm onSuccess={onLoginSuccess} />
        </Card>
        
        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-slate-500">
            © 2024 Nexo PPEAM. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </div>
  );
}