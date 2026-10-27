import React, { useState } from 'react';
import { RefreshCw, Volume2, Database } from 'lucide-react';
import { api } from '../api/client';
import { useLanguage } from '../context/LanguageContext';

export const SettingsView: React.FC = () => {
  const { t } = useLanguage();
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
        <h3 style={{ fontSize: '1.25rem', color: 'var(--text-main)' }}>{t('set.title', 'Platform Settings & Diagnostics')}</h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          {t('set.desc', 'Configure NLP confidence thresholds, speech recognition language fallback, and ledger audit parameters.')}
        </p>
      </div>

      {/* NLP & Audio Config */}
      <div className="fin-card">
        <h4 style={{ fontSize: '1rem', color: 'var(--cyan)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Volume2 size={18} /> {t('set.voice_section', 'Voice & NLP Pipeline Settings')}
        </h4>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>{t('set.threshold_lbl', 'Entity Extraction Confidence Threshold')}</label>
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
              {t('set.threshold_sub', 'Transactions with confidence below this threshold will prompt for confirmation before updating the ledger.')}
            </p>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>{t('set.high_val_lbl', 'High-Value Transaction Audit Alert (₹)')}</label>
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
          <Database size={18} /> {t('set.data_section', 'Store Khata Ledger Data & Memory')}
        </h4>

        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          {t('set.data_desc', 'Manage your business book records. You can reset active dialogue context or start with a clean empty slate.')}
        </p>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
          <button onClick={handleResetSession} className="btn btn-secondary">
            <RefreshCw size={16} /> {t('set.btn_reset_session', 'Reset Multi-Turn Session State')}
          </button>

          <button
            onClick={async () => {
              if (window.confirm(t('set.confirm_clear', 'Are you sure you want to clear all transactions, customers, and suppliers to start fresh with a clean slate?'))) {
                try {
                  await api.resetAllLedger();
                  alert(t('set.cleared_alert', 'Ledger cleared! All data removed. You have an empty khata to start from scratch.'));
                } catch (e: any) {
                  alert("Failed to reset: " + e.message);
                }
              }
            }}
            className="btn btn-secondary"
            style={{ color: '#F87171', borderColor: 'rgba(239, 68, 68, 0.4)' }}
          >
            {t('set.btn_start_scratch', '🗑️ Start from Scratch (Clear All Data)')}
          </button>

          <button
            onClick={async () => {
              try {
                await api.seedDemoData();
                alert(t('set.seeded_alert', 'Demo business data seeded successfully.'));
              } catch (e: any) {
                alert("Failed to seed: " + e.message);
              }
            }}
            className="btn btn-secondary"
            style={{ color: '#38BDF8', borderColor: 'rgba(56, 189, 248, 0.4)' }}
          >
            {t('set.btn_load_demo', '📦 Load Sample Demo Data')}
          </button>
        </div>

        {resetSuccess && (
          <div style={{ marginTop: '10px', fontSize: '0.8rem', color: '#34D399' }}>
            {t('set.reset_success', '✓ Session state successfully reset!')}
          </div>
        )}
      </div>
    </div>
  );
};
