import React, { useState } from 'react';
import ChatWindow from '../components/ChatWindow';
import WeatherCard from '../components/WeatherCard';
import MandiPriceCard from '../components/MandiPriceCard';
import SoilAdvisoryCard from '../components/SoilAdvisoryCard';
import { translations } from '../locales/translations';

export default function Dashboard({ language, activeTab, onTabChange }) {
  const t = translations[language] || translations.en;
  const [selectedLocation, setSelectedLocation] = useState('Pune');
  const [injectedQuestion, setInjectedQuestion] = useState('');

  const handleSelectCropForChat = (cropName) => {
    onTabChange('chat');
    const prompts = {
      mr: `${cropName} या पिकाची लागवड कशी करावी आणि खत नियोजन काय असावे?`,
      hi: `${cropName} फसल की बुवाई और खाद प्रबंधन की सही विधि क्या है?`,
      gu: `${cropName} પાકની વાવણી અને ખાતર વ્યવસ્થાપન કેવી રીતે કરવું?`,
      en: `What is the optimal cultivation and fertilizer schedule for ${cropName}?`
    };
    setInjectedQuestion(prompts[language] || prompts.en);
  };

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Welcome Banner */}
      <div className="mb-6 bg-gradient-to-r from-agri-700 via-agri-600 to-emerald-600 rounded-2xl p-6 text-white shadow-md flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider bg-white/20 px-2.5 py-1 rounded-full text-emerald-100 border border-white/20">
            🌱 {t.appName}
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold mt-2 tracking-tight">
            {t.appTagline}
          </h1>
          <p className="text-xs sm:text-sm text-emerald-100 max-w-2xl mt-1">
            Real-time weather alerts, APMC mandi rates, soil health analysis, and ICAR-verified RAG intelligence.
          </p>
        </div>

        {/* Quick Language Badges */}
        <div className="flex items-center gap-2 bg-black/15 p-2 rounded-xl backdrop-blur-xs border border-white/10 text-xs font-semibold">
          <span className="text-emerald-200">भाषा / Languages:</span>
          <span className="px-2 py-0.5 bg-white/20 rounded-md">मराठी</span>
          <span className="px-2 py-0.5 bg-white/20 rounded-md">हिन्दी</span>
          <span className="px-2 py-0.5 bg-white/20 rounded-md">ગુજરાતી</span>
          <span className="px-2 py-0.5 bg-white/20 rounded-md">English</span>
        </div>
      </div>

      {/* Main Content Layout based on active tab */}
      {activeTab === 'chat' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Chat Assistant (7 columns) */}
          <div className="lg:col-span-7">
            <ChatWindow
              language={language}
              activeLocation={selectedLocation}
              initialQuestion={injectedQuestion}
            />
          </div>

          {/* Side Widgets: Weather & Mandi (5 columns) */}
          <div className="lg:col-span-5 space-y-6">
            <WeatherCard
              language={language}
              selectedLocation={selectedLocation}
              onLocationChange={setSelectedLocation}
            />
            <MandiPriceCard language={language} />
          </div>
        </div>
      )}

      {activeTab === 'weather' && (
        <div className="max-w-4xl mx-auto space-y-6">
          <WeatherCard
            language={language}
            selectedLocation={selectedLocation}
            onLocationChange={setSelectedLocation}
          />
        </div>
      )}

      {activeTab === 'mandi' && (
        <div className="max-w-4xl mx-auto space-y-6">
          <MandiPriceCard language={language} />
        </div>
      )}

      {activeTab === 'soil' && (
        <div className="max-w-4xl mx-auto space-y-6">
          <SoilAdvisoryCard
            language={language}
            onSelectCropForChat={handleSelectCropForChat}
          />
        </div>
      )}
    </main>
  );
}
