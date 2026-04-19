import React, { createContext, useContext, useState, useEffect } from 'react';
import { Preferences } from '@capacitor/preferences';
import { authService } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const { value: token } = await Preferences.get({ key: 'token' });
      if (token) {
        try {
          const res = await authService.getProfile();
          setUser(res.data);
        } catch (err) {
          await Preferences.remove({ key: 'token' });
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (credentials) => {
    const res = await authService.login(credentials);
    const { user, access_token } = res.data;
    await Preferences.set({ key: 'token', value: access_token });
    setUser(user);
    return user;
  };

  const logout = async () => {
    await Preferences.remove({ key: 'token' });
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
