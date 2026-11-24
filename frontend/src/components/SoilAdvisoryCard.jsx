import React, { useState } from 'react';
import { Layers, CheckCircle2, AlertCircle, Info, Sparkles } from 'lucide-react';
import { getSoilAdvisory } from '../services/api';
import { translations } from '../locales/translations';

export default function SoilAdvisoryCard({ language, onSelectCropForChat }) {
  const t = translations[language] || translations.en;

  const [soilType, setSoilType] = useState('black');
  const [ph, setPh] = useState('7.2');
  const [landSize, setLandSize] = useState('4.0');
  const [preferredCrop, setPreferredCrop] = useState('Cotton');
  const [advisory, setAdvisory] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await getSoilAdvisory({
        soil_type: soilType,
        ph: ph ? parseFloat(ph) : null,
        land_size_acres: landSize ? parseFloat(landSize) : null,
        preferred_crop: preferredCrop || null,
        language
      });
      setAdvisory(data);
    } catch (err) {
      console.error('Soil advisory error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 hover:shadow-md transition">
      {/* Header */}
      <div className="border-b border-slate-100 pb-4 mb-4">
        <div className="flex items-center gap-2">
          <h3 className="font-bold text-lg text-slate-900">{t.soilTitle}</h3>
          <span className="text-[10px] font-semibold bg-earth-100 text-earth-800 px-2 py-0.5 rounded-full border border-earth-200">
            ICAR Guidelines
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-0.5">{t.soilSubtitle}</p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        {/* Soil Type */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            {t.soilTypeLabel}
          </label>
          <select
            value={soilType}
            onChange={(e) => setSoilType(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-agri-500"
          >
            <option value="black">{t.soilTypeBlack}</option>
            <option value="alluvial">{t.soilTypeAlluvial}</option>
            <option value="red_sandy">{t.soilTypeRedSandy}</option>
            <option value="clay_loam">{t.soilTypeClayLoam}</option>
          </select>
        </div>

        {/* Soil pH */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            {t.soilPhLabel}
          </label>
          <input
            type="number"
            step="0.1"
            min="4"
            max="10"
            value={ph}
            onChange={(e) => setPh(e.target.value)}
            placeholder="e.g. 7.2"
            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-agri-500"
          />
        </div>

        {/* Land Size */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            {t.soilLandLabel}
          </label>
          <input
            type="number"
            step="0.5"
            min="0.1"
            value={landSize}
            onChange={(e) => setLandSize(e.target.value)}
            placeholder="Acres"
            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-agri-500"
          />
        </div>

        {/* Preferred Crop & Button */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            {t.soilCropLabel}
          </label>
          <div className="flex gap-1.5">
            <input
              type="text"
              value={preferredCrop}
              onChange={(e) => setPreferredCrop(e.target.value)}
              placeholder="e.g. Cotton / कापूस"
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-agri-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-agri-600 hover:bg-agri-700 text-white font-semibold text-xs px-3 py-1.5 rounded-lg shrink-0 transition flex items-center gap-1 shadow-sm"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{t.soilGetAdvisory}</span>
            </button>
          </div>
        </div>
      </form>

      {/* Advisory Result */}
      {advisory && (
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 space-y-3.5">
          {/* Soil & pH Overview */}
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/60 pb-3">
            <div>
              <span className="text-xs font-semibold text-slate-500 block">Identified Soil Classification:</span>
              <span className="font-bold text-sm text-slate-900">{advisory.soil_profile}</span>
              <p className="text-xs text-slate-600 mt-0.5">{advisory.soil_characteristics}</p>
            </div>
            <div className="bg-white px-3 py-1.5 rounded-lg border border-slate-200 text-xs">
              <span className="text-slate-500 block text-[10px]">pH Evaluation:</span>
              <span className="font-semibold text-slate-800">{advisory.ph_evaluation.assessment}</span>
            </div>
          </div>

          {/* Crop Suitability Status */}
          <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs">
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-800">
                Crop Suitability for {advisory.crop_suitability.preferred_crop}:
              </span>
              <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 font-bold rounded-md">
                {advisory.crop_suitability.status}
              </span>
            </div>
            {advisory.crop_suitability.note && (
              <p className="text-slate-600 mt-1">{advisory.crop_suitability.note}</p>
            )}
          </div>

          {/* Recommended Crops */}
          <div>
            <span className="text-xs font-bold text-slate-800 block mb-1.5">
              🌿 {t.soilRecommendedCrops}:
            </span>
            <div className="flex flex-wrap gap-2">
              {advisory.recommended_crops?.map((crop, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => onSelectCropForChat && onSelectCropForChat(crop)}
                  className="text-xs bg-agri-100 text-agri-900 hover:bg-agri-200 font-semibold px-2.5 py-1 rounded-lg border border-agri-200 transition flex items-center gap-1"
                  title="Click to ask AI about this crop"
                >
                  <CheckCircle2 className="w-3 h-3 text-agri-600" />
                  <span>{crop}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Land Management Practices */}
          <div>
            <span className="text-xs font-bold text-slate-800 block mb-1">
              🚜 {t.soilPractices}:
            </span>
            <ul className="text-xs text-slate-600 space-y-1 list-disc list-inside">
              {advisory.land_management_practices?.map((p, idx) => (
                <li key={idx}>{p}</li>
              ))}
            </ul>
          </div>

          {/* Disclaimer */}
          <div className="text-[11px] text-slate-500 italic flex items-start gap-1.5 pt-1 border-t border-slate-200/60">
            <Info className="w-3.5 h-3.5 shrink-0 text-slate-400 mt-0.5" />
            <span>{advisory.disclaimer}</span>
          </div>
        </div>
      )}
    </div>
  );
}
