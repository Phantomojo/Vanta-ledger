import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { loginUser, getCurrentUser } from '../api';

interface User {
  id: number;
  username: string;
  email: string;
  name: string;
  role: string;
  status: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is already logged in on app start
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('jwt_token');
      if (token) {
        try {
          const userData: any = await getCurrentUser();
          // Transform the user data to match our interface
          if (userData && userData.username && userData.id) {
            setUser({
              id: userData.id,
              username: userData.username,
              email: userData.email ?? "",
              name: userData.name ?? userData.username,
              role: userData.role ?? 'user',
              status: userData.status ?? 'active'
            });
          } else {
            // Invalid user payload; clear auth
            localStorage.removeItem('jwt_token');
            setUser(null);
            setError('Invalid user profile received. Please sign in again.');
          }
        } catch (err) {
          // Token is invalid, remove it
          localStorage.removeItem('jwt_token');
        }
      }
      setIsLoading(false);
    };

    checkAuthStatus();
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await loginUser(username, password);
      const { access_token, user: userData } = response;
      
      // Store the token
      localStorage.setItem('jwt_token', access_token);
      
      // Transform and set user data
      if (!userData.id) {
        throw new Error('Invalid user data received from server');
      }
      setUser({
        id: userData.id,
        username: userData.username,
        email: userData.email ?? "",
        name: userData.name ?? userData.username,
        role: userData.role ?? 'user',
        status: userData.status ?? 'active'
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || err.message || 'Login failed. Please try again.';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('jwt_token');
    setUser(null);
    setError(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    error
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 