import React, { useState, useEffect } from 'react';
import { CloudRain, Wind, Droplets, Thermometer, AlertTriangle, CheckCircle, Info, Clock, MapPin } from 'lucide-react';
import { getWeather } from '../services/api';
import { translations } from '../locales/translations';

export default function WeatherCard({ language, selectedLocation, onLocationChange }) {
  const t = translations[language] || translations.en;
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const locations = [
    { name: 'Pune', state: 'Maharashtra' },
    { name: 'Nagpur', state: 'Maharashtra' },
    { name: 'Nashik', state: 'Maharashtra' },
    { name: 'Akola', state: 'Maharashtra' },
    { name: 'Ahmedabad', state: 'Gujarat' },
    { name: 'Rajkot', state: 'Gujarat' },
    { name: 'Indore', state: 'Madhya Pradesh' }
  ];

  const fetchWeatherData = async (loc) => {
    setLoading(true);
    setError('');
    try {
      const data = await getWeather(loc);
      setWeather(data);
    } catch (err) {
      console.error('Weather load error:', err);
      setError('Could not load weather information.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeatherData(selectedLocation || 'Pune');
  }, [selectedLocation]);

  const handleSelect = (e) => {
    const loc = e.target.value;
    if (onLocationChange) onLocationChange(loc);
    fetchWeatherData(loc);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 hover:shadow-md transition">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-lg text-slate-900">{t.weatherTitle}</h3>
            {weather?.status === 'live' ? (
              <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-200">
                ● {t.weatherLive}
              </span>
            ) : (
              <span className="text-[10px] font-semibold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full border border-amber-200">
                {t.weatherBenchmark}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
            <Clock className="w-3 h-3" /> {weather?.observation_time || 'Just now'} | {weather?.source}
          </p>
        </div>

        {/* Location Dropdown */}
        <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1">
          <MapPin className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={selectedLocation}
            onChange={handleSelect}
            className="bg-transparent text-xs font-semibold text-slate-800 focus:outline-none cursor-pointer"
          >
            {locations.map((l) => (
              <option key={l.name} value={l.name}>
                {l.name} ({l.state})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <div className="py-8 text-center text-slate-400 text-sm animate-pulse">
          Loading weather indicators...
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 text-red-700 text-xs rounded-xl border border-red-200">
          {error}
        </div>
      )}

      {weather && !loading && (
        <>
          {/* Main Weather Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
            <div className="bg-gradient-to-br from-amber-50 to-orange-50/50 p-3.5 rounded-xl border border-amber-200/60">
              <div className="flex items-center gap-1.5 text-amber-700 text-xs font-medium">
                <Thermometer className="w-4 h-4" />
                <span>{t.weatherTemp}</span>
              </div>
              <div className="mt-1 text-2xl font-bold text-slate-900">
                {weather.temperature_c}°C
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">{weather.condition}</div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-sky-50/50 p-3.5 rounded-xl border border-blue-200/60">
              <div className="flex items-center gap-1.5 text-blue-700 text-xs font-medium">
                <Droplets className="w-4 h-4" />
                <span>{t.weatherHumidity}</span>
              </div>
              <div className="mt-1 text-2xl font-bold text-slate-900">
                {weather.humidity_percent}%
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">Relative Moisture</div>
            </div>

            <div className="bg-gradient-to-br from-teal-50 to-emerald-50/50 p-3.5 rounded-xl border border-teal-200/60">
              <div className="flex items-center gap-1.5 text-teal-700 text-xs font-medium">
                <Wind className="w-4 h-4" />
                <span>{t.weatherWind}</span>
              </div>
              <div className="mt-1 text-2xl font-bold text-slate-900">
                {weather.wind_speed_kmh} <span className="text-xs font-normal">km/h</span>
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">Wind Velocity</div>
            </div>

            <div className="bg-gradient-to-br from-indigo-50 to-slate-50 p-3.5 rounded-xl border border-indigo-200/60">
              <div className="flex items-center gap-1.5 text-indigo-700 text-xs font-medium">
                <CloudRain className="w-4 h-4" />
                <span>{t.weatherRain}</span>
              </div>
              <div className="mt-1 text-2xl font-bold text-slate-900">
                {weather.precipitation_mm} <span className="text-xs font-normal">mm</span>
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">Precipitation</div>
            </div>
          </div>

          {/* Agricultural Impact Advisories */}
          <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-200/80">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <span>🌾 {t.weatherAlerts}</span>
            </h4>
            <div className="space-y-2">
              {weather.agricultural_advisories?.map((adv, idx) => (
                <div
                  key={idx}
                  className={`text-xs p-2.5 rounded-lg flex items-start gap-2 border ${
                    adv.type === 'danger'
                      ? 'bg-red-50 text-red-800 border-red-200'
                      : adv.type === 'warning'
                      ? 'bg-amber-50 text-amber-900 border-amber-200'
                      : adv.type === 'success'
                      ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
                      : 'bg-blue-50 text-blue-900 border-blue-200'
                  }`}
                >
                  {adv.type === 'danger' || adv.type === 'warning' ? (
                    <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  ) : adv.type === 'success' ? (
                    <CheckCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  ) : (
                    <Info className="w-4 h-4 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <span className="font-semibold block">{adv.category}</span>
                    <span>{adv.message}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
