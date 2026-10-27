import React, { createContext, useContext, useState, useEffect } from 'react';
import { LanguageCode } from '../i18n/translations';

export interface UserProfile {
  name: string;
  email: string;
  avatar?: string;
  language: LanguageCode;
  provider: 'google' | 'guest';
  businessName?: string;
}

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  loginWithGoogleProfile: (profile: Partial<UserProfile>) => void;
  loginAsDemoGoogle: (lang: LanguageCode) => void;
  loginAsGuest: (lang: LanguageCode) => void;
  logout: () => void;
  googleClientId: string;
  setGoogleClientId: (id: string) => void;
  isConfigModalOpen: boolean;
  setIsConfigModalOpen: (open: boolean) => void;
}

const STORAGE_USER_KEY = 'nlpledger_user_session_v1';
const STORAGE_CLIENT_ID_KEY = 'nlpledger_google_client_id';

const DEFAULT_GOOGLE_CLIENT_ID =
  (import.meta as any).env?.VITE_GOOGLE_CLIENT_ID || '';

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  loginWithGoogleProfile: () => {},
  loginAsDemoGoogle: () => {},
  loginAsGuest: () => {},
  logout: () => {},
  googleClientId: '',
  setGoogleClientId: () => {},
  isConfigModalOpen: false,
  setIsConfigModalOpen: () => {}
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_USER_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.warn("Failed to load user session:", e);
    }
    return null;
  });

  const [googleClientId, setGoogleClientIdState] = useState<string>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_CLIENT_ID_KEY);
      if (saved) return saved;
    } catch (e) {}
    return DEFAULT_GOOGLE_CLIENT_ID;
  });

  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);

  useEffect(() => {
    try {
      if (user) {
        localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
      } else {
        localStorage.removeItem(STORAGE_USER_KEY);
      }
    } catch (e) {}
  }, [user]);

  const setGoogleClientId = (id: string) => {
    setGoogleClientIdState(id);
    try {
      localStorage.setItem(STORAGE_CLIENT_ID_KEY, id);
    } catch (e) {}
  };

  const getLocalAvatar = (name: string, bg = '0284C7') => {
    const initial = (name.trim()[0] || 'M').toUpperCase();
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="#${bg}"/><text x="50%" y="54%" text-anchor="middle" dominant-baseline="middle" fill="#ffffff" font-size="44" font-family="sans-serif" font-weight="bold">${initial}</text></svg>`;
    return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
  };

  const loginWithGoogleProfile = (profile: Partial<UserProfile>) => {
    const name = profile.name || 'Merchant Owner';
    const newUser: UserProfile = {
      name,
      email: profile.email || 'merchant@gmail.com',
      avatar: profile.avatar || getLocalAvatar(name, '2563EB'),
      language: profile.language || 'en',
      provider: 'google',
      businessName: profile.businessName || 'Sri Lakshmi Kirana & General Stores'
    };
    setUser(newUser);
  };

  const loginAsDemoGoogle = (lang: LanguageCode) => {
    const namesByLang: Record<LanguageCode, string> = {
      en: 'Venkat Rao (Merchant)',
      te: 'వెంకట రావు (ఖాతాదారు)',
      ta: 'வெங்கட் ராவ் (வணிகர்)',
      hi: 'वेंकट राव (व्यापारी)',
      kn: 'ವೆಂಕಟ್ ರಾವ್ (ವ್ಯಾಪಾರಿ)',
      ml: 'വെങ്കട് റാവു (വ്യാപാരി)',
      ur: 'وینکٹ راؤ (تاجر)',
      gu: 'વેંકટ રાવ (વેપારી)'
    };
    const name = namesByLang[lang] || 'Venkat Rao';
    const newUser: UserProfile = {
      name,
      email: 'venkat.merchant@gmail.com',
      avatar: getLocalAvatar(name, '0284C7'),
      language: lang,
      provider: 'google',
      businessName: 'Sri Balaji Traders & Distributors'
    };
    setUser(newUser);
  };

  const loginAsGuest = (lang: LanguageCode) => {
    const name = 'Guest Merchant';
    const newUser: UserProfile = {
      name,
      email: 'guest@khata.local',
      avatar: getLocalAvatar(name, 'D97706'),
      language: lang,
      provider: 'guest',
      businessName: 'Demo Retail Store'
    };
    setUser(newUser);
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loginWithGoogleProfile,
        loginAsDemoGoogle,
        loginAsGuest,
        logout,
        googleClientId,
        setGoogleClientId,
        isConfigModalOpen,
        setIsConfigModalOpen
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
