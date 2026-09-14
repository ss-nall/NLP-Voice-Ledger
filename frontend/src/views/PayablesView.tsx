import React, { useState, useEffect } from 'react';
import { TrendingDown, Search, Truck, ArrowUpRight, CheckCircle2, Filter, Sparkles, Phone, Eye, FileText } from 'lucide-react';
import { api } from '../api/client';
import { EntityStatementModal } from '../components/EntityStatementModal';
import { useLedgerUpdated } from '../utils/events';

export const PayablesView: React.FC = () => {
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [tabFilter, setTabFilter] = useState<'active' | 'all' | 'settled'>('active');
  const [loading, setLoading] = useState(true);

  // Entity Statement Modal State
  const [selectedSupplierForStatement, setSelectedSupplierForStatement] = useState<any>(null);
  const [isStatementModalOpen, setIsStatementModalOpen] = useState(false);

  useEffect(() => {
    loadSuppliers();
  }, []);

  useLedgerUpdated(() => {
    loadSuppliers();
  });

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

  const handleOpenStatement = (supplier: any) => {
    setSelectedSupplierForStatement(supplier);
    setIsStatementModalOpen(true);
  };

  const activeSuppliers = suppliers.filter((s) => (s.outstanding_balance || 0) > 0);
  const settledSuppliers = suppliers.filter((s) => (s.outstanding_balance || 0) <= 0);
  const totalPayables = activeSuppliers.reduce((sum, s) => sum + (s.outstanding_balance || 0), 0);

  const filtered = suppliers.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.aliases?.some((a: string) => a.toLowerCase().includes(searchTerm.toLowerCase()));
    
    if (!matchesSearch) return false;

    if (tabFilter === 'active') {
      return (s.outstanding_balance || 0) > 0;
    } else if (tabFilter === 'settled') {
      return (s.outstanding_balance || 0) <= 0;
    }
    return true; // 'all'
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Entity Statement & Ledger History Modal */}
      <EntityStatementModal
        isOpen={isStatementModalOpen}
        onClose={() => setIsStatementModalOpen(false)}
        entity={selectedSupplierForStatement}
        type="supplier"
        onTransactionUpdated={loadSuppliers}
      />

      {/* Header Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <span style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--udhar-red-bg)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: 'var(--udhar-red)' }}>
              <TrendingDown size={20} />
            </span>
            ఇవ్వాల్సిన బాకీలు (Accounts Payable)
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            సప్లయర్లు & డీలర్లకు వ్యాపారం చెల్లించాల్సిన నికర బాకీలు (Supplier Payables & Purchase Dues).
          </p>
        </div>
      </div>

      {/* Overview Banner */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        <div className="fin-card fin-card-red">
          <div style={{ fontSize: '0.75rem', color: 'var(--udhar-red-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            మొత్తం ఇవ్వాల్సిన బాకీలు (Total Pending Payables)
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--udhar-red)', marginTop: '4px' }}>
            ₹{totalPayables.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {activeSuppliers.length} బాకీ ఉన్న సప్లయర్లు • {settledSuppliers.length} పూర్తయిన సప్లయర్లు
          </div>
        </div>

        <div className="fin-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', borderLeft: '4px solid var(--udhar-red)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
            <Sparkles size={16} color="var(--udhar-red)" />
            స్మార్ట్ చెల్లింపుల నియమం (Automated Accounting Rule)
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.5 }}>
            సప్లయర్లకు చెల్లించిన నగదు <strong>చెల్లించినవి (Paid)</strong> లో నమోదవుతుంది. ఇక్కడ ఆ సప్లయర్ బాకీ నిల్వ మాత్రమే ఆటోమేటిక్ గా తగ్గుతుంది.
          </div>
        </div>
      </div>

      {/* Filter Tabs & Search Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', gap: '6px', background: 'var(--bg-card-subtle)', padding: '4px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <button
            onClick={() => setTabFilter('active')}
            className="btn"
            style={{
              padding: '6px 14px',
              fontSize: '0.8rem',
              borderRadius: 'var(--radius-sm)',
              fontWeight: tabFilter === 'active' ? 700 : 500,
              background: tabFilter === 'active' ? 'var(--udhar-red)' : 'transparent',
              color: tabFilter === 'active' ? '#FFFFFF' : 'var(--text-dim)',
              border: 'none',
              boxShadow: tabFilter === 'active' ? '0 2px 6px rgba(239, 68, 68, 0.3)' : 'none'
            }}
          >
            బాకీ ఉన్నవి ({activeSuppliers.length})
          </button>
          <button
            onClick={() => setTabFilter('all')}
            className="btn"
            style={{
              padding: '6px 14px',
              fontSize: '0.8rem',
              borderRadius: 'var(--radius-sm)',
              fontWeight: tabFilter === 'all' ? 700 : 500,
              background: tabFilter === 'all' ? 'var(--bg-card)' : 'transparent',
              color: tabFilter === 'all' ? 'var(--text-main)' : 'var(--text-dim)',
              border: tabFilter === 'all' ? '1px solid var(--border-color)' : 'none'
            }}
          >
            అందరు సప్లయర్లు ({suppliers.length})
          </button>
          <button
            onClick={() => setTabFilter('settled')}
            className="btn"
            style={{
              padding: '6px 14px',
              fontSize: '0.8rem',
              borderRadius: 'var(--radius-sm)',
              fontWeight: tabFilter === 'settled' ? 700 : 500,
              background: tabFilter === 'settled' ? 'var(--bg-card)' : 'transparent',
              color: tabFilter === 'settled' ? 'var(--text-main)' : 'var(--text-dim)',
              border: tabFilter === 'settled' ? '1px solid var(--border-color)' : 'none'
            }}
          >
            పూర్తయినవి ({settledSuppliers.length})
          </button>
        </div>

        <div style={{ position: 'relative', flex: '1', maxWidth: '320px', minWidth: '220px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="సప్లయర్ పేరు లేదా మారుపేరు..."
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '9px 14px 9px 36px',
              color: 'var(--text-main)',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          />
        </div>
      </div>

      {/* Supplier Payables Table */}
      <div className="fin-card" style={{ padding: '0px', overflow: 'hidden' }}>
        {filtered.length === 0 ? (
          <div style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>🤝</div>
            <strong style={{ color: 'var(--text-main)', fontSize: '1rem' }}>
              {tabFilter === 'active' ? 'సప్లయర్లకు ఎలాంటి పెండింగ్ బాకీలు లేవు!' : 'సప్లయర్లు ఏవీ కనుగొనబడలేదు.'}
            </strong>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              {tabFilter === 'active'
                ? 'అన్ని సప్లయర్ బిల్లులు చెల్లించబడ్డాయి లేదా చెల్లించిన నగదు విభాగంలో నమోదయ్యాయి.'
                : 'వాయిస్ లేదా చాట్ లో లావాదేవీని నమోదు చేయండి.'}
            </div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="khata-table">
              <thead>
                <tr>
                  <th>సప్లయర్ పేరు (Supplier Name)</th>
                  <th>మారుపేర్లు (Aliases)</th>
                  <th style={{ textAlign: 'right' }}>ఇవ్వాల్సిన బాకీ (Outstanding Payable)</th>
                  <th>చివరి చెల్లింపు (Last Payment)</th>
                  <th>గమనికలు (Notes)</th>
                  <th style={{ textAlign: 'center' }}>స్టేట్‌మెంట్ (Statement)</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((s) => {
                  const hasDue = (s.outstanding_balance || 0) > 0;
                  return (
                    <tr key={s.id}>
                      <td style={{ fontWeight: 700, color: 'var(--text-main)', cursor: 'pointer' }} onClick={() => handleOpenStatement(s)}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ color: 'var(--text-main)', textDecoration: 'underline', textDecorationColor: 'var(--border-strong)' }}>{s.name}</span>
                          <Eye size={14} color="var(--text-dim)" />
                        </div>
                        {s.name_telugu && s.name_telugu !== s.name && (
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', fontWeight: 400 }}>
                            {s.name_telugu}
                          </span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                          {s.aliases && s.aliases.length > 0 ? (
                            s.aliases.slice(0, 3).map((a: string, idx: number) => (
                              <span key={idx} className="badge badge-neutral" style={{ fontSize: '0.68rem' }}>{a}</span>
                            ))
                          ) : (
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>—</span>
                          )}
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        {hasDue ? (
                          <span style={{ fontWeight: 800, color: 'var(--udhar-red)', fontSize: '0.95rem' }}>
                            ₹{Number(s.outstanding_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </span>
                        ) : (
                          <span className="badge badge-emerald" style={{ fontSize: '0.72rem' }}>
                            ✓ ₹0.00 (చెల్లింపు పూర్తయింది)
                          </span>
                        )}
                      </td>
                      <td style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                        {s.last_payment_date || 'ఇంకా నమోదు కాలేదు'}
                      </td>
                      <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        {s.notes || '—'}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <button
                          onClick={() => handleOpenStatement(s)}
                          className="btn-outline"
                          style={{ padding: '5px 10px', fontSize: '0.74rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                          title="ఖాతా వివరాలు (View Statement)"
                        >
                          <FileText size={13} /> స్టేట్‌మెంట్
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
