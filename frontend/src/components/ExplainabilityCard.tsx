import React from 'react';
import { Info, ShieldCheck } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface ExplainabilityCardProps {
  transaction: any;
  onClose?: () => void;
}

export const ExplainabilityCard: React.FC<ExplainabilityCardProps> = ({ transaction }) => {
  const { t } = useLanguage();
  if (!transaction) return null;

  return (
    <div className="fin-card" style={{ background: 'var(--bg-card)', border: '1px solid rgba(6, 182, 212, 0.3)', padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Info size={18} color="#38BDF8" />
          <h4 style={{ fontSize: '1rem', color: '#38BDF8', margin: 0 }}>{t('card.explain_title')}</h4>
        </div>
        <span className="badge badge-emerald">
          {t('card.explain_confidence')}: {Math.round((transaction.confidence || 0.95) * 100)}%
        </span>
      </div>

      <div style={{ marginBottom: '14px', background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
          {t('card.explain_source')}
        </div>
        <div style={{ fontSize: '0.92rem', fontStyle: 'italic', color: 'var(--text-main)' }}>
          "{transaction.source_text || t('card.explain_manual')}"
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '10px', marginBottom: '14px' }}>
        <div style={{ background: 'var(--bg-card-subtle)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{t('card.explain_actor')}</div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>{transaction.counterparty_name}</div>
        </div>

        <div style={{ background: 'var(--bg-card-subtle)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{t('card.explain_amount')}</div>
          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#34D399' }}>₹{Number(transaction.amount).toLocaleString('en-IN')}</div>
        </div>

        <div style={{ background: 'var(--bg-card-subtle)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{t('card.explain_direction')}</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: transaction.direction === 'receivable' ? '#34D399' : '#F87171' }}>
            {transaction.direction === 'receivable' ? t('tx.dir_receivable') : t('tx.dir_payable')}
          </div>
        </div>

        <div style={{ background: 'var(--bg-card-subtle)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{t('card.explain_type')}</div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#38BDF8' }}>{transaction.transaction_type}</div>
        </div>
      </div>

      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <ShieldCheck size={14} color="#10B981" />
        {t('card.explain_audit')} <strong style={{ color: 'var(--text-main)' }}>₹{Number(transaction.balance_after || 0).toLocaleString('en-IN')}</strong>
      </div>
    </div>
  );
};
