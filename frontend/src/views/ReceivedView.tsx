import React, { useState, useEffect } from 'react';
import {
  ArrowDownLeft,
  Search,
  CheckCircle,
  MessageSquare,
  Smartphone,
  Calendar,
  Layers,
  FileCheck,
  ShieldCheck,
  TrendingUp,
  Receipt,
  Edit2,
  Trash2
} from 'lucide-react';
import { api } from '../api/client';
import { EditTransactionModal } from '../components/EditTransactionModal';
import { useLedgerUpdated } from '../utils/events';

export const ReceivedView: React.FC = () => {
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
    if (window.confirm("ఈ రశీదును తొలగించాలనుకుంటున్నారా? కస్టమర్ బాకీ నిల్వ ఆటోమేటిక్ గా సరిచేయబడుతుంది.")) {
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
    const msg = encodeURIComponent(
      `🙏 నమస్కారం ${tx.counterparty_name} గారు!\n\nమీ నుండి ₹${Number(tx.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })} నగదు విజయవంతంగా అందింది.\nతేదీ: ${tx.date}\nరసీదు నెం: #${tx.id}\nమిగిలిన బాకీ నిల్వ: ₹${Number(tx.balance_after || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}\n\nధన్యవాదాలు! - మీ దుకాణం లెక్కలు.`
    );
    window.open(`https://wa.me/?text=${msg}`, '_blank');
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
            వచ్చిన నగదు & వసూళ్లు (Received Collections)
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            కస్టమర్ల నుండి అందిన చెల్లింపులు, వసూలైన నగదు రశీదులు మరియు సెటిల్‌మెంట్స్ రికార్డు.
          </p>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        <div className="fin-card fin-card-green">
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            మొత్తం వసూలైన నగదు (Total Received)
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--jama-green)', marginTop: '4px' }}>
            ₹{totalReceived.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)', marginTop: '4px' }}>
            👥 మొత్తం <strong>{transactions.length}</strong> చెల్లింపు రశీదులు
          </div>
        </div>

        <div className="fin-card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            నగదు వసూళ్లు (Cash Inflow)
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '4px' }}>
            ₹{cashReceived.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            ప్రత్యక్ష నగదు రూపంలో అందిన మొత్తం
          </div>
        </div>

        <div className="fin-card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            యూపీఐ / ఆన్‌లైన్ (UPI & Digital)
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--cyan)', marginTop: '4px' }}>
            ₹{upiReceived.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            PhonePe, GPay, Paytm కలెక్షన్లు
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
            placeholder="కస్టమర్ పేరు లేదా వివరాలతో వెతకండి (Search received)..."
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
            అన్ని పద్ధతులు (All)
          </button>
          <button
            onClick={() => setMethodFilter('cash')}
            className={`btn ${methodFilter === 'cash' ? 'btn-emerald' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            నగదు (Cash)
          </button>
          <button
            onClick={() => setMethodFilter('upi')}
            className={`btn ${methodFilter === 'upi' ? 'btn-emerald' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            UPI / Digital
          </button>
        </div>
      </div>

      {/* Received Collections Table Card */}
      <div className="fin-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '36px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
            వసూళ్ల వివరాలు లోడ్ అవుతున్నాయి...
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.92rem' }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>💰</div>
            <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
              ఇంకా ఏ వసూళ్లు నమోదు కాలేదు (No Received Payments Yet)
            </div>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              కస్టమర్ డబ్బులు ఇచ్చినప్పుడు వాయిస్ లో 'రమేష్ 1000 ఇచ్చాడు' లేదా 'Customer 500 ichadu' అని చెప్పండి!
            </span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="fin-table">
              <thead>
                <tr>
                  <th style={{ minWidth: '100px' }}>రశీదు #</th>
                  <th style={{ minWidth: '110px' }}>తేదీ (Date)</th>
                  <th style={{ minWidth: '160px' }}>కస్టమర్ పేరు (Customer)</th>
                  <th style={{ minWidth: '130px' }}>రకం (Type)</th>
                  <th style={{ minWidth: '130px', textAlign: 'right' }}>స్వీకరించిన నగదు (Received ₹)</th>
                  <th style={{ minWidth: '120px', textAlign: 'right' }}>మిగిలిన బాకీ (Balance)</th>
                  <th style={{ minWidth: '110px' }}>విధానం (Method)</th>
                  <th style={{ minWidth: '110px', textAlign: 'center' }}>వాట్సాప్ రశీదు (Receipt)</th>
                  <th style={{ minWidth: '130px', textAlign: 'center' }}>చర్యలు (Actions)</th>
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
                        {tx.transaction_type === 'SETTLEMENT' ? 'పూర్తి సెటిల్మెంట్' : 'నగదు వసూలు'}
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
                        <MessageSquare size={13} /> రశీదు పంపు
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
                          <Edit2 size={12} /> సవరించు
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDeleteDirect(tx.id)}
                          className="btn btn-danger-subtle"
                          style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                          title="Delete Received Payment"
                        >
                          <Trash2 size={12} /> తొలగించు
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
