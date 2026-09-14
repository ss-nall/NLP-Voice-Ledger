import React, { useState, useEffect } from 'react';
import { Edit3, Check, X, Trash2, AlertCircle } from 'lucide-react';
import { api } from '../api/client';
import { notifyLedgerUpdated } from '../utils/events';

interface EditTransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  transaction: any;
  onSaved?: (updatedTx: any) => void;
  onDeleted?: (deletedId: string) => void;
  onSuccess?: () => void;
}

export const EditTransactionModal: React.FC<EditTransactionModalProps> = ({
  isOpen,
  onClose,
  transaction,
  onSaved,
  onDeleted,
  onSuccess
}) => {
  const [counterpartyName, setCounterpartyName] = useState('');
  const [amount, setAmount] = useState<number | string>('');
  const [direction, setDirection] = useState<'receivable' | 'payable'>('receivable');
  const [transactionType, setTransactionType] = useState('CREDIT_SALE');
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [date, setDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    if (transaction) {
      setCounterpartyName(transaction.counterparty_name || transaction.actor || '');
      setAmount(transaction.amount || '');
      setDirection(transaction.direction === 'payable' ? 'payable' : 'receivable');
      setTransactionType(transaction.transaction_type || 'CREDIT_SALE');
      setPaymentMethod(transaction.payment_method || 'cash');
      setDate(transaction.date || new Date().toISOString().split('T')[0]);
      setError(null);
      setConfirmDelete(false);
    }
  }, [transaction, isOpen]);

  if (!isOpen || !transaction) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!counterpartyName.trim()) {
      setError('దయచేసి పేరు నమోదు చేయండి (Please enter counterparty name)');
      return;
    }
    const numAmount = Number(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      setError('దయచేసి సరైన మొత్తం నమోదు చేయండి (Please enter a valid amount > 0)');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const res = await api.updateTransaction(transaction.id, {
        counterparty_name: counterpartyName.trim(),
        amount: numAmount,
        direction,
        transaction_type: transactionType,
        payment_method: paymentMethod,
        date
      });
      notifyLedgerUpdated();
      if (onSaved) onSaved(res);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Error updating transaction');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    setError(null);
    try {
      await api.deleteTransaction(transaction.id);
      notifyLedgerUpdated();
      if (onDeleted) onDeleted(transaction.id);
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Error deleting transaction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.65)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      backdropFilter: 'blur(4px)'
    }}>
      <div className="modal-card" style={{
        background: 'var(--bg-card, #ffffff)',
        color: 'var(--text-main, #1e293b)',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '520px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1)',
        border: '1px solid var(--border-color, #e2e8f0)',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '16px 20px',
          background: 'var(--primary-light, #eff6ff)',
          borderBottom: '1px solid var(--border-color, #e2e8f0)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'var(--primary-color, #2563eb)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Edit3 size={18} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700 }}>
                లావాదేవీ సవరణ (Edit Transaction)
              </h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted, #64748b)' }}>
                ID: {transaction.id}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-muted, #64748b)',
              padding: '4px',
              borderRadius: '6px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Form */}
        <form onSubmit={handleSave} style={{ padding: '20px' }}>
          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 14px',
              background: '#fef2f2',
              color: '#dc2626',
              borderRadius: '8px',
              fontSize: '0.85rem',
              marginBottom: '16px',
              border: '1px solid #fecaca'
            }}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {/* Counterparty Name */}
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
              వ్యక్తి / వ్యాపారం పేరు (Counterparty Name)
            </label>
            <input
              type="text"
              value={counterpartyName}
              onChange={(e) => setCounterpartyName(e.target.value)}
              placeholder="e.g. Ramesh, Deepak, Balaji Kirana"
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                border: '1px solid var(--border-color, #cbd5e1)',
                background: 'var(--bg-input, #ffffff)',
                color: 'inherit',
                fontSize: '0.95rem'
              }}
              required
            />
          </div>

          {/* Amount & Date */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                మొత్తం (Amount ₹)
              </label>
              <input
                type="number"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color, #cbd5e1)',
                  background: 'var(--bg-input, #ffffff)',
                  color: 'inherit',
                  fontSize: '0.95rem',
                  fontWeight: 600
                }}
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                తేదీ (Date)
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color, #cbd5e1)',
                  background: 'var(--bg-input, #ffffff)',
                  color: 'inherit',
                  fontSize: '0.95rem'
                }}
                required
              />
            </div>
          </div>

          {/* Direction & Type */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                దిశ (Direction)
              </label>
              <select
                value={direction}
                onChange={(e) => setDirection(e.target.value as 'receivable' | 'payable')}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color, #cbd5e1)',
                  background: 'var(--bg-input, #ffffff)',
                  color: 'inherit',
                  fontSize: '0.9rem'
                }}
              >
                <option value="receivable">కస్టమర్ రావలసినవి / వచ్చినవి (Customer - Receivable)</option>
                <option value="payable">సప్లయర్ ఇవ్వవలసినవి / చెల్లించినవి (Supplier - Payable)</option>
              </select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
                లావాదేవీ రకం (Tx Type)
              </label>
              <select
                value={transactionType}
                onChange={(e) => setTransactionType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color, #cbd5e1)',
                  background: 'var(--bg-input, #ffffff)',
                  color: 'inherit',
                  fontSize: '0.9rem'
                }}
              >
                {direction === 'receivable' ? (
                  <>
                    <option value="CREDIT_SALE">అప్పు సరుకు (Credit Sale - Owed)</option>
                    <option value="PAYMENT_RECEIVED">డబ్బులు వచ్చినవి (Payment Received)</option>
                    <option value="RECEIVABLE_INVOICE">ఇన్వాయిస్ (Invoice)</option>
                  </>
                ) : (
                  <>
                    <option value="PURCHASE">సరుకు కొనుగోలు (Purchase - Owed)</option>
                    <option value="PAYMENT_MADE">డబ్బులు చెల్లించినవి (Payment Made)</option>
                    <option value="PAYABLE_OBLIGATION">బాకీ (Payable Obligation)</option>
                  </>
                )}
              </select>
            </div>
          </div>

          {/* Payment Method */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
              చెల్లింపు విధానం (Payment Method)
            </label>
            <select
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                borderRadius: '8px',
                border: '1px solid var(--border-color, #cbd5e1)',
                background: 'var(--bg-input, #ffffff)',
                color: 'inherit',
                fontSize: '0.9rem'
              }}
            >
              <option value="cash">నగదు (Cash)</option>
              <option value="upi">యూపీఐ (UPI / PhonePe / GPay)</option>
              <option value="bank_transfer">బ్యాంక్ ఖాతా (Bank Transfer)</option>
              <option value="cheque">చెక్కు (Cheque)</option>
            </select>
          </div>

          {/* Confirmation Box for Delete */}
          {confirmDelete && (
            <div style={{
              padding: '14px',
              background: '#fef2f2',
              borderRadius: '10px',
              marginBottom: '18px',
              border: '1px solid #f87171'
            }}>
              <p style={{ margin: '0 0 10px 0', fontSize: '0.85rem', fontWeight: 600, color: '#991b1b' }}>
                ఈ లావాదేవీని ఖచ్చితంగా తొలగించాలనుకుంటున్నారా? (Are you sure you want to delete this transaction?)
              </p>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setConfirmDelete(false)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e1',
                    background: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '0.8rem'
                  }}
                >
                  రద్దు (Cancel)
                </button>
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={loading}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '6px',
                    border: 'none',
                    background: '#dc2626',
                    color: '#ffffff',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: 600
                  }}
                >
                  {loading ? 'తొలగిస్తోంది...' : 'అవును, తొలగించు (Confirm Delete)'}
                </button>
              </div>
            </div>
          )}

          {/* Modal Actions */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '10px' }}>
            {!confirmDelete ? (
              <button
                type="button"
                onClick={() => setConfirmDelete(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '9px 14px',
                  borderRadius: '8px',
                  border: '1px solid #fecaca',
                  background: '#fff5f5',
                  color: '#dc2626',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: 600
                }}
              >
                <Trash2 size={16} />
                <span>తొలగించు (Delete)</span>
              </button>
            ) : <div />}

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button"
                onClick={onClose}
                style={{
                  padding: '9px 16px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color, #cbd5e1)',
                  background: 'transparent',
                  color: 'inherit',
                  cursor: 'pointer',
                  fontSize: '0.85rem'
                }}
              >
                రద్దు (Cancel)
              </button>
              <button
                type="submit"
                disabled={loading}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '9px 20px',
                  borderRadius: '8px',
                  border: 'none',
                  background: 'var(--primary-color, #2563eb)',
                  color: '#ffffff',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  opacity: loading ? 0.7 : 1
                }}
              >
                <Check size={16} />
                <span>{loading ? 'భద్రపరుస్తోంది...' : 'భద్రపరచు (Save Changes)'}</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
