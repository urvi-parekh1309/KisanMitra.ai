import React, { useState, useEffect } from 'react';
import { TrendingUp, MapPin, Calendar, Tag, RefreshCw, AlertCircle } from 'lucide-react';
import { getMandiPrices } from '../services/api';
import { translations } from '../locales/translations';

export default function MandiPriceCard({ language }) {
  const t = translations[language] || translations.en;
  const [commodity, setCommodity] = useState('');
  const [state, setState] = useState('');
  const [mandiResponse, setMandiResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const commodities = ['Cotton', 'Soybean', 'Wheat', 'Onion', 'Groundnut'];
  const states = ['Maharashtra', 'Gujarat', 'Madhya Pradesh'];

  const fetchPrices = async () => {
    setLoading(true);
    try {
      const data = await getMandiPrices(commodity, state);
      setMandiResponse(data);
    } catch (err) {
      console.error('Mandi prices load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrices();
  }, [commodity, state]);

  const records = mandiResponse?.data || [];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 hover:shadow-md transition">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-lg text-slate-900">{t.mandiTitle}</h3>
            <span className="text-[10px] font-semibold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-200">
              AGMARKNET
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{t.mandiSubtitle}</p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2">
          {/* Commodity Selector */}
          <select
            value={commodity}
            onChange={(e) => setCommodity(e.target.value)}
            className="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none cursor-pointer"
          >
            <option value="">{t.mandiAllCrops}</option>
            {commodities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          {/* State Selector */}
          <select
            value={state}
            onChange={(e) => setState(e.target.value)}
            className="bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none cursor-pointer"
          >
            <option value="">All States</option>
            {states.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          <button
            onClick={fetchPrices}
            className="p-1.5 rounded-lg bg-slate-100 text-slate-600 hover:bg-slate-200 transition"
            title="Refresh prices"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {loading && (
        <div className="py-8 text-center text-slate-400 text-sm animate-pulse">
          Fetching verified AGMARKNET prices...
        </div>
      )}

      {/* When no data / unavailable */}
      {!loading && records.length === 0 && (
        <div className="p-4 bg-amber-50 text-amber-900 rounded-xl border border-amber-200 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-amber-600" />
          <div>
            <span className="font-semibold block">Data Unavailable</span>
            <span>{mandiResponse?.message || 'No live price reporting available for this selection.'}</span>
          </div>
        </div>
      )}

      {/* Market Price Records Grid */}
      {!loading && records.length > 0 && (
        <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
          {records.map((item, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:border-agri-300 transition-all flex flex-wrap items-center justify-between gap-3"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-slate-900">{item.market}</span>
                  <span className="text-[11px] text-slate-500 flex items-center gap-1">
                    <MapPin className="w-3 h-3" /> {item.district}, {item.state}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-600 mt-1">
                  <span className="flex items-center gap-1 font-medium text-agri-800 bg-agri-100 px-2 py-0.5 rounded-md">
                    <Tag className="w-3 h-3" /> {item.commodity} ({item.variety})
                  </span>
                  <span className="flex items-center gap-1 text-[11px] text-slate-500">
                    <Calendar className="w-3 h-3" /> {item.arrival_date}
                  </span>
                </div>
              </div>

              {/* Price Columns */}
              <div className="text-right">
                <div className="text-xs text-slate-500">{t.mandiModalPrice}</div>
                <div className="text-lg font-extrabold text-agri-700">
                  ₹{item.modal_price.toLocaleString('en-IN')}{' '}
                  <span className="text-[10px] font-normal text-slate-500">/ Qtl</span>
                </div>
                <div className="text-[11px] text-slate-500">
                  Range: ₹{item.min_price} - ₹{item.max_price}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
