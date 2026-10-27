import React, { useState, useEffect } from 'react';
import {
  ArrowDownLeft,
  Search,
  CheckCircle,
  MessageSquare,
  Edit2,
  Trash2
} from 'lucide-react';
import { api } from '../api/client';
import { EditTransactionModal } from '../components/EditTransactionModal';
import { useLedgerUpdated } from '../utils/events';
import { useLanguage } from '../context/LanguageContext';

export const ReceivedView: React.FC = () => {
  const { t, language } = useLanguage();
  const [transactions, setTransactions] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [methodFilter, setMethodFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // Edit/Delete modal state
  const [editingTx, setEditingTx] = useState<any>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    loadReceivedTransactions();
  }, []);

  useLedgerUpdated(() => {
    loadReceivedTransactions();
  });

  const loadReceivedTransactions = async () => {
    try {
      setLoading(true);
      const allTx = await api.getTransactions({ limit: 100 });
      // Received transactions: payments received from customers, settlements, or cash sales
      const received = allTx.filter((t: any) =>
        t.transaction_type === 'PAYMENT_RECEIVED' ||
        t.transaction_type === 'SETTLEMENT' ||
        t.transaction_type === 'CASH_SALE' ||
        (t.direction === 'receivable' && (t.status === 'SETTLED' || t.status === 'PARTIAL_SETTLEMENT')) ||
        (t.source_text && (
          t.source_text.toLowerCase().includes('ichadu') ||
          t.source_text.toLowerCase().includes('vachindi') ||
          t.source_text.toLowerCase().includes('settle') ||
          t.source_text.toLowerCase().includes('kattadu') ||
          t.source_text.toLowerCase().includes('kuduthan') ||
          t.source_text.toLowerCase().includes('kodutha') ||
          t.source_text.toLowerCase().includes('diye') ||
          t.source_text.toLowerCase().includes('mil gaya') ||
          t.source_text.toLowerCase().includes('చెల్లించాడు') ||
          t.source_text.toLowerCase().includes('ఇచ్చాడు') ||
          t.source_text.toLowerCase().includes('వచ్చింది')
        ))
      );
      setTransactions(received);
    } catch (err) {
      console.error('Failed to load received transactions', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDirect = async (txId: string) => {
    if (window.confirm(t('recv.confirm_delete', 'Are you sure you want to delete this payment receipt? Customer balance will be automatically adjusted.'))) {
      try {
        await api.deleteTransaction(txId);
        loadReceivedTransactions();
      } catch (err: any) {
        alert("Error deleting transaction: " + err.message);
      }
    }
  };

  const filtered = transactions.filter((t) => {
    const matchesSearch =
      t.counterparty_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.source_text?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMethod = methodFilter ? (t.payment_method?.toLowerCase() === methodFilter.toLowerCase()) : true;
    return matchesSearch && matchesMethod;
  });

  const totalReceived = transactions.reduce((sum, t) => sum + (t.amount || 0), 0);
  const upiReceived = transactions
    .filter((t) => (t.payment_method || '').toLowerCase().includes('upi') || (t.payment_method || '').toLowerCase().includes('online'))
    .reduce((sum, t) => sum + (t.amount || 0), 0);
  const cashReceived = totalReceived - upiReceived;

  const handleShareReceipt = (tx: any) => {
    const template = t('wa.receipt_msg', '🙏 Hello {name}!\n\nWe have successfully received payment of ₹{amount}.\nDate: {date}\nReceipt #: #{id}\nRemaining Balance: ₹{balance}\n\nThank you! - Your Ledger.');
    const formatted = template
      .replace('{name}', tx.counterparty_name || '')
      .replace('{amount}', Number(tx.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 }))
      .replace('{date}', tx.date || '')
      .replace('{id}', String(tx.id || ''))
      .replace('{balance}', Number(tx.balance_after || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 }));
    
    window.open(`https://wa.me/?text=${encodeURIComponent(formatted)}`, '_blank');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Header Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <span style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--jama-green-bg)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: 'var(--jama-green)' }}>
              <ArrowDownLeft size={20} />
            </span>
            {t('recv.title', 'Received Inflows & Collections')}
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {t('recv.desc', 'All customer cash receipts, online UPI collections, and receivable reductions.')}
          </p>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        <div className="fin-card fin-card-green">
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            {t('recv.total_inflow', 'Total Inflows Received')}
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--jama-green)', marginTop: '4px' }}>
            ₹{totalReceived.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)', marginTop: '4px' }}>
            👥 <strong>{transactions.length}</strong> {t('recv.tx_count', 'collections recorded')}
          </div>
        </div>

        <div className="fin-card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            {t('recv.cash_inflow', 'Cash Inflow')}
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '4px' }}>
            ₹{cashReceived.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {t('recv.cash_sub', 'Direct physical cash received')}
          </div>
        </div>

        <div className="fin-card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            {t('recv.upi_inflow', 'UPI & Digital')}
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--cyan)', marginTop: '4px' }}>
            ₹{upiReceived.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {t('recv.upi_sub', 'PhonePe, GPay, Paytm collections')}
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
            placeholder={t('recv.search_placeholder', 'Search received transaction or customer...')}
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
            onClick={() => setMethodFilter('')}
            className={`btn ${methodFilter === '' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            {t('recv.tab_all', 'All Methods')}
          </button>
          <button
            onClick={() => setMethodFilter('cash')}
            className={`btn ${methodFilter === 'cash' ? 'btn-emerald' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            {t('recv.tab_cash', 'Cash')}
          </button>
          <button
            onClick={() => setMethodFilter('upi')}
            className={`btn ${methodFilter === 'upi' ? 'btn-emerald' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            {t('recv.tab_upi', 'UPI / Digital')}
          </button>
        </div>
      </div>

      {/* Received Collections Table Card */}
      <div className="fin-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '36px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
            {t('recv.loading', 'Loading received payment transactions...')}
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.92rem' }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>💰</div>
            <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
              {t('recv.no_records_title', 'No Received Payments Yet')}
            </div>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              {t('recv.no_records_sub', 'When a customer pays, record via voice or chat!')}
            </span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="fin-table">
              <thead>
                <tr>
                  <th style={{ minWidth: '100px' }}>{t('recv.th_receipt_no', 'Receipt #')}</th>
                  <th style={{ minWidth: '110px' }}>{t('recv.th_date', 'Date')}</th>
                  <th style={{ minWidth: '160px' }}>{t('recv.th_customer', 'Customer Name')}</th>
                  <th style={{ minWidth: '130px' }}>{t('recv.th_type', 'Type')}</th>
                  <th style={{ minWidth: '130px', textAlign: 'right' }}>{t('recv.th_amount', 'Received Amount')}</th>
                  <th style={{ minWidth: '120px', textAlign: 'right' }}>{t('recv.th_balance', 'Balance Remaining')}</th>
                  <th style={{ minWidth: '110px' }}>{t('recv.th_method', 'Method')}</th>
                  <th style={{ minWidth: '110px', textAlign: 'center' }}>{t('recv.th_wa_receipt', 'WhatsApp Receipt')}</th>
                  <th style={{ minWidth: '130px', textAlign: 'center' }}>{t('recv.th_actions', 'Actions')}</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((tx) => (
                  <tr key={tx.id}>
                    <td style={{ fontSize: '0.78rem', color: 'var(--text-dim)', fontWeight: 600 }}>
                      #{tx.id}
                    </td>
                    <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
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
                      <span className="badge badge-jama" style={{ fontSize: '0.72rem' }}>
                        <CheckCircle size={12} />
                        {tx.transaction_type === 'SETTLEMENT' ? t('recv.type_settlement', 'Full Settlement') : t('recv.type_collection', 'Cash Receipt')}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 800, fontSize: '1.05rem', color: 'var(--jama-green)' }}>
                      +₹{Number(tx.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
                      ₹{Number(tx.balance_after || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td>
                      <span className="badge badge-neutral" style={{ fontSize: '0.72rem', textTransform: 'capitalize' }}>
                        {tx.payment_method || 'Cash'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        onClick={() => handleShareReceipt(tx)}
                        className="btn-whatsapp"
                        style={{ padding: '5px 10px', fontSize: '0.74rem' }}
                        title="Send WhatsApp Payment Confirmation Receipt"
                      >
                        <MessageSquare size={13} /> {t('recv.send_receipt_btn', 'Send Receipt')}
                      </button>
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                        <button
                          type="button"
                          onClick={() => {
                            setEditingTx(tx);
                            setIsEditModalOpen(true);
                          }}
                          className="btn btn-secondary"
                          style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                          title="Edit Received Payment"
                        >
                          <Edit2 size={12} /> {t('btn.edit', 'Edit')}
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDeleteDirect(tx.id)}
                          className="btn btn-danger-subtle"
                          style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                          title="Delete Received Payment"
                        >
                          <Trash2 size={12} /> {t('btn.delete', 'Delete')}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
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
        onSaved={() => loadReceivedTransactions()}
        onDeleted={() => loadReceivedTransactions()}
      />

    </div>
  );
};
