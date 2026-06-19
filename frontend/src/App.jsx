import React, { useState, useEffect } from 'react';
import './index.css';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import DevicesPage from './pages/DevicesPage';
import ChatPage from './pages/ChatPage';
import VoicePage from './pages/VoicePage';
import EnergyPage from './pages/EnergyPage';
import HomesPage from './pages/HomesPage';
import SettingsPage from './pages/SettingsPage';
import ReportsPage from './pages/ReportsPage';
import Sidebar from './components/Sidebar';
import Topbar from './components/Topbar';
import { authApi, homeApi } from './services/api';
import { translations } from './data/mockData';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState({ name: '', email: '', avatar: '' });
  const [activePage, setActivePage] = useState('dashboard');
  const [homesList, setHomesList] = useState([]);
  const [selectedHome, setSelectedHome] = useState(null);
  const [language, setLanguage] = useState('en');
  const [showSignup, setShowSignup] = useState(false);
  const [loading, setLoading] = useState(true);

  const t = translations[language] || translations['en'];

  useEffect(() => {
    // Check if token exists on load
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const profile = await authApi.getProfile();
          if (profile && profile.user) {
            setUser({
              name: profile.user.name || profile.user.email.split('@')[0],
              email: profile.user.email,
              avatar: (profile.user.name || profile.user.email).substring(0, 2).toUpperCase()
            });
            setIsLoggedIn(true);
            await fetchHomes();
          } else {
            localStorage.removeItem('token');
          }
        } catch (err) {
          console.error("Token verification failed:", err);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  const fetchHomes = async () => {
    try {
      const list = await homeApi.getHomes();
      setHomesList(list);
      if (list.length > 0) {
        setSelectedHome(list[0]);
      }
    } catch (err) {
      console.error("Failed to load homes:", err);
    }
  };

  const handleLogin = async (email, password) => {
    const res = await authApi.login(email, password);
    if (res.success) {
      const profile = await authApi.getProfile();
      setUser({
        name: profile.user.name || profile.user.email.split('@')[0],
        email: profile.user.email,
        avatar: (profile.user.name || profile.user.email).substring(0, 2).toUpperCase()
      });
      setIsLoggedIn(true);
      await fetchHomes();
      setActivePage('dashboard');
    } else {
      throw new Error(res.message || "Login failed");
    }
  };

  const handleRegister = async (name, email, password) => {
    const res = await authApi.register(name, email, password);
    if (!res.success) {
      throw new Error(res.message || "Registration failed");
    }
    // Automatically switch to login screen
    setShowSignup(false);
  };

  const handleLogout = () => {
    authApi.logout();
    setIsLoggedIn(false);
    setSelectedHome(null);
    setHomesList([]);
  };

  // Enforce selecting/creating an active home after login
  useEffect(() => {
    if (isLoggedIn && !selectedHome && activePage !== 'homes' && !loading) {
      setActivePage('homes');
    }
  }, [isLoggedIn, selectedHome, activePage, loading]);

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-primary)', color: 'var(--teal)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 48, animation: 'spin 1.5s linear infinite', marginBottom: 16 }}>⏳</div>
          <div style={{ fontSize: 16, fontWeight: 500, fontFamily: 'var(--font-display)', letterSpacing: '1px' }}>LOADING VIDHYUTH NETRA...</div>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <LoginPage 
        onLogin={handleLogin} 
        onRegister={handleRegister}
        showSignup={showSignup} 
        setShowSignup={setShowSignup} 
      />
    );
  }

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard': 
        return <Dashboard t={t} selectedHome={selectedHome} language={language} homesList={homesList} setSelectedHome={setSelectedHome} />;
      case 'homes': 
        return <HomesPage t={t} homesList={homesList} fetchHomes={fetchHomes} selectedHome={selectedHome} setSelectedHome={setSelectedHome} />;
      case 'devices': 
        return <DevicesPage t={t} selectedHome={selectedHome} />;
      case 'energy': 
        return <EnergyPage t={t} selectedHome={selectedHome} />;
      case 'chat': 
        return <ChatPage t={t} language={language} selectedHome={selectedHome} />;
      case 'voice': 
        return <VoicePage t={t} selectedHome={selectedHome} />;
      case 'reports': 
        return <ReportsPage t={t} selectedHome={selectedHome} />;
      case 'settings': 
        return <SettingsPage t={t} language={language} setLanguage={setLanguage} user={user} />;
      default: 
        return <Dashboard t={t} selectedHome={selectedHome} language={language} homesList={homesList} setSelectedHome={setSelectedHome} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} setActivePage={setActivePage} t={t} language={language} setLanguage={setLanguage} onLogout={handleLogout} />
      <div className="main-content">
        <Topbar t={t} activePage={activePage} selectedHome={selectedHome} user={user} setActivePage={setActivePage} homesList={homesList} setSelectedHome={setSelectedHome} />
        <div className="page-content">{renderPage()}</div>
      </div>
    </div>
  );
}
