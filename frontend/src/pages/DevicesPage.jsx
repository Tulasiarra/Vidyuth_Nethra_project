import React, { useState, useEffect } from 'react';
import { deviceApi } from '../services/api';

const deviceTypesList = [
  { type: 'AC', icon: '❄️', label: 'AC', power: 1500 },
  { type: 'Fan', icon: '🌀', label: 'Fan', power: 75 },
  { type: 'BLDC Fan', icon: '🌀', label: 'BLDC Fan', power: 28 },
  { type: 'Cooler', icon: '🌬️', label: 'Cooler', power: 200 },
  { type: 'Fridge', icon: '🧊', label: 'Fridge', power: 150 },
  { type: 'TV', icon: '📺', label: 'TV', power: 100 },
  { type: 'Light', icon: '💡', label: 'Light', power: 40 },
  { type: 'LED Light', icon: '💡', label: 'LED Light', power: 12 },
  { type: 'Washing Machine', icon: '🌊', label: 'Washing Machine', power: 500 },
  { type: 'Geyser', icon: '🔥', label: 'Geyser', power: 2500 },
  { type: 'Microwave', icon: '🔥', label: 'Microwave', power: 1200 },
  { type: 'Oven', icon: '🎛️', label: 'Oven', power: 2000 },
  { type: 'Computer', icon: '💻', label: 'Computer', power: 250 },
  { type: 'Laptop', icon: '💻', label: 'Laptop', power: 65 },
  { type: 'Monitor', icon: '🖥️', label: 'Monitor', power: 40 },
  { type: 'Router', icon: '🌐', label: 'Router', power: 15 },
  { type: 'Water Purifier', icon: '💧', label: 'Water Purifier', power: 40 },
  { type: 'Dishwasher', icon: '🍽️', label: 'Dishwasher', power: 1400 },
  { type: 'Mixer', icon: '🌪️', label: 'Mixer', power: 450 },
  { type: 'Induction Stove', icon: '🍳', label: 'Induction Stove', power: 1800 },
  { type: 'Air Purifier', icon: '🍃', label: 'Air Purifier', power: 50 },
  { type: 'Vacuum Cleaner', icon: '🧹', label: 'Vacuum Cleaner', power: 1000 },
  { type: 'Iron Box', icon: '👕', label: 'Iron Box', power: 1100 },
  { type: 'Water Pump', icon: '🚰', label: 'Water Pump', power: 750 }
];

const rooms = ['Living Room', 'Bedroom', 'Kitchen', 'Bathroom', 'Utility', 'Study', 'Garage'];

