import React from 'react';
import { Server, Trophy, AlertTriangle, RefreshCw } from 'lucide-react';

export default function StatCard({ label, value, color }) {
  const getIconAndColor = () => {
    switch (label) {
      case 'Fleet Monitored':
        return { icon: Server, colorClass: 'text-[#ededed]' };
      case 'Stable Champion Models':
        return { icon: Trophy, colorClass: 'text-[#24b47e]' };
      case 'Drifting (SLA Breach)':
        return { icon: AlertTriangle, colorClass: 'text-[#d29922]' };
      case 'Active Retraining Loops':
        return { icon: RefreshCw, colorClass: 'text-[#24b47e]' };
      default:
        return { icon: Server, colorClass: 'text-[#ededed]' };
    }
  };

  const { icon: Icon, colorClass } = getIconAndColor();

  return (
    <div className="bg-[#121214] border border-white/10 p-5 rounded-xl shadow-sm hover:border-white/20 transition-all duration-300 relative overflow-hidden group">
      <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      <div className="flex items-center justify-between mb-4 relative z-10">
        <span className="text-[13px] text-[#a1a1aa] font-medium tracking-wide">
          {label}
        </span>
        <Icon className={`w-4 h-4 ${colorClass}`} />
      </div>
      <span className={`text-3xl font-mono font-semibold tracking-tight relative z-10 ${colorClass}`}>
        {value}
      </span>
    </div>
  );
}
