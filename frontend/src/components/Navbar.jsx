import React from 'react';
import { Sprout, Globe, Activity, BookOpen } from 'lucide-react';
import { translations } from '../locales/translations';

export default function Navbar({ language, onLanguageChange, activeTab, onTabChange, backendStatus, onOpenKB }) {
  const t = translations[language] || translations.en;

  const languages = [
    { code: 'mr', label: 'मराठी (Marathi)' },
    { code: 'hi', label: 'हिन्दी (Hindi)' },
    { code: 'gu', label: 'ગુજરાતી (Gujarati)' },
    { code: 'en', label: 'English' }
  ];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => onTabChange('chat')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-agri-600 to-agri-400 flex items-center justify-center text-white shadow-md shadow-agri-500/20">
              <Sprout className="w-6 h-6 stroke-[2.2]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-xl tracking-tight text-slate-900">{t.appName}</span>
                <span className="text-[10px] font-semibold uppercase tracking-wider bg-agri-100 text-agri-800 px-2 py-0.5 rounded-full border border-agri-200">
                  RAG + AI
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">{t.appTagline}</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200/60">
            <button
              onClick={() => onTabChange('chat')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'chat'
                  ? 'bg-white text-agri-700 shadow-sm border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              💬 {t.navChat}
            </button>
            <button
              onClick={() => onTabChange('weather')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'weather'
                  ? 'bg-white text-agri-700 shadow-sm border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              🌦️ {t.navWeather}
            </button>
            <button
              onClick={() => onTabChange('mandi')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'mandi'
                  ? 'bg-white text-agri-700 shadow-sm border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              🌾 {t.navMandi}
            </button>
            <button
              onClick={() => onTabChange('soil')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'soil'
                  ? 'bg-white text-agri-700 shadow-sm border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              🌱 {t.navSoil}
            </button>
          </nav>

          {/* Right Section: Knowledge Base + Language Selector + Status */}
          <div className="flex items-center gap-3">
            {/* Knowledge base inspector button */}
            <button
              onClick={onOpenKB}
              className="flex items-center gap-1.5 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 px-2.5 py-1.5 rounded-lg border border-slate-200 transition"
              title="Inspect ICAR RAG Knowledge Base"
            >
              <BookOpen className="w-3.5 h-3.5 text-agri-600" />
              <span className="hidden lg:inline">{t.navKB}</span>
            </button>

            {/* Language Selector */}
            <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 shadow-sm">
              <Globe className="w-4 h-4 text-slate-500" />
              <select
                value={language}
                onChange={(e) => onLanguageChange(e.target.value)}
                className="bg-transparent text-xs font-semibold text-slate-800 focus:outline-none cursor-pointer pr-1"
                aria-label="Select Language"
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Backend Status Indicator */}
            <div className="flex items-center gap-1.5 text-xs font-medium px-2 py-1 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="hidden sm:inline">Online</span>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
}
