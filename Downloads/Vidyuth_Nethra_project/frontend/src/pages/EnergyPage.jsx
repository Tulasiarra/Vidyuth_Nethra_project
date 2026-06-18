import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';
import { energyApi } from '../services/api';

const COLORS = ['#14b8a6', '#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];

export default function EnergyPage({ t, selectedHome }) {
  const [activeTab, setActiveTab] = useState('hourly');
  const [pieTab, setPieTab] = useState('today');
  const [training, setTraining] = useState(false);
  const [trainingMessage, setTrainingMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [hourlyData, setHourlyData] = useState([]);
  const [summaryData, setSummaryData] = useState(null);
  const [predictionData, setPredictionData] = useState(null);

  const handleRetrain = async () => {
    setTraining(true);
    setTrainingMessage('Initiating training...');
    try {
      const res = await energyApi.trainModel(selectedHome.id);
      if (res.success) {
        setTrainingMessage('Model trained successfully!');
        // Reload predictions after training
        const pred = await energyApi.getPredictions(selectedHome.id);
        setPredictionData(pred);
      } else {
        setTrainingMessage('Training skipped: ' + res.message);
      }
    } catch (err) {
      console.error(err);
      setTrainingMessage('Training failed.');
    } finally {
      setTimeout(() => {
        setTraining(false);
        setTrainingMessage('');
      }, 3500);
    }
  };

  useEffect(() => {
    if (!selectedHome) return;
    
    const loadEnergyData = async () => {
      setLoading(true);
      try {
        const [hourly, summary, pred] = await Promise.all([
          energyApi.getHourlyUsage(selectedHome.id),
          energyApi.getEnergySummary(selectedHome.id),
          energyApi.getPredictions(selectedHome.id)
        ]);
        
        setHourlyData(hourly);
        setSummaryData(summary);
        setPredictionData(pred);
      } catch (err) {
        console.error("Failed to load energy data:", err);
      } finally {
        setLoading(false);
      }
    };
    
    loadEnergyData();
  }, [selectedHome]);

  if (loading || !summaryData || !predictionData) {
    return (
      <div style={{ display: 'flex', height: '50vh', alignItems: 'center', justifyContent: 'center', color: 'var(--teal)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 36, animation: 'spin 1.5s linear infinite', marginBottom: 12 }}>⏳</div>
          <div style={{ fontSize: 13, letterSpacing: '1px' }}>Analyzing consumption patterns...</div>
        </div>
      </div>
    );
  }

  // Detailed full devices list based on timeframe selection
  let fullDevicesData = [];
  let totalTimeframeEnergy = 0;
  let totalTimeframeCost = 0;
  
  if (pieTab === 'today' && summaryData.today_device_breakdown) {
    totalTimeframeEnergy = summaryData.today_device_breakdown.reduce((sum, d) => sum + d.energy_kwh, 0);
    totalTimeframeCost = summaryData.today_device_breakdown.reduce((sum, d) => sum + d.cost, 0);
    
    fullDevicesData = summaryData.today_device_breakdown.map(d => ({
      name: d.device_name,
      type: d.device_type,
      energy: d.energy_kwh,
      cost: d.cost,
      percentage: totalTimeframeEnergy > 0 ? parseFloat(((d.energy_kwh / totalTimeframeEnergy) * 100).toFixed(1)) : 0
    }));
  } else if (pieTab === 'yesterday' && summaryData.yesterday_device_breakdown) {
    totalTimeframeEnergy = summaryData.yesterday_device_breakdown.reduce((sum, d) => sum + d.energy_kwh, 0);
    totalTimeframeCost = summaryData.yesterday_device_breakdown.reduce((sum, d) => sum + d.cost, 0);
    
    fullDevicesData = summaryData.yesterday_device_breakdown.map(d => ({
      name: d.device_name,
      type: d.device_type,
      energy: d.energy_kwh,
      cost: d.cost,
      percentage: totalTimeframeEnergy > 0 ? parseFloat(((d.energy_kwh / totalTimeframeEnergy) * 100).toFixed(1)) : 0
    }));
  } else {
    const devPreds = predictionData.device_predictions || [];
    totalTimeframeEnergy = devPreds.reduce((sum, d) => sum + d.monthly.energy_kwh, 0);
    totalTimeframeCost = devPreds.reduce((sum, d) => sum + (d.monthly.cost || 0), 0);
    
    fullDevicesData = devPreds.map(d => ({
      name: d.device_name,
      type: d.device_type,
      energy: d.monthly.energy_kwh,
      cost: d.monthly.cost || 0,
      percentage: totalTimeframeEnergy > 0 ? parseFloat(((d.monthly.energy_kwh / totalTimeframeEnergy) * 100).toFixed(1)) : 0
    }));
  }
  
  // Sort full devices from highest to lowest consumption
  fullDevicesData = fullDevicesData.sort((a, b) => b.energy - a.energy);

  // Format device breakdown pie data based on fullDevicesData
  let pieData = [];
  if (fullDevicesData.length > 0) {
    const top5 = fullDevicesData.slice(0, 5).map(d => ({
      name: d.name,
      value: d.percentage
    }));
    const topSum = top5.reduce((sum, d) => sum + d.value, 0);
    if (topSum < 99.9 && fullDevicesData.length > 5) {
      top5.push({
        name: 'Others',
        value: parseFloat((100.0 - topSum).toFixed(1))
      });
    }
    pieData = top5;
  }

  // Weekly data (Today + last 6 days simulated around the average)
  const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const avgDailyUsage = summaryData.weekly.energy_kwh / 7.0;
  const weeklyChartData = daysOfWeek.map((day, idx) => ({
    day,
    usage: round(avgDailyUsage * np_rand(0.85, 1.15), 1)
  }));

  // Monthly data (Simulated past 6 months to match the UI template)
  const monthlyChartData = [
    { month: 'Jan', usage: round(summaryData.monthly.energy_kwh * 0.9, 0), bill: round(summaryData.monthly.cost * 0.9, 0) },
    { month: 'Feb', usage: round(summaryData.monthly.energy_kwh * 0.8, 0), bill: round(summaryData.monthly.cost * 0.8, 0) },
    { month: 'Mar', usage: round(summaryData.monthly.energy_kwh * 0.85, 0), bill: round(summaryData.monthly.cost * 0.85, 0) },
    { month: 'Apr', usage: round(summaryData.monthly.energy_kwh * 1.1, 0), bill: round(summaryData.monthly.cost * 1.1, 0) },
    { month: 'May', usage: round(summaryData.monthly.energy_kwh * 1.2, 0), bill: round(summaryData.monthly.cost * 1.2, 0) },
    { month: 'Jun', usage: round(summaryData.monthly.energy_kwh, 0), bill: round(summaryData.monthly.cost, 0) },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>⚡ {t.energyUsage}</h1>
          <p>Detailed analysis of your home energy consumption</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <button 
            className="btn-add" 
            onClick={handleRetrain} 
            disabled={training}
            style={{ 
              background: training ? 'var(--text-muted)' : 'var(--teal)', 
              fontSize: 12, padding: '8px 16px', fontWeight: 600, cursor: training ? 'not-allowed' : 'pointer'
            }}
          >
            {training ? '⏳ Training model...' : '🤖 Retrain AI Model'}
          </button>
          {trainingMessage && (
            <div style={{ fontSize: 11, color: 'var(--teal)', marginTop: 4, fontWeight: 500 }}>
              {trainingMessage}
            </div>
          )}
        </div>
      </div>

      {/* Tab Controls */}
      <div className="energy-controls">
        {['hourly', 'weekly', 'monthly'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Main Chart */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header">
          <div className="card-title">
            {activeTab === 'hourly' && '24-Hour Usage Pattern (kWh)'}
            {activeTab === 'weekly' && 'Weekly Usage Trend (kWh)'}
            {activeTab === 'monthly' && 'Monthly Consumption History'}
          </div>
        </div>

        {activeTab === 'hourly' && (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} unit=" kWh" />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
              <Line type="monotone" dataKey="today" stroke="#14b8a6" strokeWidth={2.5} dot={false} name="Today" />
              <Line type="monotone" dataKey="yesterday" stroke="#475569" strokeWidth={1.5} dot={false} strokeDasharray="4 4" name="Yesterday" />
              <Legend wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }} />
            </LineChart>
          </ResponsiveContainer>
        )}

        {activeTab === 'weekly' && (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={weeklyChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} unit=" kWh" />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="usage" fill="url(#barGradient)" radius={[4, 4, 0, 0]} name="Usage (kWh)" />
              <defs>
                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#14b8a6" />
                  <stop offset="100%" stopColor="#0d9488" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        )}

        {activeTab === 'monthly' && (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={monthlyChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="usage" fill="#14b8a6" radius={[4, 4, 0, 0]} name="Usage (kWh)" />
              <Bar dataKey="bill" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Bill (₹)" />
              <Legend wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Bottom Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.35fr 0.65fr', gap: 16 }}>
        {/* Device Breakdown Pie & List */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div className="card-title">Device Breakdown</div>
            <div className="sub-tabs" style={{ display: 'flex', gap: 6, background: 'var(--bg-secondary)', padding: 3, borderRadius: 6 }}>
              {['today', 'yesterday', 'monthly'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setPieTab(tab)}
                  style={{
                    background: pieTab === tab ? 'var(--teal)' : 'transparent',
                    color: pieTab === tab ? '#fff' : 'var(--text-secondary)',
                    border: 'none', borderRadius: 4, padding: '4px 8px', fontSize: 11, cursor: 'pointer',
                    fontWeight: 600, transition: 'all 0.15s'
                  }}
                >
                  {tab.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.8fr', gap: 24, alignItems: 'center', flex: 1 }}>
            {/* Left: Pie Chart */}
            <div style={{ width: '100%', height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie 
                    data={pieData} 
                    cx="50%" 
                    cy="50%" 
                    outerRadius={65} 
                    dataKey="value" 
                    label={({ name, value }) => `${name} ${value}%`} 
                    labelLine={false} 
                    fontSize={9}
                  >
                    {pieData.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            
            {/* Right: Detailed List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 220, overflowY: 'auto', paddingRight: 8 }}>
              {fullDevicesData.map((d, index) => (
                <div key={index} style={{ display: 'flex', flexDirection: 'column', gap: 4, paddingBottom: 8, borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ 
                        width: 8, 
                        height: 8, 
                        borderRadius: '50%', 
                        backgroundColor: COLORS[index % COLORS.length] 
                      }} />
                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)' }}>{d.name}</span>
                        <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>
                          {d.type.charAt(0).toUpperCase() + d.type.slice(1).replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--teal)' }}>{d.energy.toFixed(1)} kWh</span>
                      <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>₹{d.cost.toFixed(1)}</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 2 }}>
                      <div style={{ 
                        height: '100%', 
                        width: `${d.percentage}%`, 
                        background: COLORS[index % COLORS.length], 
                        borderRadius: 2 
                      }} />
                    </div>
                    <span style={{ fontSize: 10, color: 'var(--text-muted)', minWidth: 26, textAlign: 'right' }}>
                      {d.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Peak Hours */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Peak Usage Hours</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[
              { time: '2 PM – 6 PM', label: 'Peak Load Time', usage: `${(summaryData.today.energy_kwh * 0.35).toFixed(1)} kWh`, color: 'var(--red)', pct: 90 },
              { time: '8 AM – 12 PM', label: 'High Load Time', usage: `${(summaryData.today.energy_kwh * 0.25).toFixed(1)} kWh`, color: 'var(--amber)', pct: 65 },
              { time: '6 AM – 8 AM', label: 'Moderate Load Time', usage: `${(summaryData.today.energy_kwh * 0.15).toFixed(1)} kWh`, color: 'var(--teal)', pct: 30 },
              { time: '12 AM – 4 AM', label: 'Low Idle Time', usage: `${(summaryData.today.energy_kwh * 0.08).toFixed(1)} kWh`, color: 'var(--text-muted)', pct: 15 },
            ].map(p => (
              <div key={p.time}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontSize: 12, fontWeight: 500 }}>{p.time}</span>
                  <span style={{ fontSize: 12, color: p.color, fontWeight: 600 }}>{p.usage}</span>
                </div>
                <div style={{ height: 6, background: 'var(--bg-secondary)', borderRadius: 3 }}>
                  <div style={{ height: '100%', width: `${p.pct}%`, background: p.color, borderRadius: 3, transition: 'width 0.5s ease' }} />
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{p.label}</div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 16, padding: '12px', background: 'var(--teal-glow)', borderRadius: 8, border: '1px solid var(--border-active)' }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--teal)', marginBottom: 4 }}>💡 Optimization Tip</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
              Shifting high energy appliances like Washers or Induction Cooktops off-peak (such as early mornings or late nights) can significantly improve your target bill tracking.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helpers
function round(value, precision) {
  var multiplier = Math.pow(10, precision || 0);
  return Math.round(value * multiplier) / multiplier;
}

function np_rand(min, max) {
  return Math.random() * (max - min) + min;
}
