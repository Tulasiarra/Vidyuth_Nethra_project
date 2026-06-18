import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { reportApi, energyApi } from '../services/api';

export default function ReportsPage({ t, selectedHome }) {
  const [reports, setReports] = useState([]);
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchData = async () => {
    if (!selectedHome) return;
    setLoading(true);
    try {
      const [reportsList, summary] = await Promise.all([
        reportApi.getReports(selectedHome.id),
        energyApi.getEnergySummary(selectedHome.id)
      ]);
      setReports(reportsList);
      setSummaryData(summary);
    } catch (err) {
      console.error("Failed to load reports data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedHome]);

  const handleGenerate = async () => {
    if (!selectedHome || isGenerating) return;
    setIsGenerating(true);
    try {
      const monthStr = selectedMonth < 10 ? `0${selectedMonth}` : `${selectedMonth}`;
      const dateStr = `${selectedYear}-${monthStr}-15`;
      await reportApi.generateReport(selectedHome.id, 'monthly', dateStr);
      const updatedList = await reportApi.getReports(selectedHome.id);
      setReports(updatedList);
      alert("Monthly report generated successfully!");
    } catch (err) {
      console.error("Failed to generate report:", err);
      alert(err.message || "Error generating report");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = (reportId, format) => {
    const url = format === 'pdf' ? reportApi.getPDFUrl(reportId) : reportApi.getCSVUrl(reportId);
    window.open(url, '_blank');
  };

  if (loading || !summaryData) {
    return (
      <div style={{ display: 'flex', height: '50vh', alignItems: 'center', justifyContent: 'center', color: 'var(--teal)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 36, animation: 'spin 1.5s linear infinite', marginBottom: 12 }}>⏳</div>
          <div style={{ fontSize: 13, letterSpacing: '1px' }}>Loading reports and statistics...</div>
        </div>
      </div>
    );
  }

  // Weekly data (Today + last 6 days simulated around the weekly average)
  const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const avgDailyUsage = summaryData.weekly.energy_kwh / 7.0;
  const weeklyChartData = daysOfWeek.map((day, idx) => ({
    day,
    usage: parseFloat((avgDailyUsage * (0.8 + (idx * 0.07) % 0.4)).toFixed(1))
  }));

  // Monthly data (Simulated past 6 months to match the UI template)
  const monthlyChartData = [
    { month: 'Jan', usage: Math.round(summaryData.monthly.energy_kwh * 0.9), bill: Math.round(summaryData.monthly.cost * 0.9) },
    { month: 'Feb', usage: Math.round(summaryData.monthly.energy_kwh * 0.8), bill: Math.round(summaryData.monthly.cost * 0.8) },
    { month: 'Mar', usage: Math.round(summaryData.monthly.energy_kwh * 0.85), bill: Math.round(summaryData.monthly.cost * 0.85) },
    { month: 'Apr', usage: Math.round(summaryData.monthly.energy_kwh * 1.1), bill: Math.round(summaryData.monthly.cost * 1.1) },
    { month: 'May', usage: Math.round(summaryData.monthly.energy_kwh * 1.2), bill: Math.round(summaryData.monthly.cost * 1.2) },
    { month: 'Jun', usage: Math.round(summaryData.monthly.energy_kwh), bill: Math.round(summaryData.monthly.cost) },
  ];

  // Savings calculation
  const budget = summaryData.target_bill || 2000;
  const monthlyCost = summaryData.monthly.cost || 0;
  const calculatedSavings = Math.max(0, budget - monthlyCost);

  return (
    <div>
      <div className="page-header">
        <h1>📊 Reports</h1>
        <p>Energy reports and analytics summaries</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Weekly Usage (kWh)</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={weeklyChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="usage" fill="#14b8a6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>Month Summary</div>
          {[
            { label: 'Total Usage', value: `${summaryData.monthly.energy_kwh} kWh`, icon: '⚡', color: 'var(--teal)' },
            { label: 'Total Cost', value: `₹${summaryData.monthly.cost}`, icon: '💰', color: 'var(--amber)' },
            { label: 'Savings vs Budget', value: `₹${calculatedSavings.toFixed(0)}`, icon: '🎉', color: 'var(--green)' },
            { label: 'Avg Daily Usage', value: `${(summaryData.monthly.energy_kwh / 30).toFixed(1)} kWh`, icon: '📅', color: 'var(--blue)' },
            { label: 'Top Consumer', value: summaryData.top_consuming_device.name, icon: '🔺', color: 'var(--red)' },
            { label: 'Target Budget', value: `₹${budget}`, icon: '🌿', color: 'var(--green)' },
          ].map(s => (
            <div key={s.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{s.icon} {s.label}</span>
              <span style={{ fontSize: 13, fontWeight: 600, color: s.color }}>{s.value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-title" style={{ marginBottom: 16 }}>Monthly Usage & Bill Trend</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={monthlyChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
            <Bar dataKey="usage" fill="#14b8a6" radius={[4, 4, 0, 0]} name="Usage (kWh)" />
            <Bar dataKey="bill" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Bill (₹)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div className="card-title">📁 Available Reports</div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <select
              value={selectedMonth}
              onChange={e => setSelectedMonth(parseInt(e.target.value))}
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                color: 'var(--text-primary)',
                fontSize: 12,
                padding: '6px 10px',
                cursor: 'pointer'
              }}
            >
              {['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'].map((m, idx) => (
                <option key={m} value={idx + 1}>{m}</option>
              ))}
            </select>
            <select
              value={selectedYear}
              onChange={e => setSelectedYear(parseInt(e.target.value))}
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                color: 'var(--text-primary)',
                fontSize: 12,
                padding: '6px 10px',
                cursor: 'pointer'
              }}
            >
              {[2024, 2025, 2026].map(y => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              style={{
                padding: '8px 16px',
                background: 'var(--teal-glow)',
                border: '1px solid var(--border-active)',
                borderRadius: 6,
                fontSize: 12,
                color: 'var(--teal)',
                cursor: 'pointer',
                opacity: isGenerating ? 0.6 : 1
              }}
            >
              {isGenerating ? 'Generating...' : '+ Generate New'}
            </button>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {reports.length === 0 ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
              No reports generated yet. Choose a type above and click Generate!
            </div>
          ) : (
            reports.map((r) => (
              <div key={r.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 14px', background: 'var(--bg-secondary)',
                borderRadius: 8, border: '1px solid var(--border)'
              }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 500, marginBottom: 2, textTransform: 'capitalize' }}>
                    {r.type} Summary Report ({r.start_date} to {r.end_date})
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    Generated on {new Date(r.created_at).toLocaleDateString()} at {new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => handleDownload(r.id, 'pdf')}
                    style={{
                      padding: '6px 14px',
                      background: 'transparent',
                      border: '1px solid var(--border)',
                      borderRadius: 6,
                      fontSize: 12,
                      color: 'var(--text-secondary)',
                      cursor: 'pointer'
                    }}
                  >
                    ⬇ PDF
                  </button>
                  <button
                    onClick={() => handleDownload(r.id, 'csv')}
                    style={{
                      padding: '6px 14px',
                      background: 'transparent',
                      border: '1px solid var(--border)',
                      borderRadius: 6,
                      fontSize: 12,
                      color: 'var(--text-secondary)',
                      cursor: 'pointer'
                    }}
                  >
                    ⬇ CSV
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
