import React, { useState, useEffect } from 'react';
import { LineChart, Clock, ShieldAlert, TrendingUp, AlertTriangle } from 'lucide-react';
import { api } from '../api/client';

export const InsightsView: React.FC = () => {
  const [aging, setAging] = useState<any>(null);
  const [cashflow, setCashflow] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setLoading(true);
      const [ag, cf] = await Promise.all([
        api.getAging(),
        api.getCashflow(14) // Next 14 days
      ]);
      setAging(ag);
      setCashflow(cf);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !aging) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', color: 'var(--text-muted)' }}>
        Computing Predictive Analytics & Cash Flow Forecaster...
      </div>
    );
  }

  const buckets = [
    { key: 'current_0_30', label: '0 - 30 Days (Current)', data: aging.current_0_30, badge: 'badge-emerald', color: '#10B981' },
    { key: 'overdue_31_60', label: '31 - 60 Days (Overdue)', data: aging.overdue_31_60, badge: 'badge-amber', color: '#F59E0B' },
    { key: 'overdue_61_90', label: '61 - 90 Days (Delayed)', data: aging.overdue_61_90, badge: 'badge-rose', color: '#EF4444' },
    { key: 'critical_90_plus', label: '90+ Days (Critical Default Risk)', data: aging.critical_90_plus, badge: 'badge-rose', color: '#DC2626' }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h3 style={{ fontSize: '1.25rem', color: '#F8FAFC' }}>Predictive Khata Analytics & Risk Intelligence</h3>
        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Deterministic aging classification, debtor turnaround velocity, and 14-day cash flow projection.
        </p>
      </div>

      {/* Aging Matrix Buckets */}
      <div>
        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '12px' }}>
          Receivables Aging Matrix
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
          {buckets.map(({ key, label, data, badge, color }) => (
            <div key={key} className="fin-card" style={{ borderLeft: `4px solid ${color}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className={`badge ${badge}`}>{data?.count || 0} Accounts</span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{label}</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color, marginTop: '4px' }}>
                ₹{Number(data?.amount || 0).toLocaleString()}
              </div>

              {data?.customers?.length > 0 && (
                <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid var(--border-color)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {data.customers.slice(0, 2).map((c: any, i: number) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2px' }}>
                      <span>{c.name}</span>
                      <strong>₹{Number(c.balance).toLocaleString()}</strong>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 14-Day AI Cash Flow Forecaster */}
      <div className="fin-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h4 style={{ fontSize: '1.05rem', color: '#38BDF8' }}>14-Day Projected Cash Flow</h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Calculated from active payment promises and scheduled supplier payables</p>
          </div>
          <span className="badge badge-cyan">Deterministic Projection</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px' }}>
          {cashflow.slice(0, 10).map((day, idx) => (
            <div
              key={idx}
              style={{
                background: 'var(--bg-card-subtle)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '10px 8px',
                textAlign: 'center'
              }}
            >
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{day.date.slice(5)} ({day.day_name})</div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#34D399', marginTop: '4px' }}>
                +₹{day.projected_inflow}
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#F87171', marginTop: '2px' }}>
                -₹{day.projected_outflow}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
