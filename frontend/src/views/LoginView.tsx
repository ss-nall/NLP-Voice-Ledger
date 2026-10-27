import React, { useState, useEffect } from 'react';
import {
  Globe,
  CheckCircle2,
  Sparkles,
  ShieldCheck,
  Mic,
  Key,
  BookOpen,
  ArrowRight,
  User,
  Sun,
  Moon
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { LanguageCode, SUPPORTED_LANGUAGES } from '../i18n/translations';

export const LoginView: React.FC = () => {
  const { language, setLanguage, t } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const {
    loginAsDemoGoogle,
    loginAsGuest,
    loginWithGoogleProfile,
    googleClientId,
    setGoogleClientId,
    isConfigModalOpen,
    setIsConfigModalOpen
  } = useAuth();

  const isLight = theme === 'light';
  const [tempClientId, setTempClientId] = useState(googleClientId);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // Initialize Google Identity Services if client ID is provided
  useEffect(() => {
    if (!googleClientId) return;

    // Load Google GIS Script dynamically
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      if ((window as any).google?.accounts?.id) {
        (window as any).google.accounts.id.initialize({
          client_id: googleClientId,
          callback: (response: any) => {
            handleGoogleCredentialResponse(response);
          }
        });
        const buttonDiv = document.getElementById('google-signin-btn-container');
        if (buttonDiv) {
          (window as any).google.accounts.id.renderButton(buttonDiv, {
            theme: isLight ? 'outline' : 'filled_blue',
            size: 'large',
            shape: 'pill',
            text: 'signin_with',
            width: 280
          });
        }
      }
    };
    document.body.appendChild(script);

    return () => {
      try {
        document.body.removeChild(script);
      } catch (e) {}
    };
  }, [googleClientId, language, isLight]);

  // Decode JWT credential from Google Identity Services
  const handleGoogleCredentialResponse = (response: any) => {
    try {
      setIsGoogleLoading(true);
      const token = response.credential;
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const data = JSON.parse(jsonPayload);
      loginWithGoogleProfile({
        name: data.name || data.given_name || 'Merchant',
        email: data.email || '',
        avatar: data.picture,
        language: language
      });
    } catch (err) {
      console.error('Google Sign-in decoding error:', err);
      loginAsDemoGoogle(language);
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleLanguageSelect = (code: LanguageCode) => {
    setLanguage(code);
  };

  const handleSaveClientId = (e: React.FormEvent) => {
    e.preventDefault();
    setGoogleClientId(tempClientId.trim());
    setIsConfigModalOpen(false);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        background: isLight
          ? 'linear-gradient(135deg, #F0FDF4 0%, #F8FAFC 45%, #EFF6FF 100%)'
          : 'linear-gradient(135deg, #0B1120 0%, #1E1B4B 50%, #0F172A 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '32px 16px',
        color: 'var(--text-main)',
        fontFamily: 'Inter, system-ui, sans-serif',
        position: 'relative',
        transition: 'background 0.3s ease, color 0.3s ease'
      }}
    >
      {/* Top Header Theme & Config Action Bar */}
      <div
        style={{
          position: 'absolute',
          top: '20px',
          right: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          zIndex: 10
        }}
      >
        <button
          onClick={toggleTheme}
          className="btn-theme-toggle"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 14px',
            borderRadius: 'var(--radius-full)',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-main)',
            fontSize: '0.82rem',
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: 'var(--shadow-sm)'
          }}
          title={`Switch to ${isLight ? 'Dark Mode' : 'Light Mode'}`}
        >
          {isLight ? <Moon size={15} color="#D97706" /> : <Sun size={15} color="#FBBF24" />}
          <span>{isLight ? 'Dark Mode' : 'Light Mode'}</span>
        </button>
      </div>

      {/* Subtle Background Glow Elements */}
      <div
        style={{
          position: 'fixed',
          top: '8%',
          left: '12%',
          width: '380px',
          height: '380px',
          borderRadius: '50%',
          background: isLight
            ? 'radial-gradient(circle, rgba(5, 150, 105, 0.08) 0%, rgba(255,255,255,0) 70%)'
            : 'radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none'
        }}
      />
      <div
        style={{
          position: 'fixed',
          bottom: '10%',
          right: '12%',
          width: '420px',
          height: '420px',
          borderRadius: '50%',
          background: isLight
            ? 'radial-gradient(circle, rgba(2, 132, 199, 0.08) 0%, rgba(255,255,255,0) 70%)'
            : 'radial-gradient(circle, rgba(217, 119, 6, 0.12) 0%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none'
        }}
      />

      {/* Brand Header */}
      <div style={{ textAlign: 'center', marginBottom: '28px', zIndex: 1 }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '68px',
            height: '68px',
            borderRadius: '20px',
            background: 'linear-gradient(135deg, var(--jama-green), #047857)',
            color: '#FFFFFF',
            boxShadow: isLight
              ? '0 10px 25px rgba(5, 150, 105, 0.25)'
              : '0 8px 24px rgba(5, 150, 105, 0.4)',
            marginBottom: '16px'
          }}
        >
          <BookOpen size={36} />
        </div>
        <h1
          style={{
            fontSize: '2.4rem',
            fontWeight: 800,
            letterSpacing: '-0.03em',
            color: 'var(--text-main)',
            marginBottom: '8px'
          }}
        >
          {t('app.name', 'NLP Ledger')}
        </h1>
        <p style={{ fontSize: '1.02rem', color: 'var(--text-muted)', maxWidth: '540px', lineHeight: 1.5, margin: '0 auto' }}>
          {t('login.welcome_subtitle', 'Record transactions in your mother tongue using voice or text. Real-time double-entry bookkeeping.')}
        </p>
      </div>

      {/* Main Glassmorphic Card Container */}
      <div
        style={{
          width: '100%',
          maxWidth: '840px',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '24px',
          boxShadow: isLight
            ? '0 20px 40px -10px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.04)'
            : '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          padding: '36px 32px',
          zIndex: 1,
          transition: 'all 0.2s ease'
        }}
      >
        {/* STEP 1: LANGUAGE PREFERENCE SELECTOR */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Globe size={20} color="var(--cyan)" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
                {t('login.step1_title', '1. Select Your Preferred Language')}
              </h2>
            </div>
            <span
              style={{
                fontSize: '0.78rem',
                background: 'var(--received-light)',
                color: 'var(--received-text)',
                border: '1px solid var(--received-border)',
                padding: '4px 10px',
                borderRadius: '12px',
                fontWeight: 700
              }}
            >
              8 Indian Languages Ready
            </span>
          </div>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
            {t('login.step1_desc', 'The entire application interface and voice intelligence will adapt to your choice.')}
          </p>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
              gap: '12px'
            }}
          >
            {SUPPORTED_LANGUAGES.map((item) => {
              const isSelected = language === item.code;
              return (
                <button
                  key={item.code}
                  onClick={() => handleLanguageSelect(item.code)}
                  style={{
                    padding: '16px 14px',
                    borderRadius: '16px',
                    background: isSelected
                      ? 'var(--receivable-light)'
                      : 'var(--bg-card-subtle)',
                    border: isSelected
                      ? '2px solid var(--jama-green)'
                      : '1px solid var(--border-color)',
                    boxShadow: isSelected
                      ? '0 4px 14px rgba(5, 150, 105, 0.18)'
                      : 'none',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.18s cubic-bezier(0.4, 0, 0.2, 1)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '6px',
                    position: 'relative'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.background = 'var(--bg-card-hover)';
                      e.currentTarget.style.borderColor = 'var(--border-strong)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.background = 'var(--bg-card-subtle)';
                      e.currentTarget.style.borderColor = 'var(--border-color)';
                    }
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '1.4rem' }}>{item.flag}</span>
                    {isSelected && <CheckCircle2 size={18} color="var(--jama-green)" />}
                  </div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: isSelected ? 'var(--jama-green-text)' : 'var(--text-main)' }}>
                    {item.nativeName}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {item.name} ({item.speechCode})
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* STEP 2: GOOGLE AUTH & DEMO ACCESS */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={20} color="var(--jama-green)" />
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)' }}>
                {t('login.step2_title', '2. Sign In to Your Ledger Account')}
              </h2>
            </div>
            <button
              onClick={() => setIsConfigModalOpen(true)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--cyan)',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
              title="Configure Google OAuth Client ID"
            >
              <Key size={13} />
              <span>{t('login.google_client_hint', 'Configure Google Client ID')}</span>
            </button>
          </div>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
            {t('login.step2_desc', 'Your business records are encrypted and synced across all your devices.')}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', alignItems: 'center' }}>
            {/* Real Google GIS Button Container if configured */}
            {googleClientId && (
              <div id="google-signin-btn-container" style={{ marginBottom: '6px' }} />
            )}

            {/* Instant Google Demo Profile Login */}
            <button
              onClick={() => loginAsDemoGoogle(language)}
              disabled={isGoogleLoading}
              style={{
                width: '100%',
                maxWidth: '420px',
                padding: '14px 20px',
                borderRadius: '14px',
                background: 'linear-gradient(135deg, #0284C7, #0369A1)',
                border: 'none',
                color: '#FFFFFF',
                fontSize: '0.96rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px',
                boxShadow: '0 4px 14px rgba(2, 132, 199, 0.35)',
                transition: 'all 0.18s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 20px rgba(2, 132, 199, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 14px rgba(2, 132, 199, 0.35)';
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24">
                <path
                  fill="#FFFFFF"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#FFFFFF"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FFFFFF"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#FFFFFF"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>{t('login.btn_google_demo', 'Instant Demo (Google Profile)')}</span>
              <ArrowRight size={16} />
            </button>

            {/* Quick Guest Access */}
            <button
              onClick={() => loginAsGuest(language)}
              style={{
                width: '100%',
                maxWidth: '420px',
                padding: '12px 20px',
                borderRadius: '14px',
                background: 'var(--bg-card-subtle)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-main)',
                fontSize: '0.9rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--bg-card-hover)';
                e.currentTarget.style.borderColor = 'var(--border-strong)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'var(--bg-card-subtle)';
                e.currentTarget.style.borderColor = 'var(--border-color)';
              }}
            >
              <User size={16} color="var(--text-dim)" />
              <span>{t('login.btn_guest', 'Continue as Guest Demo')}</span>
            </button>
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <div
          style={{
            marginTop: '32px',
            paddingTop: '24px',
            borderTop: '1px dashed var(--border-color)',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
            gap: '12px'
          }}
        >
          {[
            t('login.feature1', '🎙️ 8-Language Voice Recognition'),
            t('login.feature2', '⚖️ Double-Entry Accounting'),
            t('login.feature3', '💬 1-Click WhatsApp Reminders'),
            t('login.feature4', '🛡️ Contradiction Detection')
          ].map((feat, idx) => (
            <div
              key={idx}
              style={{
                padding: '10px 12px',
                background: 'var(--bg-card-subtle)',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                fontSize: '0.78rem',
                color: 'var(--text-muted)',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <span>{feat}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Google Client ID Modal */}
      {isConfigModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 999,
            padding: '16px'
          }}
        >
          <div
            style={{
              width: '100%',
              maxWidth: '480px',
              background: 'var(--bg-card)',
              borderRadius: '20px',
              border: '1px solid var(--border-color)',
              padding: '24px',
              color: 'var(--text-main)',
              boxShadow: 'var(--shadow-lg)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <Key size={20} color="var(--cyan)" />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Google OAuth Client ID</h3>
            </div>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginBottom: '16px', lineHeight: 1.4 }}>
              Enter your Google Cloud Web OAuth 2.0 Client ID (or set <code>VITE_GOOGLE_CLIENT_ID</code> in <code>.env</code>).
              If not set, you can still use the <strong>Instant Demo Profile</strong> button with full mock Google data!
            </p>

            <form onSubmit={handleSaveClientId}>
              <input
                type="text"
                value={tempClientId}
                onChange={(e) => setTempClientId(e.target.value)}
                placeholder="e.g., 123456789-abcdefg.apps.googleusercontent.com"
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: 'var(--bg-input)',
                  border: '1px solid var(--border-strong)',
                  color: 'var(--text-main)',
                  fontSize: '0.85rem',
                  marginBottom: '18px',
                  outline: 'none'
                }}
              />

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setIsConfigModalOpen(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  Save Client ID
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
