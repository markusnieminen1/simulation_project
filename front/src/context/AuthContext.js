// src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [accessJwt, setAccessJwt] = useState(null);
  const [refreshJwt, setRefreshJwt] = useState(null);

  const login = (access_jwt, refresh_jwt) => {
    setAccessJwt(access_jwt);
    setRefreshJwt(refresh_jwt);

    if (!access_jwt) {
      setIsLoggedIn(false);
    } else {
      setIsLoggedIn(true);
      localStorage.setItem('access_token', access_jwt);
      localStorage.setItem('refresh_token', refresh_jwt);
    }
  };

  const logout = () => {
    setAccessJwt(null);
    setRefreshJwt(null);
    setIsLoggedIn(false);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  useEffect(() => {
    const savedAccessJwt = localStorage.getItem('access_token');
    if (savedAccessJwt) {
      setAccessJwt(savedAccessJwt);
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);