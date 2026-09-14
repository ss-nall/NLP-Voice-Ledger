import React, { useState, useEffect } from 'react';
import { ShieldCheck, AlertCircle, RefreshCw, Scale, CheckCircle2, FileCheck, Layers } from 'lucide-react';
import { api } from '../api/client';
import { useLedgerUpdated } from '../utils/events';

export const HealthView: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [journal, setJournal] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHealthData();
  }, []);

  useLedgerUpdated(() => {
    loadHealthData();
  });

  const loadHealthData = async () => {
    try {
      setLoading(true);
      const [h, j] = await Promise.all([
        api.getHealth(),
        api.getJournal(25)
      ]);
      setHealth(h);
      setJournal(j);
    } catch (err) {
      console.error('Failed to load health status', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Scale size={24} color="#059669" />
            ఖాతా ఆడిట్ & డబుల్ ఎంట్రీ సమతుల్యత (Double-Entry Trial Balance)
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            డెబిట్ మరియు క్రెడిట్ లెక్కలు 100% సరిపోయాయో లేదో నిర్ధారించే ప్రత్యక్ష తనిఖీ వ్యవస్థ
          </p>
        </div>
        <button onClick={loadHealthData} className="btn-outline">
          <RefreshCw size={16} /> రీ-ఆడిట్ చేయి (Re-verify)
        </button>
      </div>

      {/* Trial Balance Health Banner */}
      {health && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <div className="fin-card" style={{ background: health.is_healthy ? 'var(--receivable-light)' : 'var(--payable-light)', border: `1px solid ${health.is_healthy ? 'var(--receivable-color)' : 'var(--payable-color)'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              {health.is_healthy ? <CheckCircle2 size={24} color="#059669" /> : <AlertCircle size={24} color="#DC2626" />}
              <span style={{ fontWeight: 700, fontSize: '1.05rem', color: health.is_healthy ? 'var(--jama-green-dark)' : 'var(--payable-color)' }}>
                {health.is_healthy ? 'ఖాతా సమతుల్యంగా ఉంది (100% Balanced)' : 'వ్యత్యాసం గుర్తించబడింది (Discrepancy)'}
              </span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Total Debits == Total Credits. సున్నా గణిత లోపాలు.
            </p>
          </div>

          <div className="fin-card">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 600 }}>మొత్తం డెబిట్లు (Total Debits)</span>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#059669', marginTop: '4px' }}>
              ₹{health.total_debits?.toLocaleString()}
            </div>
          </div>

          <div className="fin-card">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 600 }}>మొత్తం క్రెడిట్లు (Total Credits)</span>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#059669', marginTop: '4px' }}>
              ₹{health.total_credits?.toLocaleString()}
            </div>
          </div>

          <div className="fin-card">
            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 600 }}>వ్యత్యాసం (Discrepancy)</span>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: health.discrepancy === 0 ? '#059669' : '#DC2626', marginTop: '4px' }}>
              ₹{health.discrepancy?.toFixed(2)}
            </div>
          </div>
        </div>
      )}

      {/* General Ledger Journal Table */}
      <div className="fin-card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={18} color="#059669" />
          జనరల్ లెడ్జర్ జర్నల్ ఎంట్రీలు (Double-Entry Journal Entries)
        </h3>
        
        {loading ? (
          <p style={{ color: 'var(--text-muted)', padding: '20px' }}>జర్నల్ ఎంట్రీలు లోడ్ అవుతున్నాయి...</p>
        ) : journal.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', padding: '20px' }}>ఇంకా ఎలాంటి లావాదేవీలు నమోదు కాలేదు.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="khata-table">
              <thead>
                <tr>
                  <th>తేదీ (Date)</th>
                  <th>వివరణ (Description)</th>
                  <th>ఖాతా (Account)</th>
                  <th>రకం (Type)</th>
                  <th style={{ textAlign: 'right' }}>డెబిట్ (Debit ₹)</th>
                  <th style={{ textAlign: 'right' }}>క్రెడిట్ (Credit ₹)</th>
                </tr>
              </thead>
              <tbody>
                {journal.map((entry) => (
                  <React.Fragment key={entry.id}>
                    {entry.lines.map((line: any, idx: number) => (
                      <tr key={line.id} style={{ background: idx === 0 ? 'var(--bg-card-subtle)' : 'var(--bg-card)' }}>
                        {idx === 0 ? (
                          <td rowSpan={entry.lines.length} style={{ fontWeight: 600, verticalAlign: 'top' }}>
                            {entry.entry_date}
                          </td>
                        ) : null}
                        {idx === 0 ? (
                          <td rowSpan={entry.lines.length} style={{ verticalAlign: 'top' }}>
                            <div style={{ fontWeight: 600 }}>{entry.description}</div>
                            {entry.reference && <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>"{entry.reference}"</div>}
                          </td>
                        ) : null}
                        <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                          {line.account_name} ({line.entity_name || 'General'})
                        </td>
                        <td>
                          <span className="badge badge-neutral" style={{ fontSize: '0.72rem' }}>{line.account_type}</span>
                        </td>
                        <td style={{ textAlign: 'right', fontWeight: 700, color: line.debit > 0 ? '#059669' : '#94A3B8' }}>
                          {line.debit > 0 ? `₹${line.debit.toLocaleString()}` : '-'}
                        </td>
                        <td style={{ textAlign: 'right', fontWeight: 700, color: line.credit > 0 ? '#DC2626' : '#94A3B8' }}>
                          {line.credit > 0 ? `₹${line.credit.toLocaleString()}` : '-'}
                        </td>
                      </tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
