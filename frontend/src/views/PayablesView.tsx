import React, { useState, useEffect } from 'react';
import { TrendingDown, Search, Sparkles, Eye } from 'lucide-react';
import { api } from '../api/client';
import { EntityStatementModal } from '../components/EntityStatementModal';
import { useLedgerUpdated } from '../utils/events';
import { useLanguage } from '../context/LanguageContext';

export const PayablesView: React.FC = () => {
  const { t } = useLanguage();
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
            <span style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--udhaar-red-bg)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: 'var(--udhaar-red)' }}>
              <TrendingDown size={20} />
            </span>
            {t('pay.title', 'Supplier Payables (To Pay)')}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {t('pay.desc', 'List of trade liabilities and pending supplier bills.')}
          </p>
        </div>
      </div>

      {/* Overview Banner */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        <div className="fin-card fin-card-red">
          <div style={{ fontSize: '0.75rem', color: 'var(--udhaar-red-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            {t('pay.total_pending', 'Total Pending Payables')}
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--udhaar-red)', marginTop: '4px' }}>
            ₹{totalPayables.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {activeSuppliers.length} {t('rec.active_accounts', 'active accounts')} • {settledSuppliers.length} {t('rec.settled_accounts', 'settled accounts')}
          </div>
        </div>

        <div className="fin-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', borderLeft: '4px solid var(--udhaar-red)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)' }}>
            <Sparkles size={16} color="var(--udhaar-red)" />
            {t('pay.accounting_rule_title', 'Payable Accounting Rule')}
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.5 }}>
            {t('pay.accounting_rule_desc', 'When you pay a supplier, it is recorded in Outflows and the supplier liability automatically decreases.')}
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
              background: tabFilter === 'active' ? 'var(--udhaar-red)' : 'transparent',
              color: tabFilter === 'active' ? '#FFFFFF' : 'var(--text-dim)',
              border: 'none',
              boxShadow: tabFilter === 'active' ? '0 2px 6px rgba(239, 68, 68, 0.3)' : 'none'
            }}
          >
            {t('pay.tab_active', 'Pending Payables')} ({activeSuppliers.length})
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
            {t('pay.tab_all', 'All Suppliers')} ({suppliers.length})
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
            {t('pay.tab_settled', 'Fully Settled')} ({settledSuppliers.length})
          </button>
        </div>

        <div style={{ position: 'relative', flex: '1', maxWidth: '320px', minWidth: '220px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t('pay.search_placeholder', 'Search supplier name or business...')}
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

      {/* Suppliers List Table */}
      <div className="fin-card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '36px', textAlign: 'center', color: 'var(--text-muted)' }}>
            {t('dash.loading', 'Loading financial overview and double-entry accounts...')}
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '36px', textAlign: 'center', color: 'var(--text-muted)' }}>
            {t('pay.no_suppliers', 'No supplier accounts found.')}
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'var(--bg-card-subtle)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  {t('pay.th_supplier', 'Supplier Name')}
                </th>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  {t('rec.th_phone', 'Phone Number')}
                </th>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  {t('pay.th_balance', 'Payable Amount')}
                </th>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase' }}>
                  {t('rec.th_status', 'Status')}
                </th>
                <th style={{ padding: '12px 16px', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', textAlign: 'right' }}>
                  {t('pay.th_actions', 'Actions')}
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((supp) => {
                const bal = supp.outstanding_balance || 0;
                const isDue = bal > 0;
                return (
                  <tr key={supp.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-main)' }}>
                        {supp.name}
                      </div>
                      {supp.aliases && supp.aliases.length > 0 && (
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                          {supp.aliases.join(', ')}
                        </div>
                      )}
                    </td>
                    <td style={{ padding: '14px 16px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {supp.phone || '—'}
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <span style={{ fontWeight: 800, fontSize: '1.05rem', color: isDue ? 'var(--udhaar-red)' : 'var(--text-muted)' }}>
                        ₹{bal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <span
                        className={`badge ${isDue ? 'badge-udhaar' : 'badge-neutral'}`}
                        style={{ fontSize: '0.72rem', padding: '3px 8px', fontWeight: 600 }}
                      >
                        {isDue ? t('term.payable', 'Pending Payable') : t('pay.tab_settled', 'Settled')}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <button
                        onClick={() => handleOpenStatement(supp)}
                        className="btn btn-outline"
                        style={{ padding: '6px 12px', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                      >
                        <Eye size={13} /> {t('term.view_details', 'Statement')}
                      </button>
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
