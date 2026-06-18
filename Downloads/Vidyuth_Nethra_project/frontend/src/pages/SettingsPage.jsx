import React, { useState } from 'react';

const Toggle = ({ value, onChange }) => (
  <div className={`toggle-switch ${value ? 'on' : ''}`} onClick={() => onChange(!value)} style={{ cursor: 'pointer' }}>
    <div className="toggle-thumb" />
  </div>
);

export default function SettingsPage({ t, language, setLanguage, user }) {
  const [notifications, setNotifications] = useState(true);
  const [anomalyAlerts, setAnomalyAlerts] = useState(true);
  const [weeklyReport, setWeeklyReport] = useState(false);
  const [darkMode] = useState(true);

  return (
    <div>
      <div className="page-header">
        <h1>⚙️ {t.settings}</h1>
        <p>Manage your account and app preferences</p>
      </div>
      <div style={{ maxWidth: 600, display: 'flex', flexDirection: 'column', gap: 20 }}>
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>👤 Profile</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 8 }}>
            <div style={{ width: 56, height: 56, borderRadius: 16, background: 'linear-gradient(135deg, var(--teal), var(--blue))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, fontWeight: 700 }}>
              {user.avatar || 'UN'}
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 600 }}>{user.name || 'User'}</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{user.email}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 4 }}>🔔 Notifications</div>
          {[
            { label: 'Weekly Reports', sub: 'Email report every Monday', value: weeklyReport, fn: setWeeklyReport },
          ].map(s => (
            <div key={s.label} className="settings-row">
              <div>
                <div className="settings-row-label">{s.label}</div>
                <div className="settings-row-sub">{s.sub}</div>
              </div>
              <Toggle value={s.value} onChange={s.fn} />
            </div>
          ))}
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 12 }}>🌍 Language & Region</div>
          <div className="settings-row">
            <div>
              <div className="settings-row-label">App Language</div>
              <div className="settings-row-sub">Changes UI and AI responses</div>
            </div>
            <select value={language} onChange={e => setLanguage(e.target.value)} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text-primary)', fontSize: 13, padding: '6px 10px', cursor: 'pointer' }}>
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="te">తెలుగు</option>
            </select>
          </div>
          <div className="settings-row">
            <div>
              <div className="settings-row-label">Currency</div>
              <div className="settings-row-sub">For energy bill estimates</div>
            </div>
            <select style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: 6, color: 'var(--text-primary)', fontSize: 13, padding: '6px 10px', cursor: 'pointer' }}>
              <option>₹ INR</option>
              <option>$ USD</option>
              <option>€ EUR</option>
            </select>
          </div>
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 12 }}>🎨 Appearance</div>
          <div className="settings-row">
            <div>
              <div className="settings-row-label">Dark Mode</div>
              <div className="settings-row-sub">Uses less energy on OLED screens</div>
            </div>
            <Toggle value={darkMode} onChange={() => {}} />
          </div>
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 12 }}>ℹ️ About</div>
          {[
            { label: 'App Version', value: '1.0.0' },
            { label: 'AI Model', value: 'Vidhyuth AI v2' },
            { label: 'Data Updated', value: 'June 17, 2026' },
          ].map(s => (
            <div key={s.label} className="settings-row">
              <div className="settings-row-label">{s.label}</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{s.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
