import React, { useState } from 'react';
import {
  Sparkles,
  Layers,
  ArrowRight,
  Globe,
  Tag,
  Calendar,
  ShieldCheck,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Volume2
} from 'lucide-react';

interface PipelineVisualizerProps {
  diagnostics: any;
}

export const PipelineVisualizer: React.FC<PipelineVisualizerProps> = ({ diagnostics }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (!diagnostics) return null;

  const {
    raw_input,
    speech_data,
    language_info,
    code_switch_info,
    normalized_info,
    entities,
    temporal_info,
    relation_info,
    event,
    entity_resolution,
    consistency_info
  } = diagnostics;

  return (
    <div className="fin-card" style={{ marginBottom: '24px', border: '1px solid rgba(99, 102, 241, 0.3)', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.04), rgba(6, 182, 212, 0.03))' }}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', userSelect: 'none' }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={18} color="#818CF8" />
          <h4 style={{ fontSize: '1rem', color: '#818CF8' }}>Modular NLP Pipeline Inspector (Step-by-Step Trace)</h4>
          <span className="badge badge-indigo">Auditable Pipeline</span>
        </div>
        <button className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '0.75rem' }}>
          {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />} {isOpen ? 'Collapse' : 'Inspect'}
        </button>
      </div>

      {isOpen && (
        <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {/* Step 1: Speech & Language Identification */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
                1. Language Classification
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <Globe size={14} color="#06B6D4" />
                <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>{language_info?.primary_language}</span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Code-Mixed: <strong>{language_info?.is_code_mixed ? 'Yes' : 'No'}</strong> | CMI Score: <strong>{code_switch_info?.cmi_score}</strong>
              </div>
            </div>

            {/* Step 2: Spoken Numeral / Transliteration */}
            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
                2. Spoken Numeral & Phonetic Normalizer
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                "{normalized_info?.normalized_text}"
              </div>
              {speech_data?.spoken_amounts?.length > 0 && (
                <div style={{ fontSize: '0.75rem', color: '#10B981' }}>
                  Decoded Spoken Numeral: <strong>₹{speech_data.spoken_amounts[0].parsed_amount}</strong>
                </div>
              )}
            </div>

            {/* Step 3: Direction & Relation */}
            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
                3. Directional Relation Extractor
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                <span className={`badge ${relation_info?.direction === 'receivable' ? 'badge-emerald' : 'badge-rose'}`}>
                  {relation_info?.direction?.toUpperCase()}
                </span>
                <span style={{ fontSize: '0.82rem', fontWeight: 600 }}>{relation_info?.relation_type}</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                {relation_info?.explanation}
              </div>
            </div>
          </div>

          {/* Step 4: Extracted Entities, Temporal Dates & Consistency Engine */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '6px' }}>
                4. Financial NER Entities
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                <span className="badge badge-indigo">Actor: {event?.actor}</span>
                <span className="badge badge-emerald">Amount: ₹{event?.amount}</span>
                <span className="badge badge-cyan">Method: {event?.payment_method}</span>
                {event?.due_date && <span className="badge badge-amber">Due: {event?.due_date}</span>}
              </div>
            </div>

            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
                5. Consistency & Contradiction Guard
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                <ShieldCheck size={16} color={consistency_info?.is_consistent ? '#10B981' : '#F59E0B'} />
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: consistency_info?.is_consistent ? '#34D399' : '#FBBF24' }}>
                  {consistency_info?.is_consistent ? 'Ledger Verified (Consistent)' : 'Conflict Intercepted'}
                </span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                Confidence Score: <strong>{Math.round((event?.confidence || 0.9) * 100)}%</strong>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
