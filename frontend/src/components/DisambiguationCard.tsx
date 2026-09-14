import React from 'react';
import { HelpCircle, UserPlus, CheckCircle2, X, ArrowRight, UserCheck } from 'lucide-react';

export interface DisambiguationCardProps {
  data: {
    extracted_actor?: string;
    resolved?: boolean;
    cancelled?: boolean;
    resolvedText?: string;
    suggested_matches?: Array<{
      id: number;
      name: string;
      similarity?: number;
      outstanding_balance?: number;
    }>;
    proposed_event?: {
      actor?: string;
      amount?: number;
      event_type?: string;
      direction?: string;
    };
  };
  onSelectExisting: (entityId: number, entityName: string) => void;
  onCreateNew: () => void;
  onCancel: () => void;
  isProcessing?: boolean;
}

export const DisambiguationCard: React.FC<DisambiguationCardProps> = ({
  data,
  onSelectExisting,
  onCreateNew,
  onCancel,
  isProcessing = false
}) => {
  const spokenName = data.extracted_actor || data.proposed_event?.actor || 'పేరు';
  const amount = Number(data.proposed_event?.amount || 0);

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
            ? 'ఈ ఖాతా ఎంపిక రద్దు చేయబడింది (Selection Cancelled)'
            : (data.resolvedText || 'ఖాతా ఎంపిక పూర్తయింది (Account Linked & Resolved)')}
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
        border: '1.5px solid #0284C7',
        boxShadow: '0 4px 20px rgba(2, 132, 199, 0.12)',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        color: 'var(--text-main, #1e293b)'
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color, #e2e8f0)', paddingBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#0284C7', fontWeight: 700, fontSize: '0.92rem' }}>
          <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'rgba(2, 132, 199, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <HelpCircle size={17} color="#0284C7" />
          </div>
          <span>పోలిక ఉన్న ఖాతాను ఎంచుకోండి (Select Matching Account)</span>
        </div>
        <span
          style={{
            fontSize: '0.72rem',
            padding: '3px 8px',
            borderRadius: '20px',
            background: 'rgba(2, 132, 199, 0.15)',
            color: '#0369A1',
            fontWeight: 700
          }}
        >
          Similar Matches Found
        </span>
      </div>

      {/* Spoken Context Subtitle */}
      <div style={{ fontSize: '0.84rem', color: 'var(--text-muted, #64748b)' }}>
        మీరు చెప్పిన పేరు: <strong style={{ color: 'var(--text-main, #1e293b)', fontSize: '0.92rem' }}>"{spokenName}"</strong>
        {amount > 0 && <span> • మొత్తం: <strong style={{ color: '#0284C7' }}>₹{amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong></span>}
      </div>

      {/* Candidate List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {(data.suggested_matches || []).map((match) => (
          <button
            key={match.id}
            disabled={isProcessing}
            onClick={() => onSelectExisting(match.id, match.name)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 14px',
              background: 'var(--bg-card, #ffffff)',
              border: '1px solid var(--border-color, #cbd5e1)',
              borderRadius: '10px',
              textAlign: 'left',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#059669';
              e.currentTarget.style.background = 'rgba(16, 185, 129, 0.06)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-color, #cbd5e1)';
              e.currentTarget.style.background = 'var(--bg-card, #ffffff)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(2, 132, 199, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0284C7', fontWeight: 700, fontSize: '0.85rem' }}>
                {match.name.charAt(0)}
              </div>
              <div>
                <div style={{ fontWeight: 700, color: 'var(--text-main, #1e293b)', fontSize: '0.92rem' }}>
                  {match.name}
                </div>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted, #64748b)' }}>
                  ప్రస్తుత బాకీ (Balance): <strong style={{ color: '#059669' }}>₹{Number(match.outstanding_balance || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontSize: '0.72rem',
                  padding: '3px 8px',
                  borderRadius: '12px',
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#059669',
                  fontWeight: 700
                }}
              >
                {Math.round((match.similarity || 0.85) * 100)}% మ్యాచ్
              </span>
              <ArrowRight size={16} color="var(--text-muted, #94a3b8)" />
            </div>
          </button>
        ))}
      </div>

      {/* Action to Create New Entity */}
      <button
        disabled={isProcessing}
        onClick={onCreateNew}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
          padding: '11px 16px',
          borderRadius: '8px',
          background: 'var(--bg-card, #ffffff)',
          color: 'var(--text-main, #1e293b)',
          border: '1.5px dashed #0284C7',
          fontWeight: 600,
          fontSize: '0.84rem',
          cursor: 'pointer',
          transition: 'all 0.15s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(2, 132, 199, 0.06)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = 'var(--bg-card, #ffffff)';
        }}
      >
        <UserPlus size={16} color="#0284C7" />
        కాదు, కొత్త ఖాతా <strong style={{ color: '#0284C7' }}>"{spokenName}"</strong> గా సృష్టించు (Create New Profile)
      </button>

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
          cursor: 'pointer'
        }}
      >
        <X size={14} /> రద్దు చేయి (Cancel / Discard)
      </button>
    </div>
  );
};
