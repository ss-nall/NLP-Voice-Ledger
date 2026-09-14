import React, { useState, useEffect } from 'react';
import { Truck, Search, Phone } from 'lucide-react';
import { api } from '../api/client';

export const SuppliersView: React.FC = () => {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      const data = await api.getSuppliers();
      setSuppliers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = suppliers.filter(
    (s) =>
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.aliases?.some((a: string) => a.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>Supplier Directory & Payables</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Wholesalers, mills, and stock partners with ongoing purchase credit lines.
          </p>
        </div>

        <div style={{ position: 'relative', minWidth: '260px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '13px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search suppliers..."
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
          <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🚚</div>
          <h4 style={{ fontSize: '1.1rem', color: 'var(--text-main)', marginBottom: '6px' }}>ఇంకా ఏ సప్లయర్లు నమోదు కాలేదు (No Suppliers Yet)</h4>
          <p style={{ fontSize: '0.85rem', maxWidth: '480px', margin: '0 auto', color: 'var(--text-muted)' }}>
            సప్లయర్ లేదా డీలర్ కి ఇవ్వాల్సిన లెక్కలు వాయిస్/చాట్ లో చెప్పగానే ఇక్కడ ఆటోమేటిక్ గా కనిపిస్తాయి.
            <br /><em>(Speak in Voice & Chat, e.g. 'Supplier ki 5000 ivvali next week', and accounts appear here!)</em>
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
          {filtered.map((s) => (
            <div key={s.id} className="fin-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <h4 style={{ fontSize: '1.05rem', color: 'var(--text-main)' }}>{s.name}</h4>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                    <Phone size={12} /> {s.phone || 'No phone recorded'}
                  </div>
                </div>

                <span className="badge badge-rose">PAYABLE OBLIGATION</span>
              </div>

              <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)', marginBottom: '12px' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Outstanding Payable (We Owe)</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#F87171', marginTop: '2px' }}>
                  ₹{Number(s.outstanding_balance).toLocaleString()}
                </div>
              </div>

              <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginBottom: '4px' }}>Voice / Postposition Aliases:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {s.aliases?.map((alias: string, idx: number) => (
                    <span key={idx} className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>{alias}</span>
                  ))}
                </div>
              </div>

              {s.notes && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: '8px' }}>
                  {s.notes}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
