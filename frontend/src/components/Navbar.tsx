import React from 'react';
import { Mic, ShieldCheck, Languages, Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface NavbarProps {
  currentView: string;
  isRecording?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, isRecording = false }) => {
  const { theme, toggleTheme } = useTheme();

  const getTitle = () => {
    switch (currentView) {
      case 'dashboard': return 'హోమ్ డ్యాష్‌బోర్డ్ (Home Overview)';
      case 'conversation': return 'వాయిస్ & టెక్స్ట్ నమోదు (Voice & Text Entry)';
      case 'reminders': return 'బాకీల రిమైండర్లు & వాట్సాప్ (Reminders & WhatsApp)';
      case 'customers': return 'రావాల్సినవి / కస్టమర్ల బాకీలు (Customer Receivables)';
      case 'suppliers': return 'ఇవ్వాల్సినవి / సప్లయర్ల బాకీలు (Supplier Payables)';
      case 'received': return 'వచ్చిన నగదు & వసూళ్లు (Received Collections)';
      case 'paid': return 'చెల్లించినవి & ఖర్చులు (Paid Outflows & Expenses)';
      case 'transactions': return 'లావాదేవీల చిట్టా (All Transactions)';
      case 'health': return 'డబుల్ ఎంట్రీ ఆడిట్ (Trial Balance Health)';
      case 'settings': return 'సెట్టింగ్స్ (Settings)';
      default: return 'వ్యాపార ఖాతా (NLP Ledger)';
    }
  };

  return (
    <header className="top-navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)' }}>
          {getTitle()}
        </h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        {isRecording && (
          <span className="badge badge-udhaar" style={{ animation: 'pulse 1s infinite', fontSize: '0.82rem', padding: '6px 12px' }}>
            <Mic size={14} /> వింటున్నాము... మాట్లాడండి (Listening)
          </span>
        )}

        {/* Double Entry Status Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--jama-green-bg)', padding: '6px 12px', borderRadius: 'var(--radius-full)', border: '1px solid var(--jama-green-border)', fontSize: '0.82rem', color: 'var(--jama-green-text)', fontWeight: 600 }}>
          <ShieldCheck size={16} color="var(--jama-green)" />
          <span>డబుల్ ఎంట్రీ: <strong>సమతుల్యం (Balanced)</strong></span>
        </div>

        {/* Theme Mode Switcher */}
        <button
          onClick={toggleTheme}
          className="btn-theme-toggle"
          title={`Switch to ${theme === 'light' ? 'Dark Mode' : 'Light Mode'}`}
        >
          {theme === 'light' ? (
            <>
              <Moon size={15} color="#D97706" />
              <span>🌙 చీకటి (Dark)</span>
            </>
          ) : (
            <>
              <Sun size={15} color="#FBBF24" />
              <span>☀️ వెలుగు (Light)</span>
            </>
          )}
        </button>

        {/* Language Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--bg-card-subtle)', padding: '6px 12px', borderRadius: 'var(--radius-full)', border: '1px solid var(--border-color)', fontSize: '0.82rem', color: 'var(--text-main)', fontWeight: 600 }}>
          <Languages size={15} color="var(--khata-gold)" />
          <span>తెలుగు / English</span>
        </div>
      </div>
    </header>
  );
};
