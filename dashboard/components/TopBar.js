import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { RefreshCw, User } from 'lucide-react';
import { getMe } from '../lib/api';

export default function TopBar({ onRefresh, lastUpdated, isRefreshing }) {
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await getMe();
        setUser(data);
      } catch (err) {
        console.error("Failed to load user in top bar:", err);
      }
    }
    loadUser();
  }, []);

  const getPageTitle = () => {
    const { pathname, query } = router;
    if (pathname === '/dashboard') return 'Fleet Overview';
    if (pathname.startsWith('/models/')) return `Model Details > ${query.id || ''}`;
    return 'DriftGuard Console';
  };

  const formatLastUpdated = () => {
    if (!lastUpdated) return 'Never';
    const hours = String(lastUpdated.getHours()).padStart(2, '0');
    const minutes = String(lastUpdated.getMinutes()).padStart(2, '0');
    const seconds = String(lastUpdated.getSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
  };

  return (
    <header className="h-14 border-b border-white/10 bg-[#09090b]/80 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      {/* Left: Breadcrumbs Page Title */}
      <div className="flex items-center space-x-2 text-[13px]">
        <span className="text-[#a1a1aa] font-medium tracking-tight">Console</span>
        <span className="text-[#3f3f46]">/</span>
        <h2 className="font-semibold text-[#ededed] tracking-tight">{getPageTitle()}</h2>
      </div>

      {/* Right: Sync Status and User Profile */}
      <div className="flex items-center space-x-5">
        {onRefresh ? (
          <div className="flex items-center space-x-3">
            <span className="text-[11px] text-[#71717a] font-mono tracking-tight">Last sync: {formatLastUpdated()}</span>
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="p-1.5 rounded-md hover:bg-white/5 text-[#a1a1aa] hover:text-[#ededed] transition-colors cursor-pointer active:scale-95 disabled:opacity-50 group"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
            </button>
          </div>
        ) : null}
        
        <div className="h-4 w-[1px] bg-white/10" />
        
        <div className="flex items-center space-x-2 px-2 py-1 rounded-md hover:bg-white/5 transition-colors cursor-pointer">
          <div className="w-5 h-5 rounded-full bg-white/10 border border-white/5 flex items-center justify-center">
            <User className="w-3 h-3 text-[#ededed]" />
          </div>
          <span className="text-[13px] font-medium text-[#ededed] tracking-tight">{user ? user.name : 'Loading...'}</span>
        </div>
      </div>
    </header>
  );
}
