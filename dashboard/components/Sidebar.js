import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { LayoutDashboard, Activity, Settings, LogOut, BookOpen, ChevronDown } from 'lucide-react';
import { getMe, createProject } from '../lib/api';
import { useProject } from '../context/ProjectContext';

export default function Sidebar({ activeModelCount }) {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const { projects, activeProject, selectProject, reloadProjects } = useProject();
  const [isProjectMenuOpen, setIsProjectMenuOpen] = useState(false);

  useEffect(() => {
    async function loadUser() {
      try {
        const data = await getMe();
        setUser(data);
      } catch (err) {
        console.error("Failed to load user in sidebar:", err);
      }
    }
    loadUser();
  }, []);

  const handleSignOut = () => {
    localStorage.removeItem("dg_api_key");
    router.replace("/login");
  };

  const navItems = [
    { label: 'Fleet Overview', icon: LayoutDashboard, path: '/dashboard', isActive: (p) => p === '/dashboard' },
    { label: 'Model Metrics', icon: Activity, path: '#', badge: activeModelCount, isActive: (p) => p.startsWith('/models/') },
    { label: 'Documentation', icon: BookOpen, path: '/docs', isActive: (p) => p.startsWith('/docs') },
    { label: 'System Settings', icon: Settings, path: '/settings', isActive: (p) => p.startsWith('/settings') }
  ];

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  };

  const handleCreateProject = async () => {
    const name = prompt("Enter new project name:");
    if (name) {
      try {
        const p = await createProject(name);
        await reloadProjects();
        selectProject(p);
        setIsProjectMenuOpen(false);
      } catch (e) {
        alert(e.message || "Failed to create project");
      }
    }
  };

  return (
    <div className="w-[240px] bg-[#18181b] border-r border-white/10 flex flex-col justify-between h-screen sticky top-0 font-sans">
      <div>
        {/* Brand Header */}
        <div className="px-6 py-6 border-b border-white/10 flex items-center space-x-3 bg-gradient-to-b from-[#161616] to-[#111111]">
          <span className="text-xl">🛡️</span>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-[#ededed]">DRIFTGUARD</h1>
            <span className="text-[9px] text-[#a1a1aa] uppercase tracking-widest font-medium">Self-Healing MLOps</span>
          </div>
        </div>

        {/* Project Selector */}
        <div className="px-4 py-3 border-b border-white/10 relative">
          <button 
            onClick={() => setIsProjectMenuOpen(!isProjectMenuOpen)}
            className="w-full flex items-center justify-between px-3 py-2 bg-[#09090b] rounded-lg border border-white/5 hover:border-white/10 text-xs text-[#ededed] font-medium"
          >
            <span className="truncate">{activeProject ? activeProject.name : 'Loading Projects...'}</span>
            <ChevronDown className="w-3.5 h-3.5 text-[#a1a1aa]" />
          </button>
          
          {isProjectMenuOpen && (
            <div className="absolute top-[52px] left-4 right-4 bg-[#18181b] border border-white/10 rounded-lg shadow-xl z-50 overflow-hidden">
              <div className="max-h-48 overflow-y-auto">
                {projects.map(p => (
                  <button
                    key={p.id}
                    onClick={() => { selectProject(p); setIsProjectMenuOpen(false); }}
                    className={`w-full text-left px-3 py-2 text-xs hover:bg-white/5 ${activeProject?.id === p.id ? 'text-[#24b47e]' : 'text-[#a1a1aa]'}`}
                  >
                    {p.name}
                  </button>
                ))}
              </div>
              <div className="border-t border-white/10">
                <button
                  onClick={handleCreateProject}
                  className="w-full text-left px-3 py-2 text-xs text-[#ededed] hover:bg-white/5 font-medium"
                >
                  + New Project
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Section */}
        <nav className="mt-4 px-3 space-y-1">
          {navItems.map((item, idx) => {
            const Icon = item.icon;
            const isActive = item.isActive(router.pathname);
            return (
              <button
                key={idx}
                onClick={() => item.path !== '#' && router.push(item.path)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-[13px] font-medium tracking-wide transition-all group ${
                  isActive
                    ? 'bg-[#18181b] text-[#ededed] border border-white/10 shadow-sm'
                    : 'text-[#a1a1aa] hover:text-[#ededed] hover:bg-[#18181b]/60 border border-transparent'
                }`}
              >
                <div className="flex items-center space-x-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#24b47e]' : 'text-[#a1a1aa] group-hover:text-[#ededed]'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && item.badge > 0 ? (
                  <span className="px-1.5 py-0.5 rounded-xl text-[10px] bg-[#24b47e]/10 text-[#24b47e] border border-[#24b47e]/30 font-semibold">
                    {item.badge}
                  </span>
                ) : null}
              </button>
            );
          })}
        </nav>
      </div>

      {/* User Footer Profile */}
      <div className="p-4 border-t border-white/10 bg-[#09090b]/40 flex flex-col space-y-4">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-[#2e2e2e] border border-[#404040] flex items-center justify-center text-[11px] font-bold text-[#ededed]">
            {user ? getInitials(user.name) : 'DG'}
          </div>
          <div className="flex-1 min-w-0">
            <span className="block text-xs font-semibold text-[#ededed] truncate">
              {user ? user.name : 'DriftGuard User'}
            </span>
            <span className="block text-[10px] text-[#a1a1aa] truncate">
              {user ? user.email : 'loading...'}
            </span>
          </div>
        </div>
        <button
          onClick={handleSignOut}
          className="w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-xl bg-[#09090b] border border-white/10 hover:bg-[#18181b] hover:text-[#ededed] hover:border-[#404040] text-xs font-medium text-[#a1a1aa] transition-all"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
}
