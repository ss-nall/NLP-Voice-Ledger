import React from 'react';
import {
  LayoutDashboard,
  Mic,
  Clock,
  ReceiptText,
  Scale,
  Settings,
  BookOpen,
  ArrowDownLeft,
  ArrowUpRight,
  TrendingDown,
  TrendingUp,
  CheckCircle2,
  Wallet
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface SidebarProps {
  currentView: string;
  onSelectView: (view: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onSelectView }) => {
  const { t, language } = useLanguage();

  const navItems = [
    { id: 'dashboard', label: t('nav.dashboard', 'Home Overview'), icon: LayoutDashboard },
    { id: 'conversation', label: t('nav.conversation', 'Voice & Text'), icon: Mic, badge: t('nav.badge.primary', 'Core') },
    { id: 'reminders', label: t('nav.reminders', 'Reminders & WhatsApp'), icon: Clock, badge: 'WhatsApp' },
    { id: 'customers', label: t('nav.receivables', 'Receivables'), icon: ArrowDownLeft, color: 'var(--jama-green)' },
    { id: 'suppliers', label: t('nav.payables', 'Payables'), icon: ArrowUpRight, color: 'var(--udhaar-red)' },
    { id: 'received', label: t('nav.received', 'Received Inflows'), icon: TrendingUp, color: '#0284C7' },
    { id: 'paid', label: t('nav.paid', 'Paid Outflows'), icon: TrendingDown, color: '#D97706' },
    { id: 'transactions', label: t('nav.transactions', 'All Journal'), icon: ReceiptText },
    { id: 'health', label: t('nav.health', 'Trial Balance'), icon: Scale },
    { id: 'settings', label: t('nav.settings', 'Settings'), icon: Settings },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ padding: '20px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '12px', background: 'var(--bg-card)' }}>
        <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: 'var(--maroon)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF', boxShadow: '0 2px 8px rgba(153, 27, 27, 0.3)' }}>
          <BookOpen size={22} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--maroon)', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
            {t('app.name', 'NLP Ledger')}
          </h1>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>{t('app.subtitle', 'Multilingual Khata')}</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '16px 10px', flex: 1, overflowY: 'auto' }}>
        <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', padding: '0 12px 10px', letterSpacing: '0.06em' }}>
          {t('nav.menu', 'Main Menu')}
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 14px',
                borderRadius: 'var(--radius-md)',
                background: isActive ? 'var(--receivable-light)' : 'transparent',
                border: 'none',
                borderLeft: isActive ? '4px solid var(--jama-green)' : '4px solid transparent',
                color: isActive ? 'var(--jama-green-dark)' : 'var(--text-main)',
                fontSize: '0.92rem',
                fontWeight: isActive ? 700 : 500,
                cursor: 'pointer',
                textAlign: 'left',
                marginBottom: '4px',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = 'var(--bg-card-subtle)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = 'transparent';
              }}
            >
              <Icon size={19} color={item.color || (isActive ? 'var(--receivable-color)' : 'var(--text-dim)')} />
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.badge && (
                <span className="badge badge-gold" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer System Status & Ledger Invariant Badge */}
      <div style={{ padding: '14px 16px', borderTop: '1px solid var(--border-color)', background: 'var(--bg-card-subtle)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <CheckCircle2 size={15} color="var(--jama-green)" />
          <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-main)' }}>
            {t('header.trial_balance', 'Double-Entry Balanced')}
          </span>
        </div>
        <p style={{ fontSize: '0.7rem', color: 'var(--text-dim)', margin: 0 }}>
          Deterministic NLP • 4 Languages
        </p>
      </div>
    </aside>
  );
};
