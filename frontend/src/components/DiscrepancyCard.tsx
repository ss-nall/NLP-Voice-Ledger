import React from 'react';
import { AlertTriangle, CheckCircle2, X, Check } from 'lucide-react';

export interface DiscrepancyCardProps {
  data: {
    current_balance?: number;
    discrepancy_type?: string;
    excess_amount?: number;
    severity?: string;
    resolved?: boolean;
    cancelled?: boolean;
    resolvedText?: string;
    proposed_event?: {
      actor?: string;
      amount?: number;
      event_type?: string;
      direction?: string;
    };
    alerts?: Array<{ type: string; message: string; severity: string }>;
  };
  onConfirm: (overrideAmount?: number, forceSettle?: boolean) => void;
  onCancel: () => void;
  isProcessing?: boolean;
}

export const DiscrepancyCard: React.FC<DiscrepancyCardProps> = ({
  data,
  onConfirm,
  onCancel,
  isProcessing = false
}) => {
  const currentBalance = Number(data.current_balance || 0);
  const proposedAmount = Number(data.proposed_event?.amount || 0);
  const actor = data.proposed_event?.actor || 'ఈ ఖాతా';
  const excess = Number(data.excess_amount || Math.max(0, proposedAmount - currentBalance));
  const isDuplicate = data.discrepancy_type === 'POTENTIAL_DUPLICATE_TRANSACTION';
  const isOverpayment = data.discrepancy_type === 'OVERPAYMENT_EXCEEDS_BALANCE' || (excess > 0 && proposedAmount > currentBalance && currentBalance > 0);

  if (data.resolved) {
    return (
      <div
        style={{
          marginTop: '12px',
          padding: '12px 16px',
          background: data.cancelled ? 'rgba(239, 68, 68, 0.08)' : 'rgba(16, 185, 129, 0.08)',
          borderRadius: '12px',
          border: `1px solid ${data.cancelled ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: data.cancelled ? '#DC2626' : '#059669',
          fontSize: '0.86rem',
          fontWeight: 600
        }}
      >
        {data.cancelled ? <X size={16} /> : <CheckCircle2 size={16} />}
        <span>
          {data.cancelled
            ? 'ఈ లావాదేవీ రద్దు చేయబడింది (Transaction Cancelled)'
            : (data.resolvedText || 'ఖాతా వ్యత్యాసం పరిష్కరించబడింది (Discrepancy Resolved)')}
        </span>
      </div>
    );
  }

  return (
    <div
      style={{
        marginTop: '14px',
        padding: '18px',
        background: 'var(--bg-card, #ffffff)',
        borderRadius: '14px',
        border: '1.5px solid #F59E0B',
        boxShadow: '0 4px 20px rgba(245, 158, 11, 0.12)',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        color: 'var(--text-main, #1e293b)'
      }}
    >
      {/* Header Banner */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color, #e2e8f0)', paddingBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#D97706', fontWeight: 700, fontSize: '0.92rem' }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <AlertTriangle size={17} color="#D97706" />
          </div>
          <span>
            {isDuplicate
              ? 'పునరావృత నమోదు తనిఖీ (Duplicate Check)'
              : isOverpayment
              ? 'అదనపు చెల్లింపు తనిఖీ (Excess Payment Check)'
              : 'ఖాతా వ్యత్యాసం సరిచూడండి (Ledger Balance Mismatch)'}
          </span>
        </div>
        <span
          style={{
            fontSize: '0.72rem',
            padding: '3px 8px',
            borderRadius: '20px',
            background: 'rgba(245, 158, 11, 0.15)',
            color: '#B45309',
            fontWeight: 700,
            textTransform: 'uppercase'
          }}
        >
          {data.severity || 'Action Required'}
        </span>
      </div>

      {/* Side-by-side Financial Comparison Grid */}
      {!isDuplicate ? (
        <div style={{ display: 'grid', gridTemplateColumns: isOverpayment && excess > 0 ? '1fr 1fr 1fr' : '1fr 1fr', gap: '10px' }}>
          {/* Box 1: Recorded Khata Balance */}
          <div
            style={{
              padding: '12px 14px',
              background: 'rgba(245, 158, 11, 0.06)',
              borderRadius: '10px',
              border: '1px solid rgba(245, 158, 11, 0.25)',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <span style={{ fontSize: '0.72rem', color: '#B45309', fontWeight: 700, textTransform: 'uppercase' }}>
              పుస్తకంలో బాకీ (Book Balance)
            </span>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#D97706', marginTop: '4px' }}>
              ₹{currentBalance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted, #64748b)', marginTop: '2px' }}>
              {actor} పాత లెక్క
            </span>
          </div>

          {/* Box 2: Spoken / Input Amount */}
          <div
            style={{
              padding: '12px 14px',
              background: 'rgba(2, 132, 199, 0.06)',
              borderRadius: '10px',
              border: '1px solid rgba(2, 132, 199, 0.25)',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <span style={{ fontSize: '0.72rem', color: '#0284C7', fontWeight: 700, textTransform: 'uppercase' }}>
              చెప్పిన మొత్తం (Spoken Value)
            </span>
            <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0284C7', marginTop: '4px' }}>
              ₹{proposedAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted, #64748b)', marginTop: '2px' }}>
              తాజా మాట
            </span>
          </div>

          {/* Box 3: Advance Difference (if overpayment) */}
          {isOverpayment && excess > 0 && (
            <div
              style={{
                padding: '12px 14px',
                background: 'rgba(16, 185, 129, 0.06)',
                borderRadius: '10px',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <span style={{ fontSize: '0.72rem', color: '#059669', fontWeight: 700, textTransform: 'uppercase' }}>
                అదనపు మొత్తం (Advance Credit)
              </span>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#059669', marginTop: '4px' }}>
                +₹{excess.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted, #64748b)', marginTop: '2px' }}>
                ఖాతాలో జమ అవుతుంది
              </span>
            </div>
          )}
        </div>
      ) : (
        /* Duplicate Alert Box */
        <div
          style={{
            padding: '12px 14px',
            background: 'rgba(245, 158, 11, 0.08)',
            borderRadius: '10px',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}
        >
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#D97706' }}>
            ₹{proposedAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted, #64748b)' }}>
            ఈ మొత్తం <strong style={{ color: 'var(--text-main, #1e293b)' }}>{actor}</strong> ఖాతాలో కాసేపటి క్రితం మాత్రమే నమోదు చేయబడింది.
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
        {isOverpayment ? (
          <>
            <button
              disabled={isProcessing}
              onClick={() => onConfirm(currentBalance, true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '11px 16px',
                borderRadius: '8px',
                background: '#059669',
                color: '#ffffff',
                border: 'none',
                fontWeight: 700,
                fontSize: '0.86rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <CheckCircle2 size={17} /> బాకీ ₹{currentBalance.toLocaleString()} క్లియర్ చేసి + ₹{excess.toLocaleString()} అడ్వాన్స్‌గా జమ చేయి
            </button>

            <button
              disabled={isProcessing}
              onClick={() => onConfirm(proposedAmount, false)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 16px',
                borderRadius: '8px',
                background: 'var(--bg-card, #ffffff)',
                color: 'var(--text-main, #1e293b)',
                border: '1px solid var(--border-color, #cbd5e1)',
                fontWeight: 600,
                fontSize: '0.84rem',
                cursor: 'pointer'
              }}
            >
              చెప్పిన మొత్తం ₹{proposedAmount.toLocaleString()} మాత్రమే రికార్డ్ చేయి (Record Full ₹{proposedAmount.toLocaleString()})
            </button>
          </>
        ) : isDuplicate ? (
          <>
            <button
              disabled={isProcessing}
              onClick={() => onConfirm(proposedAmount, false)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '11px 16px',
                borderRadius: '8px',
                background: '#0284C7',
                color: '#ffffff',
                border: 'none',
                fontWeight: 700,
                fontSize: '0.86rem',
                cursor: 'pointer'
              }}
            >
              <Check size={16} /> అవును, మళ్ళీ నమోదు చేయి (Yes, Record Again)
            </button>
          </>
        ) : (
          <>
            <button
              disabled={isProcessing}
              onClick={() => onConfirm(currentBalance, true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '11px 16px',
                borderRadius: '8px',
                background: '#059669',
                color: '#ffffff',
                border: 'none',
                fontWeight: 700,
                fontSize: '0.86rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <CheckCircle2 size={17} /> అవును, మొత్తం బాకీ ₹{currentBalance.toLocaleString()} క్లియర్ చేయి (Clear Full Balance)
            </button>

            {proposedAmount > 0 && proposedAmount !== currentBalance && (
              <button
                disabled={isProcessing}
                onClick={() => onConfirm(proposedAmount, false)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  background: 'var(--bg-card, #ffffff)',
                  color: 'var(--text-main, #1e293b)',
                  border: '1px solid var(--border-color, #cbd5e1)',
                  fontWeight: 600,
                  fontSize: '0.84rem',
                  cursor: 'pointer'
                }}
              >
                చెప్పిన ₹{proposedAmount.toLocaleString()} మాత్రమే రికార్డ్ చేయి (Record Spoken Only)
              </button>
            )}
          </>
        )}

        {/* Cancel Button */}
        <button
          disabled={isProcessing}
          onClick={onCancel}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            padding: '8px 14px',
            borderRadius: '8px',
            background: 'transparent',
            color: 'var(--text-muted, #64748b)',
            border: 'none',
            fontWeight: 500,
            fontSize: '0.8rem',
            cursor: 'pointer',
            marginTop: '2px'
          }}
        >
          <X size={14} /> రద్దు చేయి (Cancel / Discard)
        </button>
      </div>
    </div>
  );
};
