import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Clock,
  Scale,
  ArrowDownLeft,
  ArrowUpRight,
  MessageCircle
} from 'lucide-react';
import { api } from '../api/client';
import { useLedgerUpdated } from '../utils/events';
import { useLanguage } from '../context/LanguageContext';

export const DashboardView: React.FC = () => {
  const { t, language } = useLanguage();
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
        {t('dash.loading', 'Loading financial overview and double-entry accounts...')}
      </div>
    );
  }

  const urgentReminders = reminders.slice(0, 3);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Top Main KPI Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px' }}>
        
        {/* Total Receivables */}
        <div className="fin-card hover-lift" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', border: '1px solid var(--receivable-border)', background: 'var(--bg-card)' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--receivable-text)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {t('dash.total_receivable', 'Total Receivables (To Receive)')}
              </span>
              <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'var(--receivable-light)', border: '1px solid var(--receivable-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--receivable-color)' }}>
                <ArrowDownLeft size={20} />
              </div>
            </div>
            <div className="tabular-nums" style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--receivable-color)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              ₹{overview.total_receivables?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '14px', fontWeight: 500 }}>
            👥 <strong>{overview.customer_count}</strong> {t('dash.active_customers', 'Active Customers')} • {t('dash.cust_receivable_sub', 'Total outstanding amount across active customers')}
          </div>
        </div>

        {/* Total Payables */}
        <div className="fin-card hover-lift" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', border: '1px solid var(--payable-border)', background: 'var(--bg-card)' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--payable-text)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {t('dash.total_payable', 'Total Payables (To Pay)')}
              </span>
              <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'var(--payable-light)', border: '1px solid var(--payable-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--payable-color)' }}>
                <ArrowUpRight size={20} />
              </div>
            </div>
            <div className="tabular-nums" style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--payable-color)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              ₹{overview.total_payables?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '14px', fontWeight: 500 }}>
            🚚 <strong>{overview.supplier_count}</strong> {t('dash.active_suppliers', 'Active Suppliers')} • {t('dash.supp_payable_sub', 'Total amount due to active trade suppliers')}
          </div>
        </div>

        {/* Net Business Balance */}
        <div className="fin-card hover-lift" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-main)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {t('dash.net_position', 'Net Cash Flow Position')}
              </span>
              <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: overview.net_position >= 0 ? 'var(--receivable-light)' : 'var(--payable-light)', border: `1px solid ${overview.net_position >= 0 ? 'var(--receivable-border)' : 'var(--payable-border)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: overview.net_position >= 0 ? 'var(--receivable-color)' : 'var(--payable-color)' }}>
                <Scale size={20} />
              </div>
            </div>
            <div className="tabular-nums" style={{ fontSize: '2.2rem', fontWeight: 800, color: overview.net_position >= 0 ? 'var(--receivable-color)' : 'var(--payable-color)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              ₹{overview.net_position?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: overview.net_position >= 0 ? 'var(--receivable-text)' : 'var(--payable-text)', marginTop: '14px', fontWeight: 600 }}>
            {overview.net_position >= 0 ? `● ${t('dash.healthy', 'Healthy (Receivables > Payables)')}` : `● ${t('dash.unhealthy', 'Action Needed (Payables > Receivables)')}`}
          </div>
        </div>

      </div>

      {/* Active Due Date Reminders Ribbon */}
      {urgentReminders.length > 0 && (
        <div className="fin-card" style={{ border: '2px solid var(--amber-border, #FDE68A)', background: 'var(--bg-card)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--amber, #D97706)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
              <Clock size={18} color="var(--amber, #D97706)" />
              {t('dash.urgent_reminders', 'Urgent Due Date Reminders')}
            </h3>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', fontWeight: 600 }}>
              {t('dash.total_reminders_count', 'Total Reminders')}: {reminders.length}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
            {urgentReminders.map((rem) => (
              <div key={rem.id} style={{ background: 'var(--bg-card-subtle)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.98rem', color: 'var(--text-main)' }}>{rem.entity_name}</span>
                  <span className={`badge ${rem.urgency === 'OVERDUE' ? 'badge-udhaar' : (rem.urgency === 'TODAY' || rem.urgency === 'TOMORROW' ? 'badge-gold' : 'badge-jama')}`}>
                    {rem.urgency}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <span style={{ fontSize: '1.25rem', fontWeight: 800, color: rem.entity_type === 'customer' ? 'var(--receivable-color)' : 'var(--payable-color)' }}>
                    ₹{rem.amount?.toLocaleString()}
                  </span>
                  <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                    {rem.due_date}
                  </span>
                </div>
                <a
                  href={rem.whatsapp_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-whatsapp"
                  style={{ justifyContent: 'center', marginTop: '4px', padding: '6px 12px' }}
                >
                  <MessageCircle size={15} /> {t('dash.send_whatsapp', 'Send WhatsApp Reminder')}
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
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', margin: 0 }}>
              {t('dash.recent_tx', 'Recent Financial Activity')}
            </h3>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
              {overview.transaction_count || 0} {t('recv.tx_count', 'records')}
            </span>
          </div>

          {recentTransactions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '36px 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {t('dash.no_data', 'No entries yet. Speak or type your first transaction!')}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {recentTransactions.map((tx) => (
                <div
                  key={tx.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 14px',
                    background: 'var(--bg-card-subtle)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div
                      style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '50%',
                        background: tx.direction === 'receivable' ? 'var(--jama-green-bg)' : 'var(--udhaar-red-bg)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: tx.direction === 'receivable' ? 'var(--jama-green)' : 'var(--udhaar-red)'
                      }}
                    >
                      {tx.direction === 'receivable' ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-main)' }}>
                        {tx.entity_name || tx.actor_name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {tx.created_at ? new Date(tx.created_at).toLocaleDateString() : 'Today'} • {tx.payment_method || 'Cash'}
                      </div>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div
                      style={{
                        fontWeight: 800,
                        fontSize: '1.05rem',
                        color: tx.direction === 'receivable' ? 'var(--jama-green)' : 'var(--udhaar-red)'
                      }}
                    >
                      {tx.direction === 'receivable' ? '+' : '-'}₹{tx.amount?.toLocaleString()}
                    </div>
                    <span
                      className={`badge ${tx.direction === 'receivable' ? 'badge-jama' : 'badge-udhaar'}`}
                      style={{ fontSize: '0.65rem', padding: '1px 6px' }}
                    >
                      {tx.direction === 'receivable' ? t('term.receivable', 'Receivable') : t('term.payable', 'Payable')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Top Debtors Side Panel */}
        <div className="fin-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '16px', margin: 0 }}>
            {t('dash.top_debtors', 'Top Customer Receivables')}
          </h3>

          {topDebtors.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '36px 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {t('rec.no_customers', 'No customer accounts found.')}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {topDebtors.map((cust) => (
                <div
                  key={cust.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 14px',
                    background: 'var(--bg-card-subtle)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-main)' }}>
                      {cust.name}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {cust.phone || 'No phone'}
                    </div>
                  </div>
                  <div style={{ fontWeight: 800, fontSize: '1.05rem', color: 'var(--jama-green)' }}>
                    ₹{cust.outstanding_balance?.toLocaleString()}
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
