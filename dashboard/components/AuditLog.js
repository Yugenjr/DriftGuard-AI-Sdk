import React, { useState } from 'react';
import { formatDate, formatDriftScore } from '../lib/utils';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';

export default function AuditLog({ logs }) {
  const [search, setSearch] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  if (!logs || logs.length === 0) {
    return (
      <div className="bg-[#18181b] border border-white/10 p-5 rounded-xl text-center text-[#a1a1aa] text-sm">
        No audit events recorded yet
      </div>
    );
  }

  const getEventBadgeClass = (type) => {
    switch (String(type).toLowerCase()) {
      case 'drift_detected':
        return 'text-[#d29922] bg-[#3d2f00] border border-[#554000]/40';
      case 'retrain_triggered':
        return 'text-[#24b47e] bg-[#1c2d3a] border border-[#243e56]/40';
      case 'model_promoted':
        return 'text-[#3fb950] bg-[#1a4731] border border-[#1f5a3a]/40';
      case 'rollback':
        return 'text-[#f85149] bg-[#3d1515] border border-[#5a1e1e]/40';
      default:
        return 'text-[#ededed] bg-[#2e2e2e] border border-white/10';
    }
  };

  const formatEventType = (type) => {
    return String(type).replace('_', ' ').toUpperCase();
  };

  // Filter logs based on search string
  const filteredLogs = logs.filter(log => {
    const term = search.toLowerCase();
    return (
      String(log.event_type || '').toLowerCase().includes(term) ||
      String(log.model_version || '').toLowerCase().includes(term) ||
      String(log.triggered_by || '').toLowerCase().includes(term) ||
      String(log.drift_score || '').toLowerCase().includes(term) ||
      formatDate(log.timestamp).toLowerCase().includes(term)
    );
  });

  // Pagination parameters
  const pageSize = 10;
  const totalItems = filteredLogs.length;
  const totalPages = Math.ceil(totalItems / pageSize) || 1;
  
  // Enforce page constraints
  const activePage = Math.min(currentPage, totalPages);
  const startIndex = (activePage - 1) * pageSize;
  const currentLogs = filteredLogs.slice(startIndex, startIndex + pageSize);

  return (
    <div className="bg-[#18181b] border border-white/10 p-5 rounded-xl shadow-md flex flex-col space-y-4">
      {/* Search Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <h3 className="text-sm font-bold text-[#ededed]">Audit Trail & Ledger</h3>
        <div className="relative w-full md:w-72">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#a1a1aa]">
            <Search className="w-3.5 h-3.5" />
          </span>
          <input
            type="text"
            placeholder="Filter audit logs..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full pl-9 pr-4 py-1.5 rounded-xl bg-[#09090b] border border-white/10 text-xs text-[#ededed] placeholder-[#7d8590] focus:outline-none focus:border-[#24b47e] transition-colors"
          />
        </div>
      </div>

      {/* Table grid */}
      <div className="overflow-x-auto border border-white/10/50 rounded-xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#09090b] border-b border-white/10 text-[10px] text-[#a1a1aa] uppercase tracking-wider font-semibold">
              <th className="px-4 py-3">Timestamp</th>
              <th className="px-4 py-3">Event Type</th>
              <th className="px-4 py-3">Model Version</th>
              <th className="px-4 py-3">Drift Score</th>
              <th className="px-4 py-3">Triggered By</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#30363d]/30 text-xs">
            {currentLogs.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-[#a1a1aa]">
                  No matching audit logs located
                </td>
              </tr>
            ) : (
              currentLogs.map((log, index) => (
                <tr key={index} className="hover:bg-[#2e2e2e]/20 transition-colors">
                  <td className="px-4 py-3 text-[#a1a1aa] font-mono">
                    {formatDate(log.timestamp)}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold tracking-wide uppercase border ${getEventBadgeClass(log.event_type)}`}>
                      {formatEventType(log.event_type)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[#ededed] font-semibold">
                    {log.model_version !== null && log.model_version !== undefined ? `v${log.model_version}` : 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-[#ededed] font-mono font-medium">
                    {formatDriftScore(log.drift_score)}
                  </td>
                  <td className="px-4 py-3 text-[#a1a1aa] uppercase font-bold text-[9px] tracking-wider">
                    {log.triggered_by || 'auto'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <span className="text-[10px] text-[#a1a1aa]">
            Showing {startIndex + 1} to {Math.min(startIndex + pageSize, totalItems)} of {totalItems} logs
          </span>
          <div className="flex space-x-1.5">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={activePage === 1}
              className="p-1.5 rounded-xl border border-white/10 bg-[#2e2e2e]/50 hover:bg-[#2e2e2e] text-[#ededed] disabled:opacity-30 disabled:pointer-events-none transition-colors"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="px-3 py-1.5 text-xs text-[#ededed] bg-[#2e2e2e] border border-white/10 rounded-xl font-bold">
              {activePage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={activePage === totalPages}
              className="p-1.5 rounded-xl border border-white/10 bg-[#2e2e2e]/50 hover:bg-[#2e2e2e] text-[#ededed] disabled:opacity-30 disabled:pointer-events-none transition-colors"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
