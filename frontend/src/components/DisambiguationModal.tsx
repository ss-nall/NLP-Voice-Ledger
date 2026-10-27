import React from 'react';
import { HelpCircle, X, CheckCircle2, UserPlus, XCircle } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface DisambiguationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectExisting: (entityId: number, entityName: string) => void;
  onCreateNew: () => void;
  data: any;
}

export const DisambiguationModal: React.FC<DisambiguationModalProps> = ({
  isOpen,
  onClose,
  onSelectExisting,
  onCreateNew,
  data
}) => {
  const { t } = useLanguage();
  if (!isOpen || !data) return null;

  const { extracted_actor, suggested_matches, proposed_event } = data;
  const matches = suggested_matches || [];
  const amount = Number(proposed_event?.amount || 0);

  return (
    <div className="modal-backdrop" style={{ zIndex: 1200 }}>
      <div className="modal-card" style={{ maxWidth: '500px', borderRadius: '16px', overflow: 'hidden' }}>
        
        {/* Header */}
        <div
          style={{
            padding: '16px 20px',
            background: 'rgba(2, 132, 199, 0.12)',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '10px',
                background: '#0284C7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                boxShadow: '0 2px 8px rgba(2, 132, 199, 0.3)'
              }}
            >
              <HelpCircle size={22} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                {t('modal.disambig_title')}
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
                {t('modal.disambig_desc')}
              </p>
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
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px' }}>
          
          {/* Spoken Candidate Box */}
          <div
            style={{
              padding: '12px 16px',
              background: 'var(--bg-card-subtle)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              marginBottom: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <div>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                {t('modal.disambig_spoken_name')}
              </span>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-main)', marginTop: '2px' }}>
                "{extracted_actor}"
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                {t('modal.disambig_amount')}
              </span>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--receivable-color)', marginTop: '2px' }}>
                ₹{amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
            </div>
          </div>

          <div style={{ fontSize: '0.84rem', color: 'var(--text-main)', fontWeight: 700, marginBottom: '10px' }}>
            {t('modal.disambig_select_prompt')}
          </div>

          {/* Suggested Existing Accounts */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
            {matches.map((m: any) => (
              <button
                key={m.id}
                onClick={() => onSelectExisting(m.id, m.name)}
                className="btn"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--jama-green)';
                  e.currentTarget.style.background = 'var(--receivable-light)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-color)';
                  e.currentTarget.style.background = 'var(--bg-card)';
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 800, fontSize: '0.96rem', color: 'var(--text-main)' }}>
                      {m.name}
                    </span>
                    <span className="badge badge-emerald" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>
                      {Math.round((m.similarity || 0.85) * 100)}% {t('modal.disambig_match')}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                    {t('modal.disambig_cur_bal')} <strong style={{ color: 'var(--jama-green)' }}>₹{Number(m.outstanding_balance || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
                  </div>
                </div>

                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '50%',
                    background: 'var(--receivable-light)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--jama-green)',
                    border: '1px solid var(--jama-green)'
                  }}
                >
                  <CheckCircle2 size={18} />
                </div>
              </button>
            ))}
          </div>

          {/* Create New Account & Cancel Option */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              onClick={onCreateNew}
              className="btn btn-secondary"
              style={{
                width: '100%',
                padding: '11px',
                fontSize: '0.85rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <UserPlus size={16} /> {t('modal.disambig_create_new', { name: extracted_actor })}
            </button>

            <button
              onClick={onClose}
              className="btn btn-danger-subtle"
              style={{
                width: '100%',
                padding: '9px',
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px'
              }}
            >
              <XCircle size={15} /> {t('modal.disambig_cancel')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
