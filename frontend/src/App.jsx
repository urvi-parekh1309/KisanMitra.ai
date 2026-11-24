import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import KnowledgeBaseModal from './components/KnowledgeBaseModal';
import { checkBackendHealth } from './services/api';

export default function App() {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('agri_lang') || 'mr'; // Default to Marathi
  });
  const [activeTab, setActiveTab] = useState('chat');
  const [isKBOpen, setIsKBOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState('connecting');

  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    localStorage.setItem('agri_lang', newLang);
  };

  useEffect(() => {
    const pingHealth = async () => {
      try {
        await checkBackendHealth();
        setBackendStatus('online');
      } catch (err) {
        setBackendStatus('offline');
      }
    };

    pingHealth();
    const interval = setInterval(pingHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      <Navbar
        language={language}
        onLanguageChange={handleLanguageChange}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        backendStatus={backendStatus}
        onOpenKB={() => setIsKBOpen(true)}
      />

      <div className="flex-1">
        <Dashboard
          language={language}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
      </div>

      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-wrap items-center justify-between gap-2">
          <span>🌾 <strong>KisanMitra AI</strong> — Multilingual Agricultural & Resource Advisory Assistant</span>
          <span>Grounded on ICAR, AGMARKNET, and OpenWeather Verified Data Sources</span>
        </div>
      </footer>

      {/* Knowledge Base Inspector Modal */}
      <KnowledgeBaseModal
        isOpen={isKBOpen}
        onClose={() => setIsKBOpen(false)}
      />
    </div>
  );
}
