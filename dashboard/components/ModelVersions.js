import React from 'react';
import { formatPercent, getStatusColor } from '../lib/utils';
import { RefreshCw } from 'lucide-react';

export default function ModelVersions({ versions, onRollback }) {
  if (!versions || versions.length === 0) {
    return (
      <div className="bg-[#18181b] border border-white/10 p-5 rounded-xl text-center text-[#a1a1aa] text-sm">
        No versions registered in registry
      </div>
    );
  }

  const formatStatus = (status) => {
    return String(status).replace('_', ' ').toUpperCase();
  };

  return (
    <div className="bg-[#18181b] border border-white/10 p-5 rounded-xl shadow-md flex flex-col space-y-4">
      <h3 className="text-sm font-bold text-[#ededed]">Model Version Registry</h3>
      
      <div className="overflow-x-auto border border-white/10/50 rounded-xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-[#09090b] border-b border-white/10 text-[10px] text-[#a1a1aa] uppercase tracking-wider font-semibold">
              <th className="px-4 py-3">Version</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Accuracy</th>
              <th className="px-4 py-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#30363d]/30 text-xs">
            {versions.map((v, index) => {
              const isArchived = v.status === 'archived';
              return (
                <tr key={index} className="hover:bg-[#2e2e2e]/20 transition-colors">
                  <td className="px-4 py-3 font-semibold text-[#ededed]">
                    {v.version !== null && v.version !== undefined ? `v${v.version}` : 'N/A'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold tracking-wide uppercase border ${getStatusColor(v.status)}`}>
                      {formatStatus(v.status)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[#ededed] font-mono">
                    {v.accuracy !== null && v.accuracy !== undefined ? formatPercent(v.accuracy) : 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {isArchived ? (
                      <button
                        onClick={() => onRollback(v.version)}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-[#2e2e2e] border border-[#f85149]/30 hover:bg-[#3d1515] hover:text-[#f85149] hover:border-[#f85149] text-[10px] font-bold text-[#f85149] transition-all cursor-pointer active:scale-95"
                      >
                        <RefreshCw className="w-2.5 h-2.5" />
                        <span>Rollback</span>
                      </button>
                    ) : (
                      <span className="text-[10px] text-[#a1a1aa] italic">Locked</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
