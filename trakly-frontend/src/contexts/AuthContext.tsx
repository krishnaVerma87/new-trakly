import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import { authService } from '@/lib/services/auth.service';
import { UserWithRolesResponse, LoginRequest } from '@/types';

interface AuthContextType {
  user: UserWithRolesResponse | null;
  loading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserWithRolesResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Auto-fetch user if token exists
    const token = localStorage.getItem('access_token');
    if (token) {
      authService
        .getCurrentUser()
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('access_token');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (data: LoginRequest) => {
    const response = await authService.login(data);
    localStorage.setItem('access_token', response.access_token);
    setUser(response.user as UserWithRolesResponse);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    authService.logout().catch(() => {}); // Fire and forget
  };

  const refreshUser = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      const response = await authService.getCurrentUser();
      setUser(response.data);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        refreshUser,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
