import React, { useState, useEffect } from 'react';
import {
  X,
  User,
  Truck,
  Smartphone,
  MessageCircle,
  FileText,
  Printer,
  Edit2,
  Trash2,
  TrendingDown,
  TrendingUp,
  Clock,
  CheckCircle2,
  Scale
} from 'lucide-react';
import { api } from '../api/client';
import { EditTransactionModal } from './EditTransactionModal';
import { notifyLedgerUpdated } from '../utils/events';

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
        const cp = (tx.counterparty || '').toLowerCase();
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

  // Calculate Running Totals
  const totalDebit = transactions
    .filter((t) => t.direction === 'IN' || t.direction === 'OUT')
    .reduce((sum, t) => sum + (t.amount || 0), 0);

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
    let statementText = isCustomer
      ? `నమస్కారం ${entity.name_telugu || entity.name} గారు,\nమీ వ్యాపార ఖాతా వివరాలు:\n`
      : `నమస్కారం ${entity.name_telugu || entity.name} గారు,\nసప్లయర్ ఖాతా వివరాలు:\n`;

    statementText += `బాకీ నిల్వ: ₹${outstanding.toLocaleString('en-IN', { minimumFractionDigits: 2 })}\n\nలావాదేవీలు:\n`;

    transactions.slice(0, 8).forEach((tx) => {
      statementText += `• ${tx.date || tx.created_at?.slice(0, 10)}: ${tx.direction === 'IN' ? 'వచ్చినవి (Received)' : 'ఇచ్చినవి (Due)'} ₹${tx.amount?.toLocaleString()} (${tx.description || tx.raw_query || ''})\n`;
    });

    statementText += `\nధన్యవాదాలు!`;

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
                  {entity.name_telugu && entity.name_telugu !== entity.name && (
                    <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginLeft: '8px', fontWeight: 500 }}>
                      ({entity.name_telugu})
                    </span>
                  )}
                </h3>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '2px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span>{isCustomer ? 'కస్టమర్ ఖాతా బుక్ (Customer Ledger)' : 'సప్లయర్ ఖాతా బుక్ (Supplier Ledger)'}</span>
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
                {isCustomer ? 'మొత్తం రావాల్సిన బాకీ' : 'మొత్తం ఇవ్వాల్సిన బాకీ'}
              </span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: outstanding > 0 ? (isCustomer ? 'var(--jama-green)' : 'var(--udhaar-red)') : 'var(--text-main)', marginTop: '2px' }}>
                ₹{outstanding.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
            </div>

            <div className="fin-card" style={{ padding: '12px 16px', background: 'var(--bg-card-subtle)' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                లావాదేవీల సంఖ్య (Total Records)
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
                <MessageCircle size={16} /> WhatsApp స్టేట్‌మెంట్
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

          {/* Transactions Ledger Body */}
          <div style={{ padding: '20px 24px', flex: 1, overflowY: 'auto' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={16} color="var(--receivable-color)" />
              వ్యక్తిగత ఖాతా చరిత్ర (Individual Ledger History)
            </h4>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-dim)' }}>
                లావాదేవీలు లోడ్ అవుతున్నాయి...
              </div>
            ) : transactions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 16px', background: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-md)', border: '1px dashed var(--border-color)' }}>
                <CheckCircle2 size={36} color="var(--receivable-color)" style={{ margin: '0 auto 8px' }} />
                <p style={{ fontWeight: 600, color: 'var(--text-main)' }}>ఈ ఖాతాపై ఎలాంటి విడి లావాదేవీలు నమోదు కాలేదు</p>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>వాయిస్ లేదా చాట్ ద్వారా లావాదేవీని నమోదు చేసినప్పుడు అవి ఇక్కడ కనిపిస్తాయి.</span>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="khata-table">
                  <thead>
                    <tr>
                      <th>తేదీ (Date)</th>
                      <th>వివరణ (Description)</th>
                      <th>రకం (Direction)</th>
                      <th style={{ textAlign: 'right' }}>మొత్తం (Amount)</th>
                      <th>పద్ధతి (Method)</th>
                      <th style={{ textAlign: 'center' }}>చర్యలు (Actions)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((tx) => {
                      const isIn = tx.direction === 'IN';
                      return (
                        <tr key={tx.id}>
                          <td style={{ fontWeight: 600, fontSize: '0.82rem' }}>
                            {tx.date || tx.created_at?.slice(0, 10)}
                          </td>
                          <td>
                            <div style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.85rem' }}>
                              {tx.description || tx.raw_query || 'లావాదేవీ'}
                            </div>
                          </td>
                          <td>
                            <span className={`badge ${isIn ? 'badge-jama' : 'badge-udhaar'}`} style={{ fontSize: '0.72rem' }}>
                              {isIn ? '↓ వచ్చింది (Received)' : '↑ ఇచ్చింది (Due / Paid)'}
                            </span>
                          </td>
                          <td style={{ textAlign: 'right', fontWeight: 800, fontSize: '0.92rem', color: isIn ? 'var(--jama-green)' : 'var(--udhaar-red)' }}>
                            ₹{Number(tx.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                          </td>
                          <td>
                            <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                              {tx.payment_mode || 'నగదు'}
                            </span>
                          </td>
                          <td style={{ textAlign: 'center' }}>
                            <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                              <button
                                onClick={() => handleEditClick(tx)}
                                className="btn-outline"
                                style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                                title="సవరించు (Edit)"
                              >
                                <Edit2 size={12} /> సవరించు
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
              డబుల్ ఎంట్రీ ఆడిట్ వెరిఫైడ్ • డెబిట్/క్రెడిట్ సమతుల్యత
            </span>
            <button onClick={onClose} className="btn-outline" style={{ padding: '6px 16px', fontSize: '0.82rem' }}>
              మూసివేయి (Close)
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
          onSuccess={handleTxSavedOrDeleted}
        />
      )}
    </>
  );
};
