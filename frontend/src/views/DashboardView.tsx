import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Clock,
  Users,
  Scale,
  ArrowDownLeft,
  ArrowUpRight,
  MessageCircle,
  Mic,
  Calendar,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { api } from '../api/client';
import { useLedgerUpdated } from '../utils/events';

export const DashboardView: React.FC = () => {
  const [overview, setOverview] = useState<any>(null);
  const [recentTransactions, setRecentTransactions] = useState<any[]>([]);
  const [reminders, setReminders] = useState<any[]>([]);
  const [topDebtors, setTopDebtors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  useLedgerUpdated(() => {
    loadDashboardData();
  });

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [ov, txs, rems, debtors] = await Promise.all([
        api.getOverview(),
        api.getTransactions({ limit: '6' as any }),
        api.getReminders(),
        api.getTopDebtors(4)
      ]);
      setOverview(ov);
      setRecentTransactions(txs);
      setReminders(rems);
      setTopDebtors(debtors);
    } catch (err) {
      console.error('Failed to load dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !overview) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', color: 'var(--text-muted)' }}>
        లెక్కలు మరియు సారాంశం లోడ్ అవుతున్నాయి...
      </div>
    );
  }

  const urgentReminders = reminders.slice(0, 3);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Main KPI Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px' }}>
        
        {/* Total Receivables (Jama / You'll Get) */}
        <div className="fin-card fin-card-green" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#065F46', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                నాకు రావాల్సినవి (You'll Get / Receivables)
              </span>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#DCFCE7', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#059669' }}>
                <ArrowDownLeft size={20} />
              </div>
            </div>
            <div style={{ fontSize: '2.1rem', fontWeight: 800, color: '#059669', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              ₹{overview.total_receivables?.toLocaleString()}
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: '#047857', marginTop: '14px', fontWeight: 500 }}>
            👥 మొత్తం <strong>{overview.customer_count}</strong> కస్టమర్ల నుండి రావలసిన మొత్తం
          </div>
        </div>

        {/* Total Payables (Udhaar / You'll Give) */}
        <div className="fin-card fin-card-red" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#991B1B', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                నేను ఇవ్వాల్సినవి (You'll Give / Payables)
              </span>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#FEE2E2', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#DC2626' }}>
                <ArrowUpRight size={20} />
              </div>
            </div>
            <div style={{ fontSize: '2.1rem', fontWeight: 800, color: '#DC2626', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              ₹{overview.total_payables?.toLocaleString()}
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: '#B91C1C', marginTop: '14px', fontWeight: 500 }}>
            🚚 మొత్తం <strong>{overview.supplier_count}</strong> సప్లయర్లకు చెల్లించాల్సిన మొత్తం
          </div>
        </div>

        {/* Net Business Balance */}
        <div className="fin-card fin-card-gold" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#92400E', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                నికర వ్యాపార నిల్వ (Net Khata Balance)
              </span>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: '#FEF3C7', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#D97706' }}>
                <Scale size={20} />
              </div>
            </div>
            <div style={{ fontSize: '2.1rem', fontWeight: 800, color: overview.net_position >= 0 ? '#059669' : '#DC2626', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              ₹{overview.net_position?.toLocaleString()}
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: '#B45309', marginTop: '14px', fontWeight: 500 }}>
            {overview.net_position >= 0 ? '● సానుకూల వ్యాపార లాభం (In Profit)' : '● జాగ్రత్త: చెల్లింపులు అధికంగా ఉన్నాయి'}
          </div>
        </div>

      </div>

      {/* Active Due Date Reminders Ribbon */}
      {urgentReminders.length > 0 && (
        <div className="fin-card" style={{ border: '2px solid var(--amber-border, #FDE68A)', background: 'var(--bg-card)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--amber, #D97706)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={18} color="var(--amber, #D97706)" />
              తక్షణ గడువు రిమైండర్లు (Urgent Due Date Reminders)
            </h3>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', fontWeight: 600 }}>
              మొత్తం {reminders.length} రిమైండర్లు
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
            {urgentReminders.map((rem) => (
              <div key={rem.id} style={{ background: 'var(--bg-card-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.98rem', color: 'var(--text-main)' }}>{rem.entity_name}</span>
                  <span className={`badge ${rem.urgency === 'OVERDUE' ? 'badge-udhaar' : (rem.urgency === 'TODAY' || rem.urgency === 'TOMORROW' ? 'badge-gold' : 'badge-jama')}`}>
                    {rem.badge_te}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <span style={{ fontSize: '1.25rem', fontWeight: 800, color: rem.entity_type === 'customer' ? 'var(--receivable-color)' : 'var(--payable-color)' }}>
                    ₹{rem.amount?.toLocaleString()}
                  </span>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                    {rem.formatted_date_te || rem.due_date}
                  </span>
                </div>
                <a
                  href={rem.whatsapp_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-whatsapp"
                  style={{ justifyContent: 'center', marginTop: '4px', padding: '6px 12px' }}
                >
                  <MessageCircle size={15} /> WhatsApp సందేశం పంపండి
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid: Recent Transactions & Top Customers */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        
        {/* Recent Transactions Journal */}
        <div className="fin-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
              తాజా లావాదేవీలు (Recent Transactions)
            </h3>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>చివరి 6 లావాదేవీలు</span>
          </div>

          {recentTransactions.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', padding: '20px 0', textAlign: 'center' }}>ఇంకా లావాదేవీలు లేవు. మాట్లాడండి లేదా టైప్ చేసి నమోదు చేయండి.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {recentTransactions.map((tx) => {
                const isReceivable = tx.direction === 'receivable';
                return (
                  <div key={tx.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 14px', borderRadius: 'var(--radius-md)', background: 'var(--bg-card-subtle)', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: isReceivable ? 'var(--receivable-light)' : 'var(--payable-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: isReceivable ? 'var(--receivable-color)' : 'var(--payable-color)' }}>
                        {isReceivable ? <ArrowDownLeft size={18} /> : <ArrowUpRight size={18} />}
                      </div>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>{tx.counterparty_name}</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                          {tx.date} • {tx.transaction_type}
                        </div>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 800, fontSize: '1.15rem', color: isReceivable ? 'var(--receivable-color)' : 'var(--payable-color)' }}>
                        {isReceivable ? '+' : '-'}₹{tx.amount?.toLocaleString()}
                      </div>
                      <span className={`badge ${isReceivable ? 'badge-jama' : 'badge-udhaar'}`} style={{ fontSize: '0.68rem', padding: '2px 6px' }}>
                        {isReceivable ? 'రావాలి (Jama)' : 'ఇవ్వాలి (Udhaar)'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Top Debtors */}
        <div className="fin-card">
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '14px' }}>
            ఎక్కువ బాకీ ఉన్న కస్టమర్లు (Top Debtors)
          </h3>
          {topDebtors.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>ప్రస్తుతం ఎవరి వద్ద బాకీలు లేవు.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {topDebtors.map((d) => (
                <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', background: 'var(--bg-card-subtle)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>{d.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>క్రెడిట్ స్కోర్: {d.credit_score}</div>
                  </div>
                  <div style={{ fontWeight: 800, color: 'var(--receivable-color)', fontSize: '1rem' }}>
                    ₹{d.outstanding_balance?.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
