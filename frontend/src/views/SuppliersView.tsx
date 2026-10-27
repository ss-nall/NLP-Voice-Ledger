import React, { useState, useEffect } from 'react';
import { Search, Phone } from 'lucide-react';
import { api } from '../api/client';
import { useLanguage } from '../context/LanguageContext';

export const SuppliersView: React.FC = () => {
  const { t } = useLanguage();
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
          <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)' }}>{t('supp.title', 'Supplier Directory & Payables')}</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {t('supp.desc', 'Tracks supplier profiles, wholesale credit terms, and payable balances.')}
          </p>
        </div>

        <div style={{ position: 'relative', minWidth: '260px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '13px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t('supp.search_placeholder', 'Search suppliers...')}
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
        <div className="empty-state-card">
          <div className="empty-state-icon">🚚</div>
          <h4 style={{ fontSize: '1.15rem', color: 'var(--text-main)', margin: 0, fontWeight: 700 }}>
            {t('supp.no_records_title', 'No Suppliers Yet')}
          </h4>
          <p style={{ fontSize: '0.88rem', maxWidth: '480px', margin: '0 auto', color: 'var(--text-muted)' }}>
            {t('supp.no_records_sub', 'Supplier accounts are dynamically created as soon as you record a payable transaction!')}
          </p>
          <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
            <span className="prompt-chip">🎙️ "Pawan ki 8000 ivvali"</span>
            <span className="prompt-chip">🎙️ "Supplier Chandu ki 5000 kattanu"</span>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
          {filtered.map((s) => (
            <div key={s.id} className="fin-card hover-lift">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <div>
                  <h4 style={{ fontSize: '1.05rem', color: 'var(--text-main)', fontWeight: 700 }}>{s.name}</h4>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                    <Phone size={12} /> {s.phone || 'No phone recorded'}
                  </div>
                </div>

                <span className="badge badge-rose">{t('term.payable', 'Payable')}</span>
              </div>

              <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-sm)', marginBottom: '12px' }}>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', fontWeight: 600 }}>{t('supp.payable_bal', 'Payable Balance')}</div>
                <div className="tabular-nums" style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--payable-color)', marginTop: '2px' }}>
                  ₹{Number(s.outstanding_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
              </div>

              <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginBottom: '4px' }}>{t('cust.voice_aliases', 'Recognized Voice Aliases:')}</div>
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
