import React, { useState, useEffect } from 'react';
import { TrendingUp, Search, Sparkles, Eye } from 'lucide-react';
import { api } from '../api/client';
import { ReminderModal } from '../components/ReminderModal';
import { EntityStatementModal } from '../components/EntityStatementModal';
import { useLedgerUpdated } from '../utils/events';
import { useLanguage } from '../context/LanguageContext';

export const ReceivablesView: React.FC = () => {
  const { t } = useLanguage();
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
            {t('rec.title', 'Customer Receivables (To Receive)')}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {t('rec.desc', 'List of pending customer credit balances & receivables.')}
          </p>
        </div>
      </div>

      {/* Overview Banner */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        <div className="fin-card fin-card-green">
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            {t('rec.total_pending', 'Total Pending Receivables')}
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--jama-green)', marginTop: '4px' }}>
            ₹{totalReceivables.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {activeCustomers.length} {t('rec.active_accounts', 'active accounts')} • {settledCustomers.length} {t('rec.settled_accounts', 'settled accounts')}
          </div>
        </div>

        <div className="fin-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', borderLeft: '4px solid var(--jama-green)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
            <Sparkles size={16} color="var(--jama-green)" />
            {t('rec.accounting_rule_title', 'Automated Accounting Rule')}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.5 }}>
            {t('rec.accounting_rule_desc', 'When customer payments are received, they are recorded in Inflows and the customer balance automatically decreases.')}
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
            {t('rec.tab_active', 'Active Dues')} ({activeCustomers.length})
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
            {t('rec.tab_all', 'All Accounts')} ({customers.length})
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
            {t('rec.tab_settled', 'Settled')} ({settledCustomers.length})
          </button>
        </div>

        <div style={{ position: 'relative', flex: '1', maxWidth: '320px', minWidth: '220px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t('rec.search_placeholder', 'Search customer name or alias...')}
            style={{
              width: '100%',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '8px 12px 8px 36px',
              color: 'var(--text-main)',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          />
        </div>
      </div>

      {/* Customers List Table */}
      <div className="fin-card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '36px', textAlign: 'center', color: 'var(--text-muted)' }}>
            {t('dash.loading', 'Loading financial overview and double-entry accounts...')}
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '36px', textAlign: 'center', color: 'var(--text-muted)' }}>
            {t('rec.no_customers', 'No customer accounts found matching your search.')}
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'var(--bg-card-subtle)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  {t('rec.th_customer', 'Customer Name')}
                </th>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  {t('rec.th_phone', 'Phone Number')}
                </th>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  {t('rec.th_balance', 'Pending Balance')}
                </th>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  {t('rec.th_status', 'Status')}
                </th>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', textAlign: 'right' }}>
                  {t('rec.th_actions', 'Actions')}
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((cust) => {
                const bal = cust.outstanding_balance || 0;
                const isDue = bal > 0;
                return (
                  <tr key={cust.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-main)' }}>
                        {cust.name}
                      </div>
                      {cust.aliases && cust.aliases.length > 0 && (
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                          {cust.aliases.join(', ')}
                        </div>
                      )}
                    </td>
                    <td style={{ padding: '14px 16px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {cust.phone || '—'}
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{ fontWeight: 800, fontSize: '1.05rem', color: isDue ? 'var(--jama-green)' : 'var(--text-muted)' }}>
                        ₹{bal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <span
                        className={`badge ${isDue ? 'badge-jama' : 'badge-neutral'}`}
                        style={{ fontSize: '0.72rem', padding: '3px 8px', fontWeight: 600 }}
                      >
                        {isDue ? t('term.receivable', 'Pending Due') : t('rec.tab_settled', 'Settled')}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '8px' }}>
                        {isDue && (
                          <button
                            onClick={() => handleOpenReminder(cust)}
                            className="btn btn-secondary"
                            style={{ padding: '6px 12px', fontSize: '0.75rem', fontWeight: 600 }}
                          >
                            💬 {t('term.send_reminder', 'Send Reminder')}
                          </button>
                        )}
                        <button
                          onClick={() => handleOpenStatement(cust)}
                          className="btn btn-outline"
                          style={{ padding: '6px 12px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                        >
                          <Eye size={13} /> {t('term.view_details', 'Statement')}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

    </div>
  );
};
