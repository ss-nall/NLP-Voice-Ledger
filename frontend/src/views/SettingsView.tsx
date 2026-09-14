import React, { useState } from 'react';
import { Settings as SettingsIcon, RefreshCw, Volume2, ShieldCheck, Database } from 'lucide-react';
import { api } from '../api/client';

export const SettingsView: React.FC = () => {
  const [resetSuccess, setResetSuccess] = useState(false);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.70);
  const [highValueAlert, setHighValueAlert] = useState(25000);

  const handleResetSession = async () => {
    try {
      await api.resetSession();
      setResetSuccess(true);
      setTimeout(() => setResetSuccess(false), 3000);
    } catch (err: any) {
      alert("Error resetting session: " + err.message);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '800px' }}>
      <div>
        <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>Platform Settings & Diagnostics</h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Configure NLP confidence thresholds, speech recognition language fallback, and ledger audit parameters.
        </p>
      </div>

      {/* NLP & Audio Config */}
      <div className="fin-card">
        <h4 style={{ fontSize: '1rem', color: 'var(--cyan)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Volume2 size={18} /> Voice & NLP Pipeline Settings
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>Entity Extraction Confidence Threshold</label>
              <strong style={{ color: 'var(--cyan)' }}>{Math.round(confidenceThreshold * 100)}%</strong>
            </div>
            <input
              type="range"
              min="0.5"
              max="0.95"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--cyan)' }}
            />
            <p style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '4px' }}>
              Transactions with confidence below this threshold will prompt for confirmation before updating the ledger.
            </p>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>High-Value Transaction Audit Alert (₹)</label>
              <strong style={{ color: 'var(--amber)' }}>₹{highValueAlert.toLocaleString()}</strong>
            </div>
            <input
              type="number"
              value={highValueAlert}
              onChange={(e) => setHighValueAlert(parseInt(e.target.value) || 0)}
              style={{
                width: '100%',
                background: 'var(--bg-card-subtle)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: '8px 12px',
                color: 'var(--text-main)'
              }}
            />
          </div>
        </div>
      </div>

      {/* Session & Database Management */}
      <div className="fin-card">
        <h4 style={{ fontSize: '1rem', color: '#818CF8', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={18} /> Store Khata Ledger Data & Memory
        </h4>

        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Manage your business book records. You can reset active dialogue context or completely start from scratch for a new real business.
        </p>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
          <button onClick={handleResetSession} className="btn btn-secondary">
            <RefreshCw size={16} /> Reset Multi-Turn Session State
          </button>

          <button
            onClick={async () => {
              if (window.confirm("Are you sure you want to clear all transactions, customers, and suppliers to start fresh with a clean slate?")) {
                try {
                  await api.resetAllLedger();
                  alert("Ledger cleared! All dummy data removed. You have an empty khata to start from scratch.");
                } catch (e: any) {
                  alert("Failed to reset: " + e.message);
                }
              }
            }}
            className="btn btn-secondary"
            style={{ color: '#F87171', borderColor: 'rgba(239, 68, 68, 0.4)' }}
          >
            🗑️ Start from Scratch (Clear All Data)
          </button>

          <button
            onClick={async () => {
              try {
                await api.seedDemoData();
                alert("Demo business data seeded successfully.");
              } catch (e: any) {
                alert("Failed to seed: " + e.message);
              }
            }}
            className="btn btn-secondary"
            style={{ color: '#38BDF8', borderColor: 'rgba(56, 189, 248, 0.4)' }}
          >
            📦 Load Sample Demo Data
          </button>
        </div>

        {resetSuccess && (
          <div style={{ marginTop: '10px', fontSize: '0.8rem', color: '#34D399' }}>
            ✓ Session state successfully reset!
          </div>
        )}
      </div>
    </div>
  );
};
