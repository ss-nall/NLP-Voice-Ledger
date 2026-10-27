import React, { useState, useRef, useEffect } from 'react';
import { Mic, ShieldCheck, Languages, Sun, Moon, LogOut, Check, ChevronDown, Wifi, WifiOff } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { LanguageCode } from '../i18n/translations';

interface NavbarProps {
  currentView: string;
  isRecording?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, isRecording = false }) => {
  const { theme, toggleTheme } = useTheme();
  const { language, setLanguage, t, supportedLanguages, languageMeta } = useLanguage();
  const { user, logout } = useAuth();
  const [isLangDropdownOpen, setIsLangDropdownOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(typeof navigator !== 'undefined' ? navigator.onLine : true);
  const langDropdownRef = useRef<HTMLDivElement>(null);

  // Listen to network online/offline events
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (langDropdownRef.current && !langDropdownRef.current.contains(e.target as Node)) {
        setIsLangDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getTitle = () => {
    switch (currentView) {
      case 'dashboard': return t('nav.dashboard', 'Home Overview');
      case 'conversation': return t('nav.conversation', 'Voice & Text Entry');
      case 'reminders': return t('nav.reminders', 'Reminders & WhatsApp');
      case 'customers': return t('nav.receivables', 'Customer Receivables');
      case 'suppliers': return t('nav.payables', 'Supplier Payables');
      case 'received': return t('nav.received', 'Received Collections');
      case 'paid': return t('nav.paid', 'Paid Outflows');
      case 'transactions': return t('nav.transactions', 'All Journal Entries');
      case 'health': return t('nav.health', 'Trial Balance Health');
      case 'settings': return t('nav.settings', 'Settings & Profile');
      default: return t('app.name', 'NLP Ledger');
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
            <Mic size={14} /> {t('header.listening', 'Listening... Speak now')}
          </span>
        )}

        {/* Double Entry Status Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--jama-green-bg)', padding: '6px 12px', borderRadius: 'var(--radius-full)', border: '1px solid var(--jama-green-border)', fontSize: '0.82rem', color: 'var(--jama-green-text)', fontWeight: 600 }}>
          <ShieldCheck size={16} color="var(--jama-green)" />
          <span>{t('header.trial_balance', 'Double Entry: Balanced')}</span>
        </div>

        {/* Offline / Online Network Indicator */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
            background: isOnline ? 'rgba(16, 185, 129, 0.1)' : 'rgba(234, 88, 12, 0.15)',
            border: isOnline ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(234, 88, 12, 0.4)',
            padding: '5px 10px',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.78rem',
            color: isOnline ? 'var(--jama-green)' : '#EA580C',
            fontWeight: 700
          }}
          title={isOnline ? "Connected to Network" : "Running in 100% Offline Mode (Local NLP & Accounting Active)"}
        >
          {isOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
          <span>{isOnline ? 'Online' : 'Offline Mode (Local NLP Active)'}</span>
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
              <span>{t('header.theme.dark', 'Dark Mode')}</span>
            </>
          ) : (
            <>
              <Sun size={15} color="#FBBF24" />
              <span>{t('header.theme.light', 'Light Mode')}</span>
            </>
          )}
        </button>

        {/* Interactive Language Selector Dropdown */}
        <div ref={langDropdownRef} style={{ position: 'relative' }}>
          <button
            onClick={() => setIsLangDropdownOpen(!isLangDropdownOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'var(--bg-card-subtle)',
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              border: '1px solid var(--cyan)',
              fontSize: '0.82rem',
              color: 'var(--text-main)',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <Languages size={15} color="var(--cyan)" />
            <span>{languageMeta.flag} {languageMeta.nativeName}</span>
            <ChevronDown size={14} />
          </button>

          {isLangDropdownOpen && (
            <div
              style={{
                position: 'absolute',
                top: 'calc(100% + 6px)',
                right: 0,
                width: '180px',
                background: 'var(--bg-card)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
                padding: '6px',
                zIndex: 100,
                display: 'flex',
                flexDirection: 'column',
                gap: '2px'
              }}
            >
              {supportedLanguages.map((item) => {
                const isSelected = language === item.code;
                return (
                  <button
                    key={item.code}
                    onClick={() => {
                      setLanguage(item.code);
                      setIsLangDropdownOpen(false);
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '8px 10px',
                      borderRadius: 'var(--radius-sm)',
                      background: isSelected ? 'var(--receivable-light)' : 'transparent',
                      border: 'none',
                      color: isSelected ? 'var(--jama-green-dark)' : 'var(--text-main)',
                      fontWeight: isSelected ? 700 : 500,
                      fontSize: '0.85rem',
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    <span>{item.flag} {item.nativeName} ({item.name})</span>
                    {isSelected && <Check size={14} color="var(--jama-green)" />}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* User Profile Chip & Logout */}
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingLeft: '4px', borderLeft: '1px solid var(--border-color)' }}>
            <img
              src={user.avatar}
              alt={user.name}
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                border: '2px solid var(--cyan)',
                objectFit: 'cover'
              }}
            />
            <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.1 }}>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)' }}>
                {user.name.split(' ')[0]}
              </span>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                {user.provider === 'google' ? 'Google' : 'Demo'}
              </span>
            </div>
            <button
              onClick={logout}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-dim)',
                cursor: 'pointer',
                padding: '4px',
                display: 'flex',
                alignItems: 'center',
                borderRadius: '4px'
              }}
              title={t('header.logout', 'Sign Out')}
            >
              <LogOut size={16} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
