import React, { useState, useEffect } from 'react';
import {
  ArrowUpRight,
  Search,
  CheckCircle,
  Truck,
  CreditCard,
  Calendar,
  Layers,
  FileText,
  ShieldCheck,
  TrendingDown,
  Receipt,
  Edit2,
  Trash2
} from 'lucide-react';
import { api } from '../api/client';
import { EditTransactionModal } from '../components/EditTransactionModal';
import { useLedgerUpdated } from '../utils/events';

export const PaidView: React.FC = () => {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [methodFilter, setMethodFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // Edit/Delete modal state
  const [editingTx, setEditingTx] = useState<any>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  useEffect(() => {
    loadPaidTransactions();
  }, []);

  useLedgerUpdated(() => {
    loadPaidTransactions();
  });

  const loadPaidTransactions = async () => {
    try {
      setLoading(true);
      const allTx = await api.getTransactions({ limit: 100 });
      // Paid transactions: supplier payments, operating expenses, settlements
      const paid = allTx.filter((t: any) =>
        t.transaction_type === 'PAYMENT_MADE' ||
        t.transaction_type === 'EXPENSE' ||
        t.transaction_type === 'SUPPLIER_PAYMENT' ||
        (t.direction === 'payable' && (t.status === 'SETTLED' || t.status === 'PARTIAL_PAYMENT')) ||
        (t.source_text && (
          t.source_text.toLowerCase().includes('kattanu') ||
          t.source_text.toLowerCase().includes('kattesa') ||
          t.source_text.toLowerCase().includes('icheshanu') ||
          t.source_text.toLowerCase().includes('ichanu') ||
          t.source_text.toLowerCase().includes('paid') ||
          t.source_text.toLowerCase().includes('చెల్లించాను') ||
          t.source_text.toLowerCase().includes('కట్టేశాను') ||
          t.source_text.toLowerCase().includes('ఇచ్చేశాను')
        ))
      );
      setTransactions(paid);
    } catch (err) {
      console.error('Failed to load paid transactions', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDirect = async (txId: string) => {
    if (window.confirm("ఈ చెల్లింపు వోచర్‌ను తొలగించాలనుకుంటున్నారా? సప్లయర్ బాకీ నిల్వ ఆటోమేటిక్ గా సరిచేయబడుతుంది.")) {
      try {
        await api.deleteTransaction(txId);
        loadPaidTransactions();
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

  const totalPaid = transactions.reduce((sum, t) => sum + (t.amount || 0), 0);
  const supplierPaid = transactions
    .filter((t) => t.counterparty_type === 'supplier' || (t.counterparty_name || '').toLowerCase().includes('supplier'))
    .reduce((sum, t) => sum + (t.amount || 0), 0);
  const otherExpenses = totalPaid - supplierPaid;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      
      {/* Header Banner */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <span style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--udhaar-red-bg)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', color: 'var(--udhaar-red)' }}>
              <ArrowUpRight size={20} />
            </span>
            చెల్లించినవి & ఖర్చులు (Paid Outflows & Expenses)
          </h2>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            సప్లయర్లకు చెల్లించిన నగదు, వ్యాపార ఖర్చులు మరియు చెల్లింపు వోచర్లు.
          </p>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        <div className="fin-card fin-card-red">
          <div style={{ fontSize: '0.75rem', color: 'var(--udhaar-red-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            మొత్తం చెల్లించిన నగదు (Total Paid)
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--udhaar-red)', marginTop: '4px' }}>
            ₹{totalPaid.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--udhaar-red-text)', marginTop: '4px' }}>
            🚚 మొత్తం <strong>{transactions.length}</strong> చెల్లింపు వోచర్లు
          </div>
        </div>

        <div className="fin-card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            సప్లయర్ చెల్లింపులు (To Suppliers)
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '4px' }}>
            ₹{supplierPaid.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            డీలర్లు & హోల్‌సేలర్లకు క్లియర్ చేసిన మొత్తం
          </div>
        </div>

        <div className="fin-card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            దుకాణం ఖర్చులు (Operating Expenses)
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--amber)', marginTop: '4px' }}>
            ₹{otherExpenses.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            అద్దె, రవాణా & రోజువారీ ఖర్చులు
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
            placeholder="సప్లయర్ పేరు లేదా ఖర్చు వివరాలతో వెతకండి (Search paid)..."
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
            onClick={() => setMethodFilter('bank')}
            className={`btn ${methodFilter === 'bank' ? 'btn-emerald' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            బ్యాంక్ / UPI
          </button>
        </div>
      </div>

      {/* Paid Transactions Table Card */}
      <div className="fin-card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '36px 16px', textAlign: 'center', color: 'var(--text-muted)' }}>
            చెల్లింపుల వివరాలు లోడ్ అవుతున్నాయి...
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.92rem' }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🧾</div>
            <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
              ఇంకా ఏ చెల్లింపులు నమోదు కాలేదు (No Paid Outflows Yet)
            </div>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              సప్లయర్ కి లేదా ఖర్చుల కోసం డబ్బులు చెల్లించినప్పుడు 'సప్లయర్ కి 5000 ఇచ్చేశాను' అని చెప్పండి!
            </span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="fin-table">
              <thead>
                <tr>
                  <th style={{ minWidth: '100px' }}>వోచర్ #</th>
                  <th style={{ minWidth: '110px' }}>తేదీ (Date)</th>
                  <th style={{ minWidth: '160px' }}>సప్లయర్ / లబ్ధిదారు (Party)</th>
                  <th style={{ minWidth: '130px' }}>రకం (Type)</th>
                  <th style={{ minWidth: '130px', textAlign: 'right' }}>చెల్లించిన మొత్తం (Paid ₹)</th>
                  <th style={{ minWidth: '120px', textAlign: 'right' }}>మిగిలిన బాకీ (Balance)</th>
                  <th style={{ minWidth: '110px' }}>విధానం (Method)</th>
                  <th style={{ minWidth: '100px' }}>ఆడిట్ (Status)</th>
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
                      <span className="badge badge-udhaar" style={{ fontSize: '0.72rem' }}>
                        <CheckCircle size={12} />
                        {tx.transaction_type === 'EXPENSE' ? 'దుకాణం ఖర్చు' : 'సప్లయర్ చెల్లింపు'}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 800, fontSize: '1.05rem', color: 'var(--udhaar-red)' }}>
                      -₹{Number(tx.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
                      ₹{Number(tx.balance_after || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                    <td>
                      <span className="badge badge-neutral" style={{ fontSize: '0.72rem', textTransform: 'capitalize' }}>
                        {tx.payment_method || 'Cash'}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-neutral" style={{ fontSize: '0.7rem', color: 'var(--jama-green)' }}>
                        <ShieldCheck size={11} color="var(--jama-green)" />
                        క్లియర్డ్
                      </span>
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
                          title="Edit Paid Voucher"
                        >
                          <Edit2 size={12} /> సవరించు
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDeleteDirect(tx.id)}
                          className="btn btn-danger-subtle"
                          style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                          title="Delete Paid Voucher"
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
        onSaved={() => loadPaidTransactions()}
        onDeleted={() => loadPaidTransactions()}
      />

    </div>
  );
};
