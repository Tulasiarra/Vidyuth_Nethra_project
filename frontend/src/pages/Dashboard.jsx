import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { energyApi } from '../services/api';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'var(--bg-card)', border: '1px solid var(--border)',
        borderRadius: 8, padding: '10px 14px', fontSize: 12
      }}>
        <div style={{ color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
        {payload.map(p => (
          <div key={p.name} style={{ color: p.color, fontWeight: 600 }}>
            {p.name}: {p.value} kWh
          </div>
        ))}
      </div>
    );
  }
  return null;
};

const MiniSparkline = ({ color }) => {
  const data = Array.from({ length: 8 }, (_, i) => ({
    v: Math.random() * 30 + 20
  }));
  return (
    <div className="mini-chart">
      <ResponsiveContainer width="100%" height={40}>
        <LineChart data={data}>
          <Line type="monotone" dataKey="v" stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default function Dashboard({ t, selectedHome, homesList, setSelectedHome }) {
  const [animIn, setAnimIn] = useState(false);
  const [loading, setLoading] = useState(true);
  const [summaryData, setSummaryData] = useState(null);
  const [hourlyData, setHourlyData] = useState([]);
  const [predictionData, setPredictionData] = useState(null);
  const [recos, setRecos] = useState([]);

  useEffect(() => {
    setAnimIn(true);
  }, []);

  useEffect(() => {
    if (!selectedHome) return;
    
    const loadDashboardData = async () => {
      setLoading(true);
      try {
        const [summary, hourly, pred, rec] = await Promise.all([
          energyApi.getEnergySummary(selectedHome.id),
          energyApi.getHourlyUsage(selectedHome.id),
          energyApi.getPredictions(selectedHome.id),
          energyApi.getRecommendations(selectedHome.id)
        ]);
        
        setSummaryData(summary);
        setHourlyData(hourly);
        setPredictionData(pred);
        setRecos(rec.slice(0, 3)); // show top 3 recommendations
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    };
    
    loadDashboardData();
  }, [selectedHome]);

  if (loading || !summaryData || !predictionData) {
    return (
      <div style={{ display: 'flex', height: '60vh', alignItems: 'center', justifyContent: 'center', color: 'var(--teal)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 36, animation: 'spin 1.5s linear infinite', marginBottom: 12 }}>⏳</div>
          <div style={{ fontSize: 13, letterSpacing: '1px', textTransform: 'uppercase' }}>Fetching live metrics...</div>
        </div>
      </div>
    );
  }

  // Calculate statistics
  const stats = [
    {
      label: t.totalConsumption, value: `${summaryData.today.energy_kwh}`, unit: 'kWh',
      sub: t.today, trend: '+2.3%', color: '#14b8a6'
    },
    {
      label: t.predictedUsage, value: `${predictionData.tomorrow.energy_kwh}`, unit: 'kWh',
      sub: 'Tomorrow', trend: '-1.1%', color: '#3b82f6'
    },
    {
      label: t.estimatedBill, value: `₹${summaryData.monthly.cost}`, unit: '',
      sub: 'This Month', trend: `Target: ₹${summaryData.target_bill}`, color: '#f59e0b'
    },
    {
      label: t.totalSavings, value: `₹${Math.max(0, summaryData.target_bill - summaryData.monthly.cost)}`, unit: '',
      sub: 'This Month Budget Surplus', trend: `Target: ₹${summaryData.target_bill}`, color: '#10b981'
    },
  ];

  // Format device breakdown to match the top devices view (Today's dynamic breakdown)
  const totalTodayEnergy = summaryData.today_device_breakdown ? summaryData.today_device_breakdown.reduce((sum, d) => sum + d.energy_kwh, 0) : 1.0;
  
  const formattedDevices = (summaryData.today_device_breakdown || []).map((d, index) => {
    const usage = d.energy_kwh;
    const pct = Math.round((usage / (totalTodayEnergy || 1.0)) * 100) || 0;
    const colors = ["#3b82f6", "#f59e0b", "#06b6d4", "#8b5cf6", "#ec4899", "#10b981"];
    const icons = {
      "AC": "❄️", "Fan": "🌀", "BLDC Fan": "🌀", "Light": "💡", "LED Light": "💡",
      "Fridge": "🧊", "TV": "📺", "Geyser": "🔥", "Water Heater": "🔥",
      "Washing Machine": "🌀", "Router": "🌐", "Computer": "💻", "Laptop": "💻"
    };
    return {
      name: d.device_name,
      type: d.device_type,
      usage: usage,
      percent: pct,
      icon: icons[d.device_type] || "⚡",
      color: colors[index % colors.length]
    };
  }).sort((a,b) => b.usage - a.usage).slice(0, 5); // top 5 devices

  return (
    <div style={{ opacity: animIn ? 1 : 0, transition: 'opacity 0.4s ease' }}>
      {/* Header */}
      <div className="page-header">
        <h1>Welcome to {selectedHome.name} 👋</h1>
        <p>{selectedHome.location} | Electricity Rate: ₹{selectedHome.electricity_rate}/kWh</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {stats.map((s, i) => (
          <div key={i} className="stat-card" style={{ animationDelay: `${i * 0.08}s` }}>
            <div className="stat-label">{s.label}</div>
            <div className="stat-value" style={{ color: s.color }}>
              {s.value}<span style={{ fontSize: 14, marginLeft: 2 }}>{s.unit}</span>
            </div>
            <div className="stat-sub">{s.sub}</div>
            <MiniSparkline color={s.color} />
            <div className="stat-trend" style={{ marginTop: 6, color: 'var(--text-muted)', fontSize: 11 }}>
              {s.trend}
            </div>
          </div>
        ))}
      </div>

      {/* Main Grid */}
      <div className="content-grid">
        {/* Usage Chart */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t.currentUsageOverview} (kWh)</div>
            <div style={{ display: 'flex', gap: 16 }}>
              <div className="legend-item"><div className="legend-dot" style={{ background: '#14b8a6' }}></div>{t.today}</div>
              <div className="legend-item"><div className="legend-dot" style={{ background: '#475569' }}></div>{t.yesterday}</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} unit=" kWh" />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="today" stroke="#14b8a6" strokeWidth={2.5} dot={false} name="Today" />
              <Line type="monotone" dataKey="yesterday" stroke="#475569" strokeWidth={1.5} dot={false} strokeDasharray="4 4" name="Yesterday" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top Devices */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t.topConsumingDevices} (Today)</div>
          </div>
          <div className="device-list">
            {formattedDevices.map((d, i) => (
              <div key={i} className="device-item">
                <div className="device-icon">{d.icon}</div>
                <div className="device-info">
                  <div className="device-name" style={{ fontSize: 12 }}>
                    {d.name}
                  </div>
                  <div className="usage-bar">
                    <div className="usage-bar-fill" style={{ width: `${d.percent}%`, background: d.color }}></div>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="device-usage" style={{ fontSize: 12 }}>{d.usage.toFixed(1)} kWh</div>
                  <div className="device-pct" style={{ fontSize: 10 }}>{d.percent}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header">
          <div className="card-title">🤖 AI Energy Insights & Recommendations</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: recos.length > 0 ? `repeat(${recos.length}, 1fr)` : '1fr', gap: 12 }}>
          {recos.length > 0 ? (
            recos.map((r, index) => {
              const bgColors = ["rgba(20,185,129,0.1)", "rgba(245,158,11,0.1)", "rgba(59,130,246,0.1)"];
              const borderColors = ["#10b981", "#f59e0b", "#3b82f6"];
              const icons = ["💡", "⚡", "🔋"];
              return (
                <div key={r.id} className="reco-card" style={{ borderLeft: `3px solid ${borderColors[index % 3]}` }}>
                  <div className="reco-icon" style={{ background: bgColors[index % 3], color: borderColors[index % 3] }}>
                    {icons[index % 3]}
                  </div>
                  <div className="reco-content">
                    <div className="reco-msg" style={{ fontSize: 12, minHeight: 40 }}>{r.message}</div>
                    <div className="reco-saving" style={{ background: bgColors[index % 3], color: borderColors[index % 3] }}>
                      Potential Saving: ₹{r.potential_saving}
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div style={{ textAlign: 'center', padding: 20, color: 'var(--text-muted)' }}>
              No active recommendations at the moment. Your usage is optimal!
            </div>
          )}
        </div>
      </div>

      {/* Bottom Grid */}
      <div className="bottom-grid">
        {/* My Homes */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">🏘️ {t.myHomes}</div>
          </div>
          <div className="homes-list">
            {homesList.map(h => (
              <div 
                key={h.id} 
                className={`home-item ${selectedHome?.id === h.id ? 'selected' : ''}`}
                onClick={() => setSelectedHome(h)}
              >
                <div className="home-thumb">🏡</div>
                <div className="home-item-info">
                  <div className="home-item-name">{h.name}</div>
                  <div className="home-item-loc">{h.location}</div>
                </div>
                <div className="status-pill">Active</div>
              </div>
            ))}
          </div>
        </div>

        {/* Home Stats */}
        <div className="card">
          <div className="card-header">
            <div className="card-title">📊 Home Insights</div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border)', paddingBottom: 10 }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Home Type</div>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{selectedHome.home_type}</div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border)', paddingBottom: 10 }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Top Consuming Device</div>
              <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--amber)' }}>{summaryData.top_consuming_device.name}</div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border)', paddingBottom: 10 }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Electricity Tariff</div>
              <div style={{ fontWeight: 600, fontSize: 13 }}>₹{selectedHome.electricity_rate}/kWh</div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Target Monthly Budget</div>
              <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--teal)' }}>₹{selectedHome.target_monthly_bill}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
