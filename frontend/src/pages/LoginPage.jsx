import React, { useState } from 'react';

export default function LoginPage({ onLogin, onRegister, showSignup, setShowSignup }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPass, setShowPass] = useState(false);

  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (!showSignup) {
        await onLogin(email, password);
      } else {
        if (password !== confirmPassword) {
          throw new Error("Passwords do not match");
        }
        await onRegister(name, email, password);
        alert("Registration successful! Please login.");
      }
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrapper">
      <div className="login-left">
        <div className="login-brand">
          <div className="brand-icon">⚡</div>
          <div>
            <div className="brand-name">VIDHYUTH NETRA</div>
            <div className="brand-tagline">AI Smart Home Energy Optimization</div>
          </div>
        </div>
        <h1 className="login-headline">
          Smarter Energy.<br /><span>Better Tomorrow.</span>
        </h1>
        <p className="login-desc">
          Monitor, optimize and save energy with the power of AI. Get real-time insights,
          voice control, and intelligent recommendations for all your smart home devices.
        </p>

        <div style={{ display: 'flex', gap: 24, marginTop: 48 }}>
          {[
            { icon: '🤖', label: 'AI Assistant' },
            { icon: '🎙️', label: 'Voice Control' },
            { icon: '📊', label: 'Smart Insights' },
            { icon: '💰', label: 'Save Energy' },
          ].map(f => (
            <div key={f.label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, marginBottom: 6 }}>{f.icon}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>{f.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="login-right">
        <div className="login-card">
          {!showSignup ? (
            <>
              <h2>Welcome Back</h2>
              <p>Login to continue to your account</p>
              {error && <div style={{ color: 'var(--red)', background: 'rgba(239,68,68,0.1)', padding: 10, borderRadius: 6, fontSize: 13, marginBottom: 16 }}>⚠️ {error}</div>}
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input
                    className="form-input"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <div style={{ position: 'relative' }}>
                    <input
                      className="form-input"
                      type={showPass ? 'text' : 'password'}
                      placeholder="Enter your password"
                      value={password}
                      onChange={e => setPassword(e.target.value)}
                      required
                      style={{ paddingRight: 40 }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPass(v => !v)}
                      style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'transparent', color: 'var(--text-muted)', fontSize: 16 }}
                    >{showPass ? '🙈' : '👁️'}</button>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--text-secondary)', cursor: 'pointer' }}>
                    <input type="checkbox" style={{ accentColor: 'var(--teal)' }} />
                    Remember me
                  </label>
                  <a href="#" style={{ fontSize: 13, color: 'var(--teal)', textDecoration: 'none' }}>Forgot Password?</a>
                </div>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={loading}
                  style={{ opacity: loading ? 0.7 : 1 }}
                >
                  {loading ? '⏳ Logging in...' : 'Login'}
                </button>
              </form>
              <div className="login-switch">
                Don't have an account?{' '}
                <a href="#" onClick={e => { e.preventDefault(); setShowSignup(true); }}>Sign up</a>
              </div>
            </>
          ) : (
            <>
              <h2>Create Account</h2>
              <p>Join us to start your energy optimization journey</p>
              {error && <div style={{ color: 'var(--red)', background: 'rgba(239,68,68,0.1)', padding: 10, borderRadius: 6, fontSize: 13, marginBottom: 16 }}>⚠️ {error}</div>}
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input className="form-input" placeholder="Enter your full name" value={name} onChange={e => setName(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input className="form-input" type="email" placeholder="Enter your email" value={email} onChange={e => setEmail(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input className="form-input" type="password" placeholder="Create a password" value={password} onChange={e => setPassword(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Confirm Password</label>
                  <input className="form-input" type="password" placeholder="Confirm your password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} required />
                </div>
                <button type="submit" className="btn-primary" disabled={loading} style={{ opacity: loading ? 0.7 : 1 }}>
                  {loading ? '⏳ Creating...' : 'Sign Up'}
                </button>
              </form>
              <div className="login-switch">
                Already have an account?{' '}
                <a href="#" onClick={e => { e.preventDefault(); setShowSignup(false); }}>Login</a>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
