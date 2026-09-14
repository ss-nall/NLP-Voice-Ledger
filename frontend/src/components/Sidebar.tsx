import {
  LayoutDashboard,
  Mic,
  Users,
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

interface SidebarProps {
  currentView: string;
  onSelectView: (view: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onSelectView }) => {
  const navItems = [
    { id: 'dashboard', label: 'హోమ్ (Home Overview)', icon: LayoutDashboard },
    { id: 'conversation', label: 'వాయిస్ లెక్కలు (Voice & Text)', icon: Mic, badge: 'ముఖ్యం' },
    { id: 'reminders', label: 'రిమైండర్లు & WhatsApp', icon: Clock, badge: 'New' },
    { id: 'customers', label: 'రావాల్సినవి (Receivables)', icon: ArrowDownLeft, color: 'var(--jama-green)' },
    { id: 'suppliers', label: 'ఇవ్వాల్సినవి (Payables)', icon: ArrowUpRight, color: 'var(--udhaar-red)' },
    { id: 'received', label: 'వచ్చినవి (Received Inflows)', icon: TrendingUp, color: '#0284C7' },
    { id: 'paid', label: 'చెల్లించినవి (Paid Outflows)', icon: TrendingDown, color: '#D97706' },
    { id: 'transactions', label: 'అన్ని లావాదేవీలు (All Journal)', icon: ReceiptText },
    { id: 'health', label: 'ఖాతా ఆరోగ్యం (Trial Balance)', icon: Scale },
    { id: 'settings', label: 'సెట్టింగ్స్ (Settings)', icon: Settings },
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
            వ్యాపార ఖాతా
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Bilingual NLP Khata</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '16px 10px', flex: 1, overflowY: 'auto' }}>
        <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-dim)', padding: '0 12px 10px', letterSpacing: '0.06em' }}>
          ఖాతా మెనూ (Main Menu)
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
                <span className={`badge ${item.badge === 'ముఖ్యం' ? 'badge-jama' : 'badge-gold'}`} style={{ fontSize: '0.68rem', padding: '2px 6px' }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Quick Balance Footer */}
      <div style={{ padding: '16px', borderTop: '1px solid var(--border-color)', background: 'var(--bg-card-subtle)' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase' }}>
          దుకాణం లెక్కలు (Shop Ledger)
        </div>
        <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '2px' }}>
          నా వ్యాపార ఖాతా బుక్
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--receivable-color)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px', marginTop: '3px' }}>
          <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--receivable-color)' }}></span>
          ఆటోమేటిక్ డబుల్ ఎంట్రీ లైవ్
        </div>
      </div>
    </aside>
  );
};
