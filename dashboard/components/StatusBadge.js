import React from 'react';
import { getStatusColor } from '../lib/utils';

export default function StatusBadge({ status }) {
  const colorClass = getStatusColor(status);
  return (
    <div className={`inline-flex items-center space-x-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium tracking-tight border bg-opacity-10 ${colorClass}`}>
      <span className="relative flex h-1.5 w-1.5">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-40"></span>
        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-current"></span>
      </span>
      <span className="capitalize">{status}</span>
    </div>
  );
}
