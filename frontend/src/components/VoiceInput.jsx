import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Square, AlertCircle } from 'lucide-react';
import { translations } from '../locales/translations';

export default function VoiceInput({ language, onSpeechResult, textToSpeak = '' }) {
  const t = translations[language] || translations.en;

  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const recognitionRef = useRef(null);

  // Map language to browser speech recognition locale
  const langLocaleMap = {
    mr: 'mr-IN',
    hi: 'hi-IN',
    gu: 'gu-IN',
    en: 'en-IN'
  };

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = langLocaleMap[language] || 'en-IN';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (transcript && onSpeechResult) {
        onSpeechResult(transcript);
      }
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.warn('[SpeechRecognition] Error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [language]);

  const toggleListening = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.lang = langLocaleMap[language] || 'en-IN';
        recognitionRef.current.start();
      } catch (err) {
        console.error('Error starting speech recognition:', err);
      }
    }
  };

  // Text-to-Speech functionality to read response to farmer
  const toggleSpeech = () => {
    if (!('speechSynthesis' in window) || !textToSpeak) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    } else {
      window.speechSynthesis.cancel(); // clear previous queue

      // Clean markdown tags for natural speech
      const cleanText = textToSpeak
        .replace(/[*#_`>]/g, '')
        .replace(/\[.*?\]/g, '')
        .replace(/\n+/g, '. ');

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = langLocaleMap[language] || 'en-IN';
      utterance.rate = 0.95; // Slightly slower for clarity

      // Attempt to pick matching Indian voice if available
      const voices = window.speechSynthesis.getVoices();
      const targetLang = langLocaleMap[language];
      const matchedVoice = voices.find(v => v.lang.startsWith(language) || v.lang === targetLang);
      if (matchedVoice) {
        utterance.voice = matchedVoice;
      }

      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  };

  return (
    <div className="flex items-center gap-2">
      {/* Speech-to-Text Microphone Button */}
      {speechSupported ? (
        <button
          type="button"
          onClick={toggleListening}
          className={`p-2.5 rounded-xl flex items-center justify-center transition-all ${
            isListening
              ? 'bg-red-500 text-white animate-pulse shadow-md shadow-red-500/30'
              : 'bg-agri-50 text-agri-700 hover:bg-agri-100 border border-agri-200'
          }`}
          title={isListening ? t.chatListening : "Click to speak in your language"}
          aria-label="Voice input"
        >
          {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>
      ) : (
        <span title="Speech recognition not supported in this browser" className="text-slate-400 p-2">
          <AlertCircle className="w-4 h-4" />
        </span>
      )}

      {/* Text-to-Speech Playback Button (if textToSpeak is provided) */}
      {textToSpeak && (
        <button
          type="button"
          onClick={toggleSpeech}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            isSpeaking
              ? 'bg-amber-100 text-amber-800 border border-amber-300 animate-pulse'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200'
          }`}
          title={isSpeaking ? t.chatStopSpeak : t.chatSpeakAnswer}
        >
          {isSpeaking ? (
            <>
              <Square className="w-3.5 h-3.5 fill-current" />
              <span>{t.chatStopSpeak}</span>
            </>
          ) : (
            <>
              <Volume2 className="w-3.5 h-3.5" />
              <span>{t.chatSpeakAnswer}</span>
            </>
          )}
        </button>
      )}
    </div>
  );
}
