import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, ChevronDown, ChevronUp, AlertCircle, FileText } from 'lucide-react';
import { sendChatMessage } from '../services/api';
import { translations } from '../locales/translations';
import VoiceInput from './VoiceInput';

export default function ChatWindow({ language, activeLocation = 'Pune', initialQuestion = '' }) {
  const t = translations[language] || translations.en;

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: t.chatSubtitle,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedSources, setExpandedSources] = useState({});
  const messagesEndRef = useRef(null);

  // Suggested questions in the current language
  const suggestedQuestions = [
    t.suggestedQ1,
    t.suggestedQ2,
    t.suggestedQ3,
    t.suggestedQ4
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    if (initialQuestion) {
      handleSend(initialQuestion);
    }
  }, [initialQuestion]);

  const handleSend = async (queryText) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage({
        query: textToSend,
        language,
        location: activeLocation
      });

      const botMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        text: response.answer,
        model: response.model,
        sources: response.sources || [],
        has_rag_context: response.has_rag_context,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error('Chat API Error:', err);
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'bot',
        text: `Error: ${err.message || 'Could not communicate with the agricultural advisor backend.'}`,
        isError: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSources = (msgId) => {
    setExpandedSources((prev) => ({
      ...prev,
      [msgId]: !prev[msgId]
    }));
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[650px] overflow-hidden">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-100 bg-gradient-to-r from-agri-50/60 to-white flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-agri-600 text-white flex items-center justify-center shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
              <span>{t.chatTitle}</span>
              <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-200">
                ICAR Grounded
              </span>
            </h3>
            <p className="text-xs text-slate-500">Live Context: {activeLocation} | Language: {language.toUpperCase()}</p>
          </div>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/30">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'bot' && (
              <div className="w-8 h-8 rounded-lg bg-agri-600 text-white flex items-center justify-center shrink-0 text-xs shadow-sm mt-1">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div className={`max-w-[85%] sm:max-w-[75%] space-y-2`}>
              {/* Message Bubble */}
              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-agri-600 text-white rounded-tr-none shadow-sm'
                    : msg.isError
                    ? 'bg-red-50 text-red-900 border border-red-200 rounded-tl-none'
                    : 'bg-white text-slate-900 border border-slate-200/90 rounded-tl-none shadow-sm'
                }`}
              >
                {/* Render formatted text */}
                <div className="whitespace-pre-wrap font-normal">
                  {msg.text}
                </div>

                {/* Footer bar for bot responses */}
                {msg.sender === 'bot' && !msg.isError && (
                  <div className="mt-3 pt-2.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
                    <span className="text-[10px] text-slate-400">
                      Model: {msg.model || 'Gemini 2.5 Flash'} • {msg.timestamp}
                    </span>

                    {/* Audio Playback button for Farmer accessibility */}
                    <VoiceInput language={language} textToSpeak={msg.text} />
                  </div>
                )}
              </div>

              {/* RAG Sources Citations Section */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="bg-emerald-50/70 border border-emerald-200/80 rounded-xl p-2.5 text-xs text-emerald-950">
                  <button
                    type="button"
                    onClick={() => toggleSources(msg.id)}
                    className="w-full flex items-center justify-between font-bold text-emerald-900 hover:text-emerald-950 transition"
                  >
                    <span className="flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-emerald-700" />
                      <span>{t.chatSourcesTitle} ({msg.sources.length})</span>
                    </span>
                    {expandedSources[msg.id] ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )}
                  </button>

                  {/* Expanded Citations */}
                  {expandedSources[msg.id] && (
                    <div className="mt-2.5 space-y-2 border-t border-emerald-200/60 pt-2">
                      {msg.sources.map((src, sIdx) => (
                        <div key={sIdx} className="bg-white p-2.5 rounded-lg border border-emerald-200 text-xs">
                          <div className="flex items-center justify-between text-slate-700 font-semibold mb-1">
                            <span className="flex items-center gap-1">
                              <FileText className="w-3 h-3 text-agri-600" />
                              <span>{src.document}</span>
                              <span className="text-slate-400 font-normal">({t.chatSourcePage} {src.page})</span>
                            </span>
                            <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
                              {t.chatRelevance}: {Math.round(src.relevance_score * 100)}%
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-600 italic bg-slate-50 p-1.5 rounded border border-slate-100">
                            "{src.snippet}"
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-slate-800 text-white flex items-center justify-center shrink-0 text-xs shadow-sm mt-1">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 justify-start items-center">
            <div className="w-8 h-8 rounded-lg bg-agri-600 text-white flex items-center justify-center shrink-0 text-xs">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-white border border-slate-200 p-3 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2 text-xs text-slate-500">
              <Sparkles className="w-4 h-4 text-agri-600 animate-spin" />
              <span>Retrieving verified ICAR documents & analyzing advisory...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Question Chips */}
      <div className="px-4 py-2 bg-slate-100/60 border-t border-slate-200/60 flex items-center gap-2 overflow-x-auto">
        <span className="text-[11px] font-bold text-slate-500 shrink-0 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-agri-600" />
          {t.suggestedQuestionsTitle}
        </span>
        {suggestedQuestions.map((q, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSend(q)}
            className="text-xs bg-white text-slate-700 hover:text-agri-700 hover:border-agri-300 px-2.5 py-1 rounded-full border border-slate-200 transition shrink-0 whitespace-nowrap shadow-xs"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input Form Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 bg-white border-t border-slate-200 flex items-center gap-2"
      >
        {/* Voice Input (Mic) */}
        <VoiceInput
          language={language}
          onSpeechResult={(transcript) => {
            setInput(transcript);
            handleSend(transcript);
          }}
        />

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t.chatPlaceholder}
          disabled={loading}
          className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-agri-500 transition"
        />

        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-agri-600 hover:bg-agri-700 disabled:opacity-50 text-white px-4 py-2.5 rounded-xl font-semibold text-sm flex items-center gap-1.5 transition shadow-sm"
        >
          <Send className="w-4 h-4" />
          <span className="hidden sm:inline">{t.chatSend}</span>
        </button>
      </form>
    </div>
  );
}
