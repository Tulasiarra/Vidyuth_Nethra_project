import React from 'react';

const navItems = [
  { id: 'dashboard', icon: '🏠', labelKey: 'dashboard' },
  { id: 'homes', icon: '🏘️', labelKey: 'myHomes' },
  { id: 'devices', icon: '📱', labelKey: 'devices' },
  { id: 'energy', icon: '⚡', labelKey: 'energyUsage' },
  { id: 'chat', icon: '🤖', labelKey: 'chatAssistant' },
  { id: 'voice', icon: '🎙️', labelKey: 'voiceAssistant' },
  { id: 'reports', icon: '📊', labelKey: 'reports' },
  { id: 'settings', icon: '⚙️', labelKey: 'settings' },
];

const languages = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी' },
  { code: 'te', label: 'తెలుగు' },
];

export default function Sidebar({ activePage, setActivePage, t, language, setLanguage, onLogout }) {
  return (
    <div className="sidebar">
      <div className="sidebar-brand">
        <div className="icon">⚡</div>
        <div>
          <div className="sidebar-brand-text">VIDHYUTH NETRA</div>
          <div className="sidebar-brand-sub">AI Smart Home Energy</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">MAIN MENU</div>
        {navItems.map(item => (
          <div
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => setActivePage(item.id)}
          >
            <div className="nav-icon">{item.icon}</div>
            <span>{t[item.labelKey] || item.labelKey}</span>
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="lang-selector">
          <span>🌍</span>
          <span style={{ fontSize: 12 }}>{t.language || 'Language'}</span>
          <select
            className="lang-select"
            value={language}
            onChange={e => setLanguage(e.target.value)}
          >
            {languages.map(l => (
              <option key={l.code} value={l.code}>{l.label}</option>
            ))}
          </select>
        </div>
        <button className="logout-btn" onClick={onLogout}>
          <span>🚪</span>
          <span>{t.logout || 'Logout'}</span>
        </button>
      </div>
    </div>
  );
}
