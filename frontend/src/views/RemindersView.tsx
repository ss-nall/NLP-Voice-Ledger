import React, { useState, useEffect } from 'react';
import { Clock, MessageCircle, AlertTriangle, Calendar, CheckCircle2, User, RefreshCw, Send } from 'lucide-react';
import { api } from '../api/client';
import { useLedgerUpdated } from '../utils/events';

export const RemindersView: React.FC = () => {
  const [reminders, setReminders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('ALL');

  useEffect(() => {
    loadReminders();
  }, []);

  useLedgerUpdated(() => {
    loadReminders();
  });

  const loadReminders = async () => {
    try {
      setLoading(true);
      const data = await api.getReminders();
      setReminders(data);
    } catch (err) {
      console.error('Failed to load reminders', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredReminders = reminders.filter((r) => {
    if (filter === 'OVERDUE') return r.urgency === 'OVERDUE';
    if (filter === 'TODAY') return r.urgency === 'TODAY' || r.urgency === 'TOMORROW';
    if (filter === 'UPCOMING') return r.urgency === 'UPCOMING';
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Banner */}
      <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Clock size={24} color="#D97706" />
            చెల్లింపుల రిమైండర్లు (Due Date Reminders & WhatsApp)
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>
            గడువు తేదీలతో ఉన్న బాకీల వివరాలు మరియు ఒక్క క్లిక్‌తో వాట్సాప్ రిమైండర్ సందేశాలు
          </p>
        </div>
        <button onClick={loadReminders} className="btn-outline">
          <RefreshCw size={16} /> రిఫ్రెష్ (Refresh)
        </button>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {[
          { id: 'ALL', label: `అన్నీ (All - ${reminders.length})` },
          { id: 'OVERDUE', label: `గడువు దాటినవి (Overdue - ${reminders.filter(r => r.urgency === 'OVERDUE').length})`, color: 'var(--udhaar-red)' },
          { id: 'TODAY', label: `ఈరోజు / రేపు (Today/Tomorrow - ${reminders.filter(r => r.urgency === 'TODAY' || r.urgency === 'TOMORROW').length})`, color: '#D97706' },
          { id: 'UPCOMING', label: `రాబోయేవి (Upcoming - ${reminders.filter(r => r.urgency === 'UPCOMING').length})`, color: 'var(--jama-green)' },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setFilter(t.id)}
            style={{
              padding: '8px 16px',
              borderRadius: 'var(--radius-full)',
              border: filter === t.id ? '2px solid var(--border-focus)' : '1px solid var(--border-color)',
              background: filter === t.id ? 'var(--receivable-light)' : 'var(--bg-card)',
              color: filter === t.id ? 'var(--jama-green-dark)' : 'var(--text-main)',
              fontWeight: filter === t.id ? 700 : 500,
              fontSize: '0.88rem',
              cursor: 'pointer'
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Reminders Cards List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          రిమైండర్లు లోడ్ అవుతున్నాయి...
        </div>
      ) : filteredReminders.length === 0 ? (
        <div style={{ background: 'var(--bg-card)', padding: '40px', borderRadius: 'var(--radius-lg)', textAlign: 'center', border: '1px dashed var(--border-strong)' }}>
          <CheckCircle2 size={40} color="#059669" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>ప్రస్తుతం ఎలాంటి పెండింగ్ రిమైండర్లు లేవు</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '4px' }}>
            "సెప్టెంబర్ 17 కి పవన్ కి 15,000 ఇవ్వాలి" వంటి వాయిస్ లేదా టెక్స్ట్ నమోదు చేసినప్పుడు రిమైండర్ ఆటోమేటిక్‌గా ఇక్కడ కనిపిస్తుంది.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '16px' }}>
          {filteredReminders.map((rem) => {
            const isOverdue = rem.urgency === 'OVERDUE';
            const isToday = rem.urgency === 'TODAY' || rem.urgency === 'TOMORROW';
            const isReceivable = rem.entity_type === 'customer';

            return (
              <div
                key={rem.id}
                className="fin-card"
                style={{
                  borderLeft: `5px solid ${isOverdue ? '#DC2626' : (isToday ? '#D97706' : '#059669')}`,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '14px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <User size={18} color="#64748B" />
                      {rem.entity_name}
                    </div>
                    <span style={{ fontSize: '0.75rem', color: isReceivable ? '#059669' : '#DC2626', fontWeight: 600 }}>
                      {isReceivable ? '↓ కస్టమర్ నుండి రావాలి (Receivable)' : '↑ సప్లయర్ కి ఇవ్వాలి (Payable)'}
                    </span>
                  </div>
                  <span className={`badge ${isOverdue ? 'badge-udhaar' : (isToday ? 'badge-gold' : 'badge-jama')}`}>
                    {rem.badge_te}
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', background: 'var(--bg-card-subtle)', padding: '12px 14px', borderRadius: 'var(--radius-md)' }}>
                  <div>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'block' }}>మొత్తం (Amount)</span>
                    <span style={{ fontSize: '1.45rem', fontWeight: 800, color: isReceivable ? 'var(--receivable-color)' : 'var(--payable-color)' }}>
                      ₹{rem.amount?.toLocaleString()}
                    </span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'block' }}>గడువు తేదీ (Due Date)</span>
                    <span style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      {rem.formatted_date_te || rem.due_date}
                    </span>
                  </div>
                </div>

                {rem.source_text && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', background: 'var(--bg-card-subtle)', padding: '6px 10px', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                    "{rem.source_text}"
                  </div>
                )}

                {/* WhatsApp Action Button */}
                <div style={{ marginTop: 'auto', paddingTop: '8px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                    {rem.badge_en}
                  </span>
                  <a
                    href={rem.whatsapp_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-whatsapp"
                  >
                    <MessageCircle size={16} />
                    WhatsApp రిమైండర్ పంపండి
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
