import React, { useState, useEffect } from 'react';
import { Users, Search, Plus, Phone, ShieldCheck, CreditCard } from 'lucide-react';
import { api } from '../api/client';

export const CustomersView: React.FC = () => {
  const [customers, setCustomers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const data = await api.getCustomers();
      setCustomers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = customers.filter(
    (c) =>
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.aliases?.some((a: string) => a.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>Customer Directory & Sub-Ledgers</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Tracks customer profiles, phonetic aliases, credit scores, and risk classifications.
          </p>
        </div>

        <div style={{ position: 'relative', minWidth: '260px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '13px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search customers..."
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '10px 14px 10px 36px',
              color: 'var(--text-main)',
              fontSize: '0.88rem',
              outline: 'none'
            }}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="fin-card" style={{ textAlign: 'center', padding: '48px 20px', color: 'var(--text-dim)' }}>
          <div style={{ fontSize: '2rem', marginBottom: '10px' }}>👥</div>
          <h4 style={{ fontSize: '1.1rem', color: 'var(--text-main)', marginBottom: '6px' }}>ఇంకా ఏ కస్టమర్లు నమోదు కాలేదు (No Customers Yet)</h4>
          <p style={{ fontSize: '0.85rem', maxWidth: '480px', margin: '0 auto', color: 'var(--text-muted)' }}>
            మీరు వాయిస్ లేదా చాట్ లో లావాదేవీ చెప్పగానే కస్టమర్ వివరాలు ఆటోమేటిక్ గా ఇక్కడ కనిపిస్తాయి.
            <br /><em>(Speak or type in Voice & Chat, e.g. 'Customer nundi 3000 ravali', and accounts are created dynamically!)</em>
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
          {filtered.map((c) => (
            <div key={c.id} className="fin-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <h4 style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>{c.name}</h4>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                    <Phone size={12} /> {c.phone || 'No phone recorded'}
                  </div>
                </div>

                <span className={`badge ${c.risk_tier === 'LOW' ? 'badge-emerald' : c.risk_tier === 'MEDIUM' ? 'badge-amber' : 'badge-rose'}`}>
                  {c.risk_tier} RISK
                </span>
              </div>

              <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)', marginBottom: '12px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Outstanding Balance</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34D399' }}>₹{Number(c.outstanding_balance).toLocaleString()}</div>
                </div>

                <div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Credit Score (300-850)</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#38BDF8' }}>{c.credit_score}</div>
                </div>
              </div>

              <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginBottom: '4px' }}>Recognized Voice Aliases:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {c.aliases?.map((alias: string, idx: number) => (
                    <span key={idx} className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>{alias}</span>
                  ))}
                </div>
              </div>

              {c.notes && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: '8px' }}>
                  {c.notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
