import React, { useState } from 'react';


const pageTitles = {
  dashboard: 'Dashboard',
  homes: 'My Homes',
  devices: 'Devices',
  energy: 'Energy Usage',
  chat: 'Chat Assistant',
  voice: 'Voice Assistant',
  reports: 'Reports',
  settings: 'Settings',
};

export default function Topbar({ t, activePage, selectedHome, user, setActivePage, homesList = [], setSelectedHome }) {
  const [showHomeMenu, setShowHomeMenu] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="topbar-title">{pageTitles[activePage] || 'Dashboard'}</div>
      </div>

      <div className="topbar-right">
        {/* Home Selector */}
        <div style={{ position: 'relative' }}>
          <div className="home-selector" onClick={() => setShowHomeMenu(v => !v)}>
            <div className="home-dot"></div>
            <span style={{ fontSize: 13, fontWeight: 500 }}>{selectedHome?.name}</span>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>▼</span>
          </div>
          {showHomeMenu && (
            <div style={{
              position: 'absolute', top: '110%', right: 0,
              background: 'var(--bg-card)', border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)', padding: '8px', minWidth: 200,
              zIndex: 100, boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
            }}>
              {homesList.map(h => (
                <div
                  key={h.id}
                  style={{
                    padding: '10px 12px', borderRadius: 8, cursor: 'pointer',
                    fontSize: 13, fontWeight: 500,
                    background: selectedHome?.id === h.id ? 'var(--teal-glow)' : 'transparent',
                    color: selectedHome?.id === h.id ? 'var(--teal)' : 'var(--text-primary)',
                    transition: 'all 0.15s'
                  }}
                  onClick={() => { 
                    setSelectedHome(h);
                    setShowHomeMenu(false); 
                  }}
                >
                  {h.home_type === 'Office' ? '🏢' : h.home_type === 'Villa' ? '🏡' : '🏠'} {h.name}
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 400 }}>{h.location}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Voice Button */}
        <button
          className="icon-btn notif-dot"
          title="Voice Assistant"
          onClick={() => setActivePage('voice')}
          style={{ fontSize: 16 }}
        >🎙️</button>

        {/* Notifications */}
        <button className="icon-btn notif-dot" title="Notifications" style={{ fontSize: 16 }}>
          🔔
        </button>

        {/* Avatar */}
        <div style={{ position: 'relative' }}>
          <div 
            className="avatar" 
            title={user.name} 
            onClick={() => setShowProfile(v => !v)}
            style={{ cursor: 'pointer', userSelect: 'none' }}
          >
            {user.avatar}
          </div>
          {showProfile && (
            <div style={{
              position: 'absolute', top: '115%', right: 0,
              background: 'var(--bg-card)', border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)', padding: '20px', minWidth: 260,
              zIndex: 200, boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
              display: 'flex', flexDirection: 'column', gap: 16
            }}>
              {/* Header with Avatar & Name */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, borderBottom: '1px solid var(--border)', paddingBottom: 12 }}>
                <div style={{
                  width: 40, height: 40, borderRadius: '50%',
                  background: 'linear-gradient(135deg, var(--teal), var(--blue))',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 14, fontWeight: 700, color: 'white'
                }}>
                  {user.avatar}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{user.name}</span>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>User Account</span>
                </div>
              </div>
              
              {/* Detailed fields: Email & House */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <span style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>📧 Email Address</span>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)', wordBreak: 'break-all' }}>{user.email}</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <span style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>🏠 Active House</span>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    {selectedHome ? `${selectedHome.name} (${selectedHome.home_type})` : 'No house selected'}
                  </span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <span style={{ fontSize: 9, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>📍 House Location</span>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{selectedHome?.location || 'N/A'}</span>
                </div>
              </div>
              
              {/* Actions */}
              <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                <button 
                  onClick={() => {
                    setActivePage('settings');
                    setShowProfile(false);
                  }}
                  style={{
                    flex: 1, padding: '8px 12px', background: 'var(--teal-glow)',
                    border: '1px solid var(--border-active)', borderRadius: 6,
                    fontSize: 12, color: 'var(--teal)', fontWeight: 600, cursor: 'pointer'
                  }}
                >
                  ⚙️ Settings
                </button>
                <button 
                  onClick={() => setShowProfile(false)}
                  style={{
                    padding: '8px 12px', background: 'rgba(255,255,255,0.05)',
                    border: '1px solid var(--border)', borderRadius: 6,
                    fontSize: 12, color: 'var(--text-secondary)', cursor: 'pointer'
                  }}
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
