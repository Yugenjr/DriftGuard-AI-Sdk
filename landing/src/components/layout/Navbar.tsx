'use client';
import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import Link from 'next/link';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const links = [
    { name: 'PRODUCT', href: '#product' },
    { name: 'HOW IT WORKS', href: '#how-it-works' },
    { name: 'SDK', href: '#sdk' },
    { name: 'ARCHITECTURE', href: '#architecture' },
    { name: 'GITHUB', href: 'https://github.com/Yugenjr/DriftGuard-AI-Sdk' }
  ];

  return (
    <nav className="fixed top-0 w-full z-50 bg-[#F4F1EA] border-b-4 border-black transition-all">
      <div className="flex justify-between items-center h-20 px-6 lg:px-12 xl:px-24 w-full max-w-[2000px] mx-auto">
        
        <Link href="/" className="text-3xl lg:text-4xl font-black tracking-tighter transition-colors">
          DRIFTGUARD
        </Link>
        
        <div className="hidden lg:flex items-center space-x-8 xl:space-x-12">
          {links.map((l) => (
            <a key={l.name} href={l.href} className="text-sm font-black uppercase tracking-widest hover:underline decoration-[3px] underline-offset-8 transition-colors">
              {l.name}
            </a>
          ))}
        </div>
        
        <div className="hidden lg:flex items-center space-x-6">
          <div className="flex items-center space-x-2 border-2 border-black px-3 py-1 bg-white brutal-shadow-sm">
            <span className="w-2 h-2 bg-[#a3e635] rounded-full animate-pulse border border-black"></span>
            <span className="font-mono text-[10px] font-black uppercase tracking-widest">v1.0.7</span>
          </div>
          <Link href="#docs" className="bg-[#111] text-[#a3e635] px-6 py-2.5 font-black hover:bg-[#a3e635] hover:text-[#111] border-2 border-black shadow-[4px_4px_0px_0px_#111] hover:shadow-[6px_6px_0px_0px_#111] hover:-translate-y-0.5 transition-all uppercase tracking-widest text-sm">
            GET STARTED
          </Link>
        </div>
        
        <div className="lg:hidden flex items-center">
          <button onClick={() => setIsOpen(!isOpen)} className="text-[#111]">
            {isOpen ? <X size={32} strokeWidth={3} /> : <Menu size={32} strokeWidth={3} />}
          </button>
        </div>
      </div>
      
      {isOpen && (
        <div className="lg:hidden bg-white brutal-border border-t-4 border-r-0 border-l-0 border-b-0 flex flex-col shadow-2xl">
          {links.map((l) => (
            <a key={l.name} href={l.href} onClick={() => setIsOpen(false)} className="px-8 py-5 text-base font-black border-b-2 border-black hover:bg-[#a3e635] uppercase tracking-widest">
              {l.name}
            </a>
          ))}
          <Link href="#docs" onClick={() => setIsOpen(false)} className="px-8 py-5 text-base font-black border-b-2 border-black bg-[#111] text-[#a3e635] uppercase tracking-widest">
            GET STARTED
          </Link>
        </div>
      )}
    </nav>
  );
}
