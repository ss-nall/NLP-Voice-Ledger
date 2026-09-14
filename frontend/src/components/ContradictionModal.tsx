import React from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle2, X, Scale, ArrowRight, XCircle } from 'lucide-react';

interface ContradictionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (overrideAmount?: number, forceSettle?: boolean) => void;
  data: any;
}

export const ContradictionModal: React.FC<ContradictionModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  data
}) => {
  if (!isOpen || !data) return null;

  const { proposed_event, current_balance, alerts, confirmation_prompt } = data;
  const actor = proposed_event?.actor || 'Customer';
  const spokenAmt = Number(proposed_event?.amount || 0);
  const curBal = Number(current_balance || 0);

  return (
    <div className="modal-backdrop" style={{ zIndex: 1200 }}>
      <div className="modal-card" style={{ maxWidth: '520px', borderRadius: '16px', overflow: 'hidden' }}>
        
        {/* Header */}
        <div
          style={{
            padding: '16px 20px',
            background: 'var(--amber-light, rgba(245, 158, 11, 0.12))',
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
                background: '#F59E0B',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                boxShadow: '0 2px 8px rgba(245, 158, 11, 0.3)'
              }}
            >
              <AlertTriangle size={22} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
                ఖాతా వ్యత్యాసం (Ledger Discrepancy)
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
                రికార్డైన బాకీకి మరియు చెప్పిన మొత్తానికి తేడా గుర్తించబడింది
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
          
          {/* Prompt Message */}
          <div
            style={{
              padding: '12px 16px',
              background: 'var(--bg-card-subtle)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              marginBottom: '16px',
              fontSize: '0.9rem',
              color: 'var(--text-main)',
              lineHeight: 1.5,
              fontWeight: 600
            }}
          >
            {confirmation_prompt || `${actor} ఖాతాలో ₹${curBal.toLocaleString()} బాకీ ఉంది. మీరు ₹${spokenAmt.toLocaleString()} చెప్పారు.`}
          </div>

          {/* Side-by-Side Comparison */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
            <div
              className="fin-card"
              style={{
                padding: '12px 14px',
                background: 'var(--bg-card-subtle)',
                borderLeft: '4px solid #F59E0B'
              }}
            >
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                పుస్తకంలో ఉన్న బాకీ (Current Khata)
              </span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#D97706', marginTop: '4px' }}>
                ₹{curBal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                {actor} పెండింగ్ నిల్వ
              </div>
            </div>

            <div
              className="fin-card"
              style={{
                padding: '12px 14px',
                background: 'var(--bg-card-subtle)',
                borderLeft: '4px solid #0284C7'
              }}
            >
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                మీరు చెప్పిన మొత్తం (Spoken)
              </span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0284C7', marginTop: '4px' }}>
                ₹{spokenAmt.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                వాయిస్ / టెక్స్ట్ ఎంట్రీ
              </div>
            </div>
          </div>

          {/* Action Resolution Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <button
              onClick={() => onConfirm(curBal, true)}
              className="btn btn-emerald"
              style={{
                width: '100%',
                padding: '12px 16px',
                fontSize: '0.88rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <CheckCircle2 size={18} />
              అవును, మొత్తం బాకీ ₹{curBal.toLocaleString()} క్లియర్ చేయి (Full Settle)
            </button>

            <button
              onClick={() => onConfirm(spokenAmt, false)}
              className="btn btn-secondary"
              style={{
                width: '100%',
                padding: '11px 16px',
                fontSize: '0.85rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              కాదు, చెప్పిన ₹{spokenAmt.toLocaleString()} మాత్రమే నమోదు చేయి (Record Spoken Only)
            </button>

            <button
              onClick={onClose}
              className="btn btn-danger-subtle"
              style={{
                width: '100%',
                padding: '9px 14px',
                fontSize: '0.82rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px'
              }}
            >
              <XCircle size={16} /> రద్దు చేయి & లావాదేవీని ఆపు (Cancel & Discard)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
