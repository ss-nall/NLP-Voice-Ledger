import React, { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { LanguageProvider, useLanguage } from './context/LanguageContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LoginView } from './views/LoginView';
import { DashboardView } from './views/DashboardView';
import { ConversationView } from './views/ConversationView';
import { RemindersView } from './views/RemindersView';
import { TransactionsView } from './views/TransactionsView';
import { ReceivablesView } from './views/ReceivablesView';
import { PayablesView } from './views/PayablesView';
import { ReceivedView } from './views/ReceivedView';
import { PaidView } from './views/PaidView';
import { HealthView } from './views/HealthView';
import { SettingsView } from './views/SettingsView';

export const MainAppLayout: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [currentView, setCurrentView] = useState<string>('dashboard');

  if (!isAuthenticated) {
    return <LoginView />;
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <DashboardView />;
      case 'conversation':
        return <ConversationView />;
      case 'reminders':
        return <RemindersView />;
      case 'customers':
        return <ReceivablesView />;
      case 'suppliers':
        return <PayablesView />;
      case 'received':
        return <ReceivedView />;
      case 'paid':
        return <PaidView />;
      case 'transactions':
        return <TransactionsView />;
      case 'health':
        return <HealthView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <DashboardView />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar currentView={currentView} onSelectView={setCurrentView} />

      <div className="main-content">
        <Navbar currentView={currentView} />

        <main className="page-body">
          {renderCurrentView()}
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <MainAppLayout />
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
};

export default App;
