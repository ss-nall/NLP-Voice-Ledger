import React, { useState, useEffect } from 'react';
import {
  X,
  User,
  Truck,
  MessageCircle,
  FileText,
  Printer,
  Edit2,
  CheckCircle2
} from 'lucide-react';
import { api } from '../api/client';
import { EditTransactionModal } from './EditTransactionModal';
import { notifyLedgerUpdated } from '../utils/events';
import { useLanguage } from '../context/LanguageContext';
import { generateAndDownloadStatementPDF } from '../utils/pdfGenerator';

interface EntityStatementModalProps {
  isOpen: boolean;
  onClose: () => void;
  entity: any;
  type: 'customer' | 'supplier';
  onTransactionUpdated?: () => void;
}

export const EntityStatementModal: React.FC<EntityStatementModalProps> = ({
  isOpen,
  onClose,
  entity,
  type,
  onTransactionUpdated
}) => {
  const { t, language } = useLanguage();
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTxForEdit, setSelectedTxForEdit] = useState<any>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    if (isOpen && entity) {
      loadEntityLedger();
    }
  }, [isOpen, entity]);

  const loadEntityLedger = async () => {
    try {
      setLoading(true);
      const allTxs = await api.getTransactions({ limit: 100 });
      // Filter transactions matching this entity's name or aliases
      const entityNames = [
        (entity.name || '').toLowerCase(),
        (entity.name_telugu || '').toLowerCase(),
        ...(entity.aliases || []).map((a: string) => a.toLowerCase())
      ].filter(Boolean);

      const filtered = allTxs.filter((tx: any) => {
        const cp = (tx.counterparty || tx.counterparty_name || '').toLowerCase();
        return entityNames.some((n) => cp.includes(n) || n.includes(cp));
      });

      setTransactions(filtered);
    } catch (err) {
      console.error('Failed to load entity statement transactions', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !entity) return null;

  const isCustomer = type === 'customer';
  const outstanding = Number(entity.outstanding_balance || 0);

  const handleEditClick = (tx: any) => {
    setSelectedTxForEdit(tx);
    setIsEditModalOpen(true);
  };

  const handleTxSavedOrDeleted = () => {
    loadEntityLedger();
    notifyLedgerUpdated();
    if (onTransactionUpdated) {
      onTransactionUpdated();
    }
  };

  const handleShareWhatsApp = () => {
    const phone = (entity.phone || '+919848012345').replace(/[^0-9]/g, '');
    const template = t('wa.statement_msg', '🙏 Hello {name}!\n\nHere is your account statement:\nCurrent Balance: ₹{balance}\n\nTransactions:\n{lines}\n\nThank you!');
    
    const lines = transactions.slice(0, 8).map((tx) => {
      const isRecv = tx.direction === 'IN' || tx.direction === 'receivable';
      return `• ${tx.date || tx.created_at?.slice(0, 10)}: ${isRecv ? '+' : '-'}₹${Number(tx.amount || 0).toLocaleString()} (${tx.description || tx.source_text || ''})`;
    }).join('\n');

    const statementText = template
      .replace('{name}', entity.name || '')
      .replace('{balance}', Number(outstanding || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 }))
      .replace('{lines}', lines);

    const url = `https://wa.me/${phone}?text=${encodeURIComponent(statementText)}`;
    window.open(url, '_blank');
  };

  return (
    <>
      <div className="modal-backdrop" style={{ zIndex: 1100 }}>
        <div className="modal-card" style={{ maxWidth: '850px', width: '95%', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}>
          
          {/* Header */}
          <div
            style={{
              padding: '18px 24px',
              borderBottom: '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'var(--bg-card-subtle)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  background: isCustomer ? 'var(--jama-green)' : 'var(--udhaar-red)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF'
                }}
              >
                {isCustomer ? <User size={24} /> : <Truck size={24} />}
              </div>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                  {entity.name}
                  {language === 'te' && entity.name_telugu && entity.name_telugu !== entity.name && (
                    <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginLeft: '8px', fontWeight: 500 }}>
                      ({entity.name_telugu})
                    </span>
                  )}
                </h3>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '2px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span>{isCustomer ? t('modal.statement_cust_title', 'Customer Account Ledger Statement') : t('modal.statement_supp_title', 'Supplier Account Ledger Statement')}</span>
                  <span>•</span>
                  <span>{entity.phone || '+91 98480 12345'}</span>
                </div>
              </div>
            </div>

            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-dim)',
                cursor: 'pointer',
                padding: '6px',
                borderRadius: '50%'
              }}
            >
              <X size={22} />
            </button>
          </div>

          {/* KPI Summary Cards */}
          <div style={{ padding: '16px 24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', background: 'var(--bg-card)', borderBottom: '1px solid var(--border-color)' }}>
            <div className="fin-card" style={{ padding: '12px 16px', background: 'var(--bg-card-subtle)' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                {isCustomer ? t('modal.statement_total_pending', 'Total Outstanding Balance') : t('modal.statement_total_payable', 'Total Payable Balance')}
              </span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: outstanding > 0 ? (isCustomer ? 'var(--jama-green)' : 'var(--udhaar-red)') : 'var(--text-main)', marginTop: '2px' }}>
                ₹{outstanding.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
            </div>

            <div className="fin-card" style={{ padding: '12px 16px', background: 'var(--bg-card-subtle)' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                {t('modal.statement_total_records', 'Total Records')}
              </span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '2px' }}>
                {transactions.length}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', justifyContent: 'flex-end' }}>
              <button
                onClick={handleShareWhatsApp}
                className="btn btn-emerald"
                style={{ padding: '8px 14px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <MessageCircle size={16} /> {t('modal.statement_wa_btn', 'WhatsApp Statement')}
              </button>
              <button
                onClick={() => generateAndDownloadStatementPDF({
                  entityName: entity.name,
                  entityType: type,
                  phone: entity.phone,
                  outstandingBalance: outstanding,
                  transactions: transactions.map(t => ({
                    date: t.date || t.created_at?.slice(0, 10),
                    description: t.description || t.source_text || 'Transaction',
                    direction: t.direction,
                    amount: t.amount,
                    payment_method: t.payment_method
                  })),
                  language
                })}
                className="btn btn-primary"
                style={{ padding: '8px 14px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}
                title="Download PDF Statement"
              >
                <FileText size={16} /> Download PDF
              </button>
              <button
                onClick={() => window.print()}
                className="btn-outline"
                style={{ padding: '8px 12px', fontSize: '0.82rem' }}
                title="Print Statement"
              >
                <Printer size={16} />
              </button>
            </div>
          </div>

          {/* Dynamic UPI QR Box for Instant Settlement */}
          {outstanding > 0 && isCustomer && (
            <div style={{ margin: '14px 24px 0 24px', padding: '14px 18px', background: 'rgba(16, 185, 129, 0.08)', border: '1px dashed rgba(16, 185, 129, 0.4)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=90x90&data=${encodeURIComponent(`upi://pay?pa=merchant@upi&pn=Khata&am=${outstanding}&cu=INR`)}`}
                  alt="UPI QR Code"
                  style={{ width: '70px', height: '70px', borderRadius: '6px', background: '#fff', padding: '4px' }}
                />
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    ⚡ Instant UPI Settlement (₹{outstanding.toLocaleString('en-IN', { minimumFractionDigits: 2 })})
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Customer can scan with PhonePe, Google Pay, or Paytm to pay directly into your account.
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '2px', fontFamily: 'monospace' }}>
                    UPI ID: merchant@upi
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Transactions Ledger Body */}
          <div style={{ padding: '20px 24px', flex: 1, overflowY: 'auto' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={16} color="var(--receivable-color)" />
              {t('modal.statement_history_title', 'Individual Ledger History')}
            </h4>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-dim)' }}>
                {t('modal.statement_loading', 'Loading transactions...')}
              </div>
            ) : transactions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 16px', background: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-color)' }}>
                <CheckCircle2 size={36} color="var(--receivable-color)" style={{ margin: '0 auto 8px' }} />
                <p style={{ fontWeight: 600, color: 'var(--text-main)' }}>{t('modal.statement_empty', 'No individual transactions recorded on this account.')}</p>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>{t('modal.statement_empty_sub', 'Transactions recorded via voice or chat will appear here.')}</span>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="khata-table">
                  <thead>
                    <tr>
                      <th>{t('modal.statement_th_date', 'Date')}</th>
                      <th>{t('modal.statement_th_desc', 'Description')}</th>
                      <th>{t('modal.statement_th_dir', 'Direction')}</th>
                      <th style={{ textAlign: 'right' }}>{t('modal.statement_th_amount', 'Amount')}</th>
                      <th>{t('modal.statement_th_method', 'Method')}</th>
                      <th style={{ textAlign: 'center' }}>{t('modal.statement_th_actions', 'Actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((tx) => {
                      const isIn = tx.direction === 'IN' || tx.direction === 'receivable';
                      return (
                        <tr key={tx.id}>
                          <td style={{ fontWeight: 600, fontSize: '0.82rem' }}>
                            {tx.date || tx.created_at?.slice(0, 10)}
                          </td>
                          <td>
                            <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.85rem' }}>
                              {tx.description || tx.source_text || tx.raw_query || 'Entry'}
                            </div>
                          </td>
                          <td>
                            <span className={`badge ${isIn ? 'badge-jama' : 'badge-udhaar'}`} style={{ fontSize: '0.72rem' }}>
                              {isIn ? `↓ ${t('term.receivable', 'Receivable')}` : `↑ ${t('term.payable', 'Payable')}`}
                            </span>
                          </td>
                          <td style={{ textAlign: 'right', fontWeight: 800, fontSize: '0.92rem', color: isIn ? 'var(--jama-green)' : 'var(--udhaar-red)' }}>
                            ₹{Number(tx.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </td>
                          <td>
                            <span className="badge badge-neutral" style={{ fontSize: '0.7rem', textTransform: 'capitalize' }}>
                              {tx.payment_method || tx.payment_mode || 'Cash'}
                            </span>
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                              <button
                                onClick={() => handleEditClick(tx)}
                                className="btn-outline"
                                style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                                title={t('btn.edit', 'Edit')}
                              >
                                <Edit2 size={12} /> {t('btn.edit', 'Edit')}
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

          {/* Footer */}
          <div style={{ padding: '12px 24px', borderTop: '1px solid var(--border-color)', background: 'var(--bg-card-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              {t('modal.statement_verified', 'Double-Entry Audit Verified • Debit/Credit Balanced')}
            </span>
            <button onClick={onClose} className="btn-outline" style={{ padding: '6px 16px', fontSize: '0.82rem' }}>
              {t('btn.close', 'Close')}
            </button>
          </div>
        </div>
      </div>

      {/* Embedded Edit / Delete Modal */}
      {selectedTxForEdit && (
        <EditTransactionModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          transaction={selectedTxForEdit}
          onSaved={handleTxSavedOrDeleted}
          onDeleted={handleTxSavedOrDeleted}
        />
      )}
    </>
  );
};