export default function DevicesPage({ t, selectedHome }) {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedType, setSelectedType] = useState(null);
  const [selectedRoom, setSelectedRoom] = useState('Living Room');
  const [customName, setCustomName] = useState('');
  const [brand, setBrand] = useState('');
  const [model, setModel] = useState('');
  const [ratedWatts, setRatedWatts] = useState(100);

  const fetchDevices = async () => {
    if (!selectedHome) return;
    setLoading(true);
    try {
      const list = await deviceApi.getDevices(selectedHome.id);
      setDevices(list);
    } catch (err) {
      console.error("Failed to load devices:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, [selectedHome]);

  const handleToggle = async (id, currentStatus) => {
    const nextStatus = currentStatus === 'ON' ? 'OFF' : 'ON';
    // Optimistic UI update
    setDevices(prev => prev.map(d => 
      d.id === id ? { ...d, status: nextStatus } : d
    ));
    
    try {
      await deviceApi.toggleDevice(id, nextStatus);
    } catch (err) {
      console.error("Failed to toggle device:", err);
      // Revert if error
      setDevices(prev => prev.map(d => 
        d.id === id ? { ...d, status: currentStatus } : d
      ));
    }
  };

  const removeDevice = async (id) => {
    const confirmed = window.confirm("Are you sure you want to remove this device?");
    if (!confirmed) return;

    setDevices(prev => prev.filter(d => d.id !== id));
    try {
      await deviceApi.deleteDevice(id);
    } catch (err) {
      console.error("Failed to delete device:", err);
      fetchDevices(); // reload
    }
  };

  const handleAddDevice = async () => {
    if (!selectedType) return;
    const typeObj = deviceTypesList.find(dt => dt.type === selectedType);
    
    const newDeviceData = {
      home_id: selectedHome.id,
      name: customName || `${brand || typeObj.label} ${typeObj.label}`,
      device_type: selectedType,
      brand: brand || 'Generic',
      model: model || 'Generic',
      room_name: selectedRoom,
      rated_watts: parseFloat(ratedWatts || typeObj.power)
    };

    try {
      const added = await deviceApi.addDevice(newDeviceData);
      setDevices(prev => [...prev, added]);
      setShowModal(false);
      setSelectedType(null);
      setCustomName('');
      setBrand('');
      setModel('');
      setRatedWatts(100);
    } catch (err) {
      console.error("Failed to add device:", err);
      alert("Error adding device: " + err.message);
    }
  };

  const handleTypeSelect = (type) => {
    setSelectedType(type);
    const typeObj = deviceTypesList.find(dt => dt.type === type);
    if (typeObj) {
      setRatedWatts(typeObj.power);
    }
  };

  // Group devices by room
  const devicesByRoom = devices.reduce((acc, d) => {
    const room = d.room_name || 'Living Room';
    if (!acc[room]) acc[room] = [];
    acc[room].push(d);
    return acc;
  }, {});

  const onCount = devices.filter(d => d.status === 'ON').length;
  const totalPower = devices.filter(d => d.status === 'ON').reduce((s, d) => s + d.rated_watts, 0);

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '50vh', alignItems: 'center', justify: 'center', color: 'var(--teal)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 36, animation: 'spin 1.5s linear infinite', marginBottom: 12 }}>⏳</div>
          <div style={{ fontSize: 13, letterSpacing: '1px' }}>Loading devices...</div>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header with stats */}
      <div className="devices-header">
        <div>
          <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700, marginBottom: 4 }}>
            Device Manager
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
            {onCount} devices active · {totalPower.toFixed(0)}W current draw · {devices.length} total registered
          </p>
        </div>
        <button className="btn-add" onClick={() => setShowModal(true)}>
          <span>+</span> {t.addDevice || 'Add Device'}
        </button>
      </div>

      {/* Quick Stats */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
        {[
          { label: 'Total Devices', value: devices.length, icon: '📱', color: 'var(--teal)' },
          { label: 'Active Now', value: onCount, icon: '✅', color: 'var(--green)' },
          { label: 'Inactive', value: devices.length - onCount, icon: '⭕', color: 'var(--text-muted)' },
          { label: 'Power Draw', value: `${totalPower.toFixed(0)}W`, icon: '⚡', color: 'var(--amber)' },
        ].map(s => (
          <div key={s.label} className="card" style={{ flex: 1, padding: '14px 16px' }}>
            <div style={{ fontSize: 20, marginBottom: 6 }}>{s.icon}</div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Devices by Room */}
      <div className="rooms-grid">
        {Object.keys(devicesByRoom).length > 0 ? (
          Object.entries(devicesByRoom).map(([room, roomDevices]) => (
            <div key={room} className="room-section">
              <div className="card">
                <div className="room-label">🏠 {room} · {roomDevices.length} device{roomDevices.length !== 1 ? 's' : ''}</div>
                <div className="devices-grid">
                  {roomDevices.map(device => {
                    const devTypeObj = deviceTypesList.find(dt => dt.type === device.device_type) || { icon: '⚡' };
                    const isDeviceOn = device.status === 'ON';
                    return (
                      <div key={device.id} className={`device-card ${isDeviceOn ? 'on' : 'off'}`}>
                        <button className="device-remove" onClick={() => removeDevice(device.id)}>✕</button>
                        <div className="device-card-icon">{devTypeObj.icon}</div>
                        <div className="device-card-name" style={{ fontSize: 13 }}>{device.name}</div>
                        <div className="device-card-room" style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 8 }}>
                          {device.brand} {device.model}
                        </div>
                        <div className="device-card-power">{device.rated_watts}W</div>
                        <div className="device-toggle">
                          <span className={`status-label ${isDeviceOn ? 'on' : 'off'}`}>
                            {isDeviceOn ? 'ON' : 'OFF'}
                          </span>
                          <div
                            className={`toggle-switch ${isDeviceOn ? 'on' : 'off'}`}
                            onClick={() => handleToggle(device.id, device.status)}
                          >
                            <div className="toggle-thumb"></div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div style={{ textAlign: 'center', padding: 40 }} className="card">
            <div style={{ fontSize: 48, marginBottom: 12 }}>🔌</div>
            <h3 style={{ marginBottom: 6 }}>No Devices Added Yet</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>Register your household devices to start monitoring their energy load.</p>
            <button className="btn-add" style={{ margin: '0 auto' }} onClick={() => setShowModal(true)}>Add Your First Device</button>
          </div>
        )}
      </div>

      {/* Add Device Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={e => { if (e.target === e.currentTarget) setShowModal(false); }}>
          <div className="modal" style={{ width: 500, maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <div className="modal-title">Add New Device</div>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 11, color: 'var(--text-secondary)', display: 'block', marginBottom: 8, fontWeight: 600 }}>SELECT DEVICE TYPE</label>
              <div className="modal-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', gap: 8, maxHeight: 200, overflowY: 'auto', padding: 4 }}>
                {deviceTypesList.map(dt => (
                  <button
                    key={dt.type}
                    className={`device-type-btn ${selectedType === dt.type ? 'selected' : ''}`}
                    onClick={() => handleTypeSelect(dt.type)}
                    style={{ padding: '8px 4px', fontSize: 11 }}
                  >
                    <span style={{ fontSize: 18, marginBottom: 2 }}>{dt.icon}</span>
                    {dt.label}
                  </button>
                ))}
              </div>
            </div>

            {selectedType && (
              <div style={{
                marginBottom: 16,
                padding: '12px 14px',
                background: 'rgba(20, 185, 129, 0.08)',
                border: '1px dashed var(--green)',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 12
              }}>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--green)', marginBottom: 2 }}>🔗 Bluetooth Remote Sync</div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Demo of future feature: Auto-configure brand, model & control via remote.</div>
                </div>
                <button
                  type="button"
                  onClick={() => alert("This feature will allow you to connect the device via Bluetooth and use it as a remote in the future.")}
                  style={{
                    padding: '6px 12px',
                    background: 'var(--teal-glow)',
                    border: '1px solid var(--border-active)',
                    borderRadius: 6,
                    color: 'var(--teal)',
                    fontSize: 11,
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Connect
                </button>
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="form-group">
                <label className="form-label">Brand</label>
                <input className="form-input" placeholder="e.g. Havells" value={brand} onChange={e => setBrand(e.target.value)} />
              </div>
              <div className="form-group">
                <label className="form-label">Model</label>
                <input className="form-input" placeholder="e.g. X10" value={model} onChange={e => setModel(e.target.value)} />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="form-group">
                <label className="form-label">Rated Watts (W)</label>
                <input 
                  className="form-input" 
                  type="number" 
                  value={ratedWatts} 
                  onChange={e => setRatedWatts(e.target.value)} 
                />
              </div>
              <div className="form-group">
                <label className="form-label">Room</label>
                <select
                  className="form-input"
                  value={selectedRoom}
                  onChange={e => setSelectedRoom(e.target.value)}
                  style={{ cursor: 'pointer' }}
                >
                  {rooms.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Custom Device Name (optional)</label>
              <input
                className="form-input"
                placeholder="e.g. Living Room Smart AC"
                value={customName}
                onChange={e => setCustomName(e.target.value)}
              />
            </div>

            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
              <button
                className="btn-primary btn-confirm"
                onClick={handleAddDevice}
                disabled={!selectedType}
                style={{ opacity: selectedType ? 1 : 0.5 }}
              >
                Add Device
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
