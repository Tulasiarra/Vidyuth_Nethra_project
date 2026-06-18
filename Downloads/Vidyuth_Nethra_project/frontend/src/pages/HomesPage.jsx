import React, { useState } from 'react';
import { homeApi } from '../services/api';

export default function HomesPage({ t, homesList, fetchHomes, selectedHome, setSelectedHome }) {
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [rate, setRate] = useState(7.0);
  const [targetBill, setTargetBill] = useState(3000);
  const [homeType, setHomeType] = useState('Apartment');
  const [submitting, setSubmitting] = useState(false);

  const handleCreateHome = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const newHome = await homeApi.createHome({
        name,
        location: location || "Bangalore, India",
        electricity_rate: parseFloat(rate),
        target_monthly_bill: parseFloat(targetBill),
        home_type: homeType
      });
      await fetchHomes();
      setSelectedHome(newHome);
      setShowModal(false);
      setName('');
      setLocation('');
      setRate(7.0);
      setTargetBill(3000);
      setHomeType('Apartment');
    } catch (err) {
      console.error("Failed to create home:", err);
      alert("Error creating home: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteHome = async (e, homeId) => {
    e.stopPropagation(); // Prevent selection
    const confirmed = window.confirm("Are you sure you want to delete this home and all its devices? This action is permanent.");
    if (!confirmed) return;
    
    try {
      await homeApi.deleteHome(homeId);
      await fetchHomes();
      if (selectedHome?.id === homeId) {
        setSelectedHome(null);
      }
    } catch (err) {
      console.error("Failed to delete home:", err);
      alert("Error deleting home: " + err.message);
    }
  };

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>🏘️ {t.myHomes}</h1>
          <p>Manage and monitor all your smart homes</p>
        </div>
        <button className="btn-add" onClick={() => setShowModal(true)}>
          <span>+</span> Add Home
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
        {homesList.map(h => (
          <div
            key={h.id}
            className="card"
            style={{ 
              cursor: 'pointer', 
              border: selectedHome?.id === h.id ? '1px solid var(--teal)' : '1px solid var(--border)', 
              transition: 'all 0.2s',
              position: 'relative'
            }}
            onClick={() => setSelectedHome(h)}
          >
            {/* Delete button */}
            <button 
              onClick={(e) => handleDeleteHome(e, h.id)}
              style={{
                position: 'absolute', top: 12, right: 12,
                background: 'transparent', color: 'var(--red)', fontSize: 13,
                opacity: 0.7, border: 'none', cursor: 'pointer'
              }}
              title="Delete home"
            >
              ✕ Delete
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
              <div style={{ width: 64, height: 48, borderRadius: 10, background: 'linear-gradient(135deg, #1e3a5f, #0d2137)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28 }}>
                {h.home_type === 'Office' ? '🏢' : h.home_type === 'Villa' ? '🏡' : '🏠'}
              </div>
              <div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 700 }}>{h.name}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>📍 {h.location}</div>
              </div>
              {selectedHome?.id === h.id && (
                <div className="status-pill" style={{ marginLeft: 'auto', marginRight: 40 }}>Active</div>
              )}
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              <div style={{ padding: '10px 12px', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>⚡ Tariff Rate</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--teal)' }}>₹{h.electricity_rate}/kWh</div>
              </div>
              <div style={{ padding: '10px 12px', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border)' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>💰 Monthly Target</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--teal)' }}>₹{h.target_monthly_bill}</div>
              </div>
            </div>
          </div>
        ))}

        <div 
          className="card" 
          style={{ cursor: 'pointer', border: '1px dashed var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 160 }}
          onClick={() => setShowModal(true)}
        >
          <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: 36, marginBottom: 10 }}>+</div>
            <div style={{ fontSize: 14, fontWeight: 500 }}>Add New Home</div>
            <div style={{ fontSize: 12, marginTop: 4 }}>Connect another smart home</div>
          </div>
        </div>
      </div>

      {/* Add Home Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={e => { if (e.target === e.currentTarget) setShowModal(false); }}>
          <form className="modal" onSubmit={handleCreateHome} style={{ width: 440 }}>
            <div className="modal-header">
              <div className="modal-title">Add Smart Home</div>
              <button type="button" className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div className="form-group">
              <label className="form-label">Home Name</label>
              <input 
                className="form-input" 
                placeholder="e.g. My Flat, Parents Home, Office" 
                value={name} 
                onChange={e => setName(e.target.value)} 
                required 
              />
            </div>

            <div className="form-group">
              <label className="form-label">Location / Address</label>
              <input 
                className="form-input" 
                placeholder="e.g. Bangalore, Karnataka" 
                value={location} 
                onChange={e => setLocation(e.target.value)} 
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="form-group">
                <label className="form-label">Electricity Rate (₹/kWh)</label>
                <input 
                  className="form-input" 
                  type="number" 
                  step="0.05"
                  value={rate} 
                  onChange={e => setRate(e.target.value)} 
                  required 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Target Bill (₹/month)</label>
                <input 
                  className="form-input" 
                  type="number" 
                  value={targetBill} 
                  onChange={e => setTargetBill(e.target.value)} 
                  required 
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Home Type</label>
              <select 
                className="form-input"
                value={homeType} 
                onChange={e => setHomeType(e.target.value)}
              >
                <option value="Apartment">Apartment</option>
                <option value="Villa">Villa</option>
                <option value="Independent House">Independent House</option>
                <option value="Office">Office</option>
              </select>
            </div>

            <div className="modal-actions" style={{ marginTop: 24 }}>
              <button type="button" className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
              <button 
                type="submit" 
                className="btn-primary btn-confirm"
                disabled={submitting}
              >
                {submitting ? 'Creating...' : 'Create Home'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
