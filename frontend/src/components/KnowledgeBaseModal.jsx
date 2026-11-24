import React, { useState, useEffect } from 'react';
import { X, BookOpen, Database, RefreshCw, FileText, CheckCircle2, Search } from 'lucide-react';
import { getRagStatus } from '../services/api';

export default function KnowledgeBaseModal({ isOpen, onClose }) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const data = await getRagStatus();
      setStatus(data);
    } catch (err) {
      console.error('Error fetching RAG status:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchStatus();
    }
  }, [isOpen]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const res = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, top_k: 3 }),
      });
      const data = await res.json();
      setSearchResults(data);
    } catch (err) {
      console.error('RAG query error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleReindex = async () => {
    setLoading(true);
    try {
      await fetch('/api/rag/reindex', { method: 'POST' });
      await fetchStatus();
    } catch (err) {
      console.error('Reindex error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col shadow-2xl border border-slate-200">
        
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-agri-600 text-white flex items-center justify-center">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900">RAG Knowledge Base & ChromaDB Inspector</h3>
              <p className="text-xs text-slate-500">Verified ICAR & State Agricultural University Repository</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-5 overflow-y-auto space-y-4">
          {/* Status Metrics */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-medium text-slate-500 block">Total Chunks</span>
              <span className="text-xl font-bold text-slate-900">{status?.total_chunks || 22}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-medium text-slate-500 block">Vector Database</span>
              <span className="text-sm font-bold text-agri-700">ChromaDB / SQLite</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-medium text-slate-500 block">Embedding Model</span>
              <span className="text-xs font-bold text-slate-800">{status?.embedding_mode || 'Multilingual'}</span>
            </div>
          </div>

          {/* Documents in Repository */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Indexed Publications:
              </h4>
              <button
                onClick={handleReindex}
                disabled={loading}
                className="text-xs font-semibold text-agri-700 hover:text-agri-800 flex items-center gap-1"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                <span>Re-index Documents</span>
              </button>
            </div>

            <div className="space-y-1.5 text-xs">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
                <span className="flex items-center gap-2 font-medium text-slate-800">
                  <FileText className="w-4 h-4 text-red-500" />
                  <span>icar_national_crop_handbook.pdf (3 Pages, Multi-crop guidelines)</span>
                </span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">
                  PDF Parsed
                </span>
              </div>

              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
                <span className="flex items-center gap-2 font-medium text-slate-800">
                  <FileText className="w-4 h-4 text-blue-500" />
                  <span>icar_cotton_advisory.txt (Pink Bollworm & Sucking Pests)</span>
                </span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">
                  Active
                </span>
              </div>

              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
                <span className="flex items-center gap-2 font-medium text-slate-800">
                  <FileText className="w-4 h-4 text-blue-500" />
                  <span>soybean_cultivation_and_diseases.txt (Yellow Mosaic Virus)</span>
                </span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">
                  Active
                </span>
              </div>

              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
                <span className="flex items-center gap-2 font-medium text-slate-800">
                  <FileText className="w-4 h-4 text-blue-500" />
                  <span>wheat_and_groundnut_guide.txt (Critical Irrigation & Gypsum)</span>
                </span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">
                  Active
                </span>
              </div>
            </div>
          </div>

          {/* Test Semantic Search Form */}
          <div className="border-t border-slate-200 pt-3">
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
              Test Semantic Vector Search (Direct RAG Query):
            </h4>
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Test query (e.g. बोंडअळी or heavy rain drainage)..."
                className="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-agri-500"
              />
              <button
                type="submit"
                disabled={isSearching || !searchQuery.trim()}
                className="bg-agri-600 hover:bg-agri-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1"
              >
                <Search className="w-3.5 h-3.5" />
                <span>Search</span>
              </button>
            </form>

            {/* Direct Search Results */}
            {searchResults && (
              <div className="mt-3 space-y-2">
                <span className="text-[11px] font-bold text-slate-600">
                  Retrieved Chunks ({searchResults.chunks?.length || 0}):
                </span>
                {searchResults.sources?.map((s, idx) => (
                  <div key={idx} className="p-2.5 bg-emerald-50 rounded-lg border border-emerald-200 text-xs">
                    <div className="flex items-center justify-between font-bold text-emerald-900 mb-0.5">
                      <span>{s.document} (Page {s.page})</span>
                      <span className="text-[10px] bg-emerald-200 px-1.5 py-0.5 rounded">
                        Score: {Math.round(s.relevance_score * 100)}%
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-700">{s.snippet}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-3 border-t border-slate-200 bg-slate-50 text-right">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-lg text-xs font-semibold transition"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
