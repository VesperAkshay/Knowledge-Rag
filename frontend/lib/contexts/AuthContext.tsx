"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  user_id: string;
  username: string;
}

interface Credentials {
  google_api_key: string;
  chromadb_api_key: string;
  chromadb_tenant: string;
  chromadb_database: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  hasCredentials: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  saveCredentials: (creds: Credentials) => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE = 'http://localhost:8000';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [hasCredentials, setHasCredentials] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/me`, {
        credentials: 'include'
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);

        // Check if user has credentials
        const credsResponse = await fetch(`${API_BASE}/api/auth/credentials`, {
          credentials: 'include'
        });

        if (credsResponse.ok) {
          const credsData = await credsResponse.json();
          setHasCredentials(credsData.has_credentials || false);
        }
      } else {
        setUser(null);
        setHasCredentials(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      setHasCredentials(false);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const register = async (username: string, password: string) => {
    const response = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data = await response.json();
    
    // Auto-login after registration
    await login(username, password);
  };

  const login = async (username: string, password: string) => {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    setUser({ user_id: data.user_id, username: data.username });
    setHasCredentials(false); // Will be checked on settings page
  };

  const logout = async () => {
    await fetch(`${API_BASE}/api/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    });

    setUser(null);
    setHasCredentials(false);
  };

  const saveCredentials = async (creds: Credentials) => {
    const response = await fetch(`${API_BASE}/api/auth/credentials`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(creds),
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save credentials');
    }

    setHasCredentials(true);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        hasCredentials,
        isLoading,
        login,
        register,
        logout,
        saveCredentials,
        checkAuth
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
