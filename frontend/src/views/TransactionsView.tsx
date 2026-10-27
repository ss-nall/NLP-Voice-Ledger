import React, { useState, useEffect } from 'react';
import {
  Search,
  ShieldCheck,
  ArrowDownLeft,
  ArrowUpRight,
  Edit2,
  Trash2
} from 'lucide-react';
import { api } from '../api/client';
import { ExplainabilityCard } from '../components/ExplainabilityCard';
import { EditTransactionModal } from '../components/EditTransactionModal';
import { useLedgerUpdated } from '../utils/events';
import { useLanguage } from '../context/LanguageContext';

export const TransactionsView: React.FC = () => {
  const { t } = useLanguage();
  const [transactions, setTransactions] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDirection, setSelectedDirection] = useState<string>('');
  const [selectedTransaction, setSelectedTransaction] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Edit/Delete Modal State
  const [editingTx, setEditingTx] = useState<any>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    loadTransactions();
  }, [selectedDirection]);

  useLedgerUpdated(() => {
    loadTransactions();
  });

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (selectedDirection) params.direction = selectedDirection;
      const txs = await api.getTransactions(params);
      setTransactions(txs);
      if (txs.length > 0 && !selectedTransaction) {
        setSelectedTransaction(txs[0]);
      }
    } catch (err) {
      console.error('Failed to load transactions', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDirect = async (txId: string) => {
    if (window.confirm(t('tx.confirm_delete', 'Are you sure you want to delete this transaction? Ledger balances will be automatically adjusted.'))) {
      try {
        await api.deleteTransaction(txId);
        loadTransactions();
      } catch (err: any) {
        alert("Error deleting transaction: " + err.message);
      }
    }
  };

  const filtered = transactions.filter((t) =>
    t.counterparty_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.source_text?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalReceivables = transactions
    .filter((t) => t.direction === 'receivable')
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  const totalPayables = transactions
    .filter((t) => t.direction === 'payable')
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Selected Transaction Explainability Card */}
      {selectedTransaction && (
        <ExplainabilityCard
          transaction={selectedTransaction}
          onClose={() => setSelectedTransaction(null)}
        />
      )}

      {/* Top Overview KPI Ribbon */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        <div className="fin-card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            {t('tx.total_tx', 'All Transactions')}
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '4px' }}>
            {transactions.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {t('tx.total_tx_sub', 'All entries recorded in the double-entry ledger')}
          </div>
        </div>

        <div className="fin-card fin-card-green">
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            {t('tx.total_inflow', 'Total Inflow (Receivables)')}
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--jama-green)', marginTop: '4px' }}>
            +₹{totalReceivables.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)' }}>
            {t('tx.total_inflow_sub', 'Total customer dues & receipts')}
          </div>
        </div>

        <div className="fin-card fin-card-red">
          <div style={{ fontSize: '0.75rem', color: 'var(--udhaar-red-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            {t('tx.total_outflow', 'Total Outflow (Payables)')}
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--udhaar-red)', marginTop: '4px' }}>
            -₹{totalPayables.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--udhaar-red-text)' }}>
            {t('tx.total_outflow_sub', 'Total supplier dues & payments')}
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '13px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t('tx.search_placeholder', 'Search by party, keyword, or note...')}
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

        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            onClick={() => setSelectedDirection('')}
            className={`btn ${selectedDirection === '' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            {t('tx.tab_all', 'All Entries')}
          </button>
          <button
            onClick={() => setSelectedDirection('receivable')}
            className={`btn ${selectedDirection === 'receivable' ? 'btn-emerald' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            {t('tx.tab_inflow', '🟢 Inflow (Receivable)')}
          </button>
          <button
            onClick={() => setSelectedDirection('payable')}
            className={`btn ${selectedDirection === 'payable' ? 'btn-danger' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            {t('tx.tab_outflow', '🔴 Outflow (Payable)')}
          </button>
        </div>
      </div>

      {/* Transactions Ledger Table Card */}
      <div className="fin-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '36px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
            {t('tx.loading', 'Loading journal transactions...')}
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state-card" style={{ border: 'none', borderRadius: '0' }}>
            <div className="empty-state-icon">📒</div>
            <h4 style={{ fontSize: '1.15rem', color: 'var(--text-main)', margin: 0, fontWeight: 700 }}>
              {t('tx.no_records_title', 'No Transactions Found')}
            </h4>
            <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              {t('tx.no_records_sub', 'Transactions recorded via voice or chat will automatically appear here.')}
            </span>
            <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
              <span className="prompt-chip">🎙️ "Ramesh 500 ichadu"</span>
              <span className="prompt-chip">🎙️ "Pawan ki 8000 ivvali"</span>
            </div>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="fin-table">
              <thead>
                <tr>
                  <th style={{ minWidth: '105px' }}>{t('tx.th_date', 'Date')}</th>
                  <th style={{ minWidth: '160px' }}>{t('tx.th_party', 'Party / Business')}</th>
                  <th style={{ minWidth: '120px' }}>{t('tx.th_type', 'Type')}</th>
                  <th style={{ minWidth: '130px' }}>{t('tx.th_direction', 'Direction')}</th>
                  <th style={{ minWidth: '120px', textAlign: 'right' }}>{t('tx.th_amount', 'Amount (₹)')}</th>
                  <th style={{ minWidth: '120px', textAlign: 'right' }}>{t('tx.th_balance', 'Balance')}</th>
                  <th style={{ minWidth: '110px' }}>{t('tx.th_method', 'Method')}</th>
                  <th style={{ minWidth: '100px' }}>{t('tx.th_audit', 'Audit')}</th>
                  <th style={{ minWidth: '120px', textAlign: 'center' }}>{t('tx.th_actions', 'Action')}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((tx) => {
                  const txType = (tx.transaction_type || '').toUpperCase();
                  const isPayable = tx.direction === 'payable' || tx.counterparty_type === 'supplier';
                  const isPaymentMade = isPayable && (txType.includes('PAYMENT') || tx.status === 'SETTLED');
                  const isPaymentRecv = !isPayable && (txType.includes('PAYMENT') || txType.includes('RECEIVED') || tx.status === 'PARTIAL_PAYMENT');

                  let badgeClass = 'badge-emerald';
                  let badgeText = `🟢 ${t('term.receivable', 'Receivable')}`;
                  let amountColor = 'var(--receivable-color)';

                  if (isPaymentMade) {
                    badgeClass = 'badge-amber';
                    badgeText = `💸 ${t('term.paid', 'Paid')}`;
                    amountColor = 'var(--paid-color)';
                  } else if (isPaymentRecv) {
                    badgeClass = 'badge-cyan';
                    badgeText = `💰 ${t('term.received', 'Received')}`;
                    amountColor = 'var(--received-color)';
                  } else if (isPayable) {
                    badgeClass = 'badge-rose';
                    badgeText = `🔴 ${t('term.payable', 'Payable')}`;
                    amountColor = 'var(--payable-color)';
                  }

                  const isSelected = selectedTransaction?.id === tx.id;
                  return (
                    <tr
                      key={tx.id}
                      onClick={() => setSelectedTransaction(tx)}
                      style={{
                        cursor: 'pointer',
                        background: isSelected ? 'rgba(2, 132, 199, 0.09)' : 'transparent',
                        borderLeft: isSelected ? '4px solid var(--accent-primary)' : '4px solid transparent'
                      }}
                    >
                      <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)', fontWeight: 500 }}>
                        {tx.date}
                      </td>
                      <td>
                        <div style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '0.92rem' }}>
                          {tx.counterparty_name}
                        </div>
                        {tx.source_text && (
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontStyle: 'italic', maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            "{tx.source_text}"
                          </div>
                        )}
                      </td>
                      <td>
                        <span className="badge badge-neutral" style={{ fontSize: '0.72rem', fontWeight: 600 }}>
                          {tx.transaction_type}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${badgeClass}`} style={{ fontSize: '0.74rem' }}>
                          {badgeText}
                        </span>
                      </td>
                      <td className="tabular-nums" style={{ textAlign: 'right', fontWeight: 800, fontSize: '0.98rem', color: amountColor }}>
                        {isPaymentMade ? '-' : isPaymentRecv ? '+' : isPayable ? '-' : '+'}₹{Number(tx.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="tabular-nums" style={{ textAlign: 'right', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
                        ₹{Number(tx.balance_after || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td style={{ fontSize: '0.8rem', textTransform: 'capitalize', color: 'var(--text-muted)' }}>
                        {tx.payment_method || 'Cash'}
                      </td>
                      <td>
                        <span className="badge badge-neutral" style={{ fontSize: '0.7rem', color: 'var(--cyan)', border: '1px solid rgba(6, 182, 212, 0.3)' }}>
                          <ShieldCheck size={11} color="var(--cyan)" />
                          {Math.round((tx.confidence || 0.95) * 100)}%
                        </span>
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setEditingTx(tx);
                              setIsEditModalOpen(true);
                            }}
                            className="btn btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            title="Edit Entry"
                          >
                            <Edit2 size={12} /> {t('btn.edit', 'Edit')}
                          </button>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteDirect(tx.id);
                            }}
                            className="btn btn-danger-subtle"
                            style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            title="Delete Entry"
                          >
                            <Trash2 size={12} /> {t('btn.delete', 'Delete')}
                          </button>
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

      {/* Universal Edit Transaction Modal */}
      <EditTransactionModal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setEditingTx(null);
        }}
        transaction={editingTx}
        onSaved={() => loadTransactions()}
        onDeleted={() => loadTransactions()}
      />
    </div>
  );
};
