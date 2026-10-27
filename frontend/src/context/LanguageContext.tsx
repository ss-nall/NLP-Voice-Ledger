import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  LanguageCode,
  LanguageMeta,
  SUPPORTED_LANGUAGES,
  TRANSLATIONS
} from '../i18n/translations';

interface LanguageContextType {
  language: LanguageCode;
  setLanguage: (lang: LanguageCode) => void;
  t: (key: string, paramsOrFallback?: Record<string, any> | string, fallback?: string) => string;
  speechCode: 'en-IN' | 'te-IN' | 'ta-IN' | 'hi-IN' | 'kn-IN' | 'ml-IN' | 'ur-IN' | 'gu-IN';
  languageMeta: LanguageMeta;
  meta: LanguageMeta;
  supportedLanguages: LanguageMeta[];
}

const STORAGE_KEY = 'nlpledger_app_language';

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key, fallback) => (typeof fallback === 'string' ? fallback : key),
  speechCode: 'en-IN',
  languageMeta: SUPPORTED_LANGUAGES[0],
  meta: SUPPORTED_LANGUAGES[0],
  supportedLanguages: SUPPORTED_LANGUAGES
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<LanguageCode>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY) as LanguageCode;
      if (saved && SUPPORTED_LANGUAGES.some(l => l.code === saved)) {
        return saved;
      }
    } catch (e) {
      console.warn("Error reading language preference:", e);
    }
    return 'en';
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, language);
      document.documentElement.setAttribute('lang', language);
    } catch (e) {
      console.warn("Error saving language preference:", e);
    }
  }, [language]);

  const setLanguage = (lang: LanguageCode) => {
    setLanguageState(lang);
  };

  const currentMeta =
    SUPPORTED_LANGUAGES.find((m) => m.code === language) || SUPPORTED_LANGUAGES[0];

  const t = (
    key: string,
    paramsOrFallback?: Record<string, any> | string,
    fallback?: string
  ): string => {
    const langDict = TRANSLATIONS[language] || TRANSLATIONS['en'];
    let str = (langDict && key in langDict) ? langDict[key] : (TRANSLATIONS['en']?.[key] || (typeof paramsOrFallback === 'string' ? paramsOrFallback : fallback) || key);

    if (paramsOrFallback && typeof paramsOrFallback === 'object') {
      Object.entries(paramsOrFallback).forEach(([pKey, pVal]) => {
        str = str.replace(new RegExp(`\\{${pKey}\\}`, 'g'), String(pVal));
      });
    }

    return str;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        speechCode: currentMeta.speechCode,
        languageMeta: currentMeta,
        meta: currentMeta,
        supportedLanguages: SUPPORTED_LANGUAGES
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
