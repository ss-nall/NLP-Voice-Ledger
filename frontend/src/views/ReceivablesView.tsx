import React, { useState, useEffect } from 'react';
import { TrendingUp, MessageSquare, Smartphone, Search, AlertCircle, CheckCircle2, Clock, Filter, Sparkles, ArrowDownLeft, Eye, FileText } from 'lucide-react';
import { api } from '../api/client';
import { ReminderModal } from '../components/ReminderModal';
import { EntityStatementModal } from '../components/EntityStatementModal';
import { useLedgerUpdated } from '../utils/events';

export const ReceivablesView: React.FC = () => {
  const [customers, setCustomers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [tabFilter, setTabFilter] = useState<'active' | 'all' | 'settled'>('active');
  const [loading, setLoading] = useState(true);

  // Reminder Modal State
  const [selectedReminder, setSelectedReminder] = useState<any>(null);
  const [isReminderModalOpen, setIsReminderModalOpen] = useState(false);

  // Entity Statement Modal State
  const [selectedEntityForStatement, setSelectedEntityForStatement] = useState<any>(null);
  const [isStatementModalOpen, setIsStatementModalOpen] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, []);

  useLedgerUpdated(() => {
    loadCustomers();
  });

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

  const handleOpenReminder = async (customer: any) => {
    try {
      const reminderData = await api.generateReminder(
        customer.name,
        customer.outstanding_balance,
        'Friday (Next Week)',
        customer.phone || '+919848012345'
      );
      setSelectedReminder(reminderData);
      setIsReminderModalOpen(true);
    } catch (err: any) {
      alert("Error generating reminder: " + err.message);
    }
  };

  const handleOpenStatement = (customer: any) => {
    setSelectedEntityForStatement(customer);
    setIsStatementModalOpen(true);
  };

  const activeCustomers = customers.filter((c) => (c.outstanding_balance || 0) > 0);
  const settledCustomers = customers.filter((c) => (c.outstanding_balance || 0) <= 0);
  const totalReceivables = activeCustomers.reduce((sum, c) => sum + (c.outstanding_balance || 0), 0);

  const filtered = customers.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.aliases?.some((a: string) => a.toLowerCase().includes(searchTerm.toLowerCase()));
    
    if (!matchesSearch) return false;

    if (tabFilter === 'active') {
      return (c.outstanding_balance || 0) > 0;
    } else if (tabFilter === 'settled') {
      return (c.outstanding_balance || 0) <= 0;
    }
    return true; // 'all'
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Reminder Modal */}
      <ReminderModal
        isOpen={isReminderModalOpen}
        onClose={() => setIsReminderModalOpen(false)}
        reminderData={selectedReminder}
      />

      {/* Entity Statement & Ledger History Modal */}
      <EntityStatementModal
        isOpen={isStatementModalOpen}
        onClose={() => setIsStatementModalOpen(false)}
        entity={selectedEntityForStatement}
        type="customer"
        onTransactionUpdated={loadCustomers}
      />

      {/* Header Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <span style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--jama-green-bg)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: 'var(--jama-green)' }}>
              <TrendingUp size={20} />
            </span>
            రావాల్సిన బాకీలు (Accounts Receivable)
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            కస్టమర్ల నుండి వ్యాపారానికి రావాల్సిన నికర బాకీల జాబితా (Pending Customer Dues & Credit Sales).
          </p>
        </div>
      </div>

      {/* Overview Banner */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        <div className="fin-card fin-card-green">
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            మొత్తం రావాల్సిన బాకీలు (Total Pending Dues)
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--jama-green)', marginTop: '4px' }}>
            ₹{totalReceivables.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {activeCustomers.length} బాకీ ఉన్న ఖాతాలు • {settledCustomers.length} పూర్తయిన ఖాతాలు
          </div>
        </div>

        <div className="fin-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', borderLeft: '4px solid var(--jama-green)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
            <Sparkles size={16} color="var(--jama-green)" />
            స్మార్ట్ వసూళ్ల నియమం (Automated Accounting Rule)
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.5 }}>
            కస్టమర్ డబ్బులు ఇచ్చినప్పుడు అవి <strong>వచ్చినవి (Received)</strong> లో నమోదవుతాయి. ఇక్కడ ఆ కస్టమర్ బాకీ నిల్వ మాత్రమే ఆటోమేటిక్ గా తగ్గుతుంది.
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
              background: tabFilter === 'active' ? 'var(--jama-green)' : 'transparent',
              color: tabFilter === 'active' ? '#FFFFFF' : 'var(--text-dim)',
              border: 'none',
              boxShadow: tabFilter === 'active' ? '0 2px 6px rgba(16, 185, 129, 0.3)' : 'none'
            }}
          >
            బాకీ ఉన్నవి ({activeCustomers.length})
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
            అన్ని ఖాతాలు ({customers.length})
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
            పూర్తయినవి ({settledCustomers.length})
          </button>
        </div>

        <div style={{ position: 'relative', flex: '1', maxWidth: '320px', minWidth: '220px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="కస్టమర్ పేరు లేదా మారుపేరు..."
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

      {/* Customer Receivables Table */}
      <div className="fin-card" style={{ padding: '0px', overflow: 'hidden' }}>
        {filtered.length === 0 ? (
          <div style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '8px' }}>🎉</div>
            <strong style={{ color: 'var(--text-main)', fontSize: '1rem' }}>
              {tabFilter === 'active' ? 'ప్రస్తుతం ఎలాంటి పెండింగ్ బాకీలు లేవు!' : 'ఖాతాలు ఏవీ కనుగొనబడలేదు.'}
            </strong>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              {tabFilter === 'active' 
                ? 'అన్ని కస్టమర్ చెల్లింపులు పూర్తయ్యాయి లేదా వచ్చిన నగదు కింద నమోదయ్యాయి.' 
                : 'వాయిస్ లేదా చాట్ లో లావాదేవీని నమోదు చేయండి.'}
            </div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="khata-table">
              <thead>
                <tr>
                  <th>కస్టమర్ పేరు (Customer)</th>
                  <th>మారుపేర్లు (Aliases)</th>
                  <th style={{ textAlign: 'right' }}>రావాల్సిన బాకీ (Outstanding Balance)</th>
                  <th>క్రెడిట్ స్కోర్ (Score)</th>
                  <th>రిస్క్ స్థాయి (Risk)</th>
                  <th>చివరి చెల్లింపు (Last Payment)</th>
                  <th style={{ textAlign: 'center' }}>రిమైండర్ (Reminder)</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => {
                  const hasDue = (c.outstanding_balance || 0) > 0;
                  return (
                    <tr key={c.id}>
                      <td style={{ fontWeight: 700, color: 'var(--text-main)', cursor: 'pointer' }} onClick={() => handleOpenStatement(c)}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{ color: 'var(--text-main)', textDecoration: 'underline', textDecorationColor: 'var(--border-strong)' }}>{c.name}</span>
                          <Eye size={14} color="var(--text-dim)" />
                        </div>
                        {c.name_telugu && c.name_telugu !== c.name && (
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', fontWeight: 400 }}>
                            {c.name_telugu}
                          </span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                          {c.aliases && c.aliases.length > 0 ? (
                            c.aliases.slice(0, 3).map((a: string, idx: number) => (
                              <span key={idx} className="badge badge-neutral" style={{ fontSize: '0.68rem' }}>{a}</span>
                            ))
                          ) : (
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>—</span>
                          )}
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        {hasDue ? (
                          <span style={{ fontWeight: 800, color: 'var(--jama-green)', fontSize: '0.95rem' }}>
                            ₹{Number(c.outstanding_balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </span>
                        ) : (
                          <span className="badge badge-emerald" style={{ fontSize: '0.72rem' }}>
                            ✓ ₹0.00 (పూర్తయింది)
                          </span>
                        )}
                      </td>
                      <td>
                        <span className={`badge ${c.credit_score >= 750 ? 'badge-emerald' : c.credit_score >= 650 ? 'badge-amber' : 'badge-rose'}`} style={{ fontSize: '0.75rem' }}>
                          {c.credit_score || 700}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${c.risk_tier === 'LOW' ? 'badge-emerald' : c.risk_tier === 'MEDIUM' ? 'badge-amber' : 'badge-rose'}`} style={{ fontSize: '0.72rem' }}>
                          {c.risk_tier || 'LOW'}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                        {c.last_payment_date || 'ఇంకా నమోదు కాలేదు'}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                          <button
                            onClick={() => handleOpenStatement(c)}
                            className="btn-outline"
                            style={{ padding: '5px 10px', fontSize: '0.74rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            title="ఖాతా వివరాలు (View Statement)"
                          >
                            <FileText size={13} /> స్టేట్‌మెంట్
                          </button>
                          {hasDue && (
                            <button
                              onClick={() => handleOpenReminder(c)}
                              className="btn btn-emerald"
                              style={{ padding: '5px 10px', fontSize: '0.74rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            >
                              <Smartphone size={13} /> రిమైండర్
                            </button>
                          )}
                        </div>
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
