import React, { useState, useEffect } from 'react';
import {
  ReceiptText,
  Search,
  Filter,
  Info,
  ShieldCheck,
  ArrowDownLeft,
  ArrowUpRight,
  Edit2,
  Trash2,
  CheckCircle,
  X
} from 'lucide-react';
import { api } from '../api/client';
import { ExplainabilityCard } from '../components/ExplainabilityCard';
import { EditTransactionModal } from '../components/EditTransactionModal';
import { useLedgerUpdated } from '../utils/events';

export const TransactionsView: React.FC = () => {
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
    if (window.confirm("ఈ లావాదేవీని తొలగించాలనుకుంటున్నారా? బాకీ నిల్వ ఆటోమేటిక్ గా సరిచేయబడుతుంది.")) {
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
            మొత్తం లావాదేవీలు (All Transactions)
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '4px' }}>
            {transactions.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ఖాతా పుస్తకంలో నమోదైన అన్ని ఎంట్రీలు</div>
        </div>

        <div className="fin-card fin-card-green">
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            మొత్తం జమ / రావాలి (Total Inflow)
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--jama-green)', marginTop: '4px' }}>
            +₹{totalReceivables.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--jama-green-text)' }}>కస్టమర్ల నుండి రావలసిన మొత్తం</div>
        </div>

        <div className="fin-card fin-card-red">
          <div style={{ fontSize: '0.75rem', color: 'var(--udhaar-red-text)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            మొత్తం ఉధార్ / ఇవ్వాలి (Total Outflow)
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--udhaar-red)', marginTop: '4px' }}>
            -₹{totalPayables.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--udhaar-red-text)' }}>సప్లయర్లకు చెల్లించాల్సిన మొత్తం</div>
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
            placeholder="కస్టమర్, సప్లయర్ లేదా మాట్లాడిన మాటలతో వెతకండి (Search transactions)..."
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
            అన్నీ (All Entries)
          </button>
          <button
            onClick={() => setSelectedDirection('receivable')}
            className={`btn ${selectedDirection === 'receivable' ? 'btn-emerald' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            🟢 రావాలి (Inflow)
          </button>
          <button
            onClick={() => setSelectedDirection('payable')}
            className={`btn ${selectedDirection === 'payable' ? 'btn-danger' : 'btn-secondary'}`}
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            🔴 ఇవ్వాలి (Outflow)
          </button>
        </div>
      </div>

      {/* Transactions Ledger Table Card */}
      <div className="fin-card" style={{ padding: '0', overflow: 'hidden' }}>
        {filtered.length === 0 ? (
          <div style={{ padding: '48px 16px', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.92rem' }}>
            <div style={{ fontSize: '2rem', marginBottom: '8px' }}>📒</div>
            <div style={{ fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
              ఇంకా ఏ లావాదేవీలు నమోదు కాలేదు (No Transactions Found)
            </div>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              వాయిస్ లేదా చాట్ లో లావాదేవీ చెప్పగానే ఎంట్రీలు ఇక్కడ ఆటోమేటిక్ గా కనిపిస్తాయి.
            </span>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="fin-table">
              <thead>
                <tr>
                  <th style={{ minWidth: '105px' }}>తేదీ (Date)</th>
                  <th style={{ minWidth: '160px' }}>వ్యక్తి / వ్యాపారం (Party)</th>
                  <th style={{ minWidth: '120px' }}>రకం (Type)</th>
                  <th style={{ minWidth: '130px' }}>దిశ (Direction)</th>
                  <th style={{ minWidth: '120px', textAlign: 'right' }}>మొత్తం (Amount ₹)</th>
                  <th style={{ minWidth: '120px', textAlign: 'right' }}>నిల్వ (Balance)</th>
                  <th style={{ minWidth: '110px' }}>విధానం (Method)</th>
                  <th style={{ minWidth: '100px' }}>ఆడిట్ (Audit)</th>
                  <th style={{ minWidth: '95px', textAlign: 'center' }}>చర్యలు (Action)</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((tx) => {
                  const isReceivable = tx.direction === 'receivable';
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
                        <span className={`badge ${isReceivable ? 'badge-jama' : 'badge-udhaar'}`} style={{ fontSize: '0.74rem' }}>
                          {isReceivable ? <ArrowDownLeft size={13} /> : <ArrowUpRight size={13} />}
                          {isReceivable ? 'రావాలి (Jama)' : 'ఇవ్వాలి (Udhaar)'}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 800, fontSize: '0.98rem', color: isReceivable ? 'var(--receivable-color)' : 'var(--payable-color)' }}>
                        {isReceivable ? '+' : '-'}₹{Number(tx.amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
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
                            <Edit2 size={12} /> సవరించు (Edit)
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
                            <Trash2 size={12} /> తొలగించు
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
