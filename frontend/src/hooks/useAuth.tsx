export function useAuth() { 
  return { 
    user: { 
      id: "1", 
      email: "admin@nexo.com", 
      firstName: "Admin", 
      lastName: "User", 
      isActive: true, 
      createdAt: "2024-01-01" 
    }, 
    isAuthenticated: true, 
    isLoading: false, 
    login: async () => {}, 
    logout: () => {} 
  }; 
} 
export function AuthProvider({ children }: { children: React.ReactNode }) { 
  return <>{children}</>; 
}
