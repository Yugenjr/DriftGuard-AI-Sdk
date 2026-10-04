'use client';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Hero() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setStep((s) => (s + 1) % 6);
    }, 2500);
    return () => clearInterval(timer);
  }, []);

  const state = {
    0: { d: 0.08, s: 'HEALTHY', v: '1.0.4' },
    1: { d: 0.16, s: 'WARNING', v: '1.0.4' },
    2: { d: 0.31, s: 'DRIFT DETECTED', v: '1.0.4' },
    3: { d: 0.31, s: 'RETRAINING RUNNING', v: '1.0.4' },
    4: { d: 0.31, s: 'VERSION 1.0.5 VALIDATED', v: '1.0.5' },
    5: { d: 0.02, s: 'HEALTHY', v: '1.0.5' }
  }[step] as any;

  return (
    <section className="pt-32 pb-16 px-6 lg:px-12 w-full mx-auto flex flex-col xl:flex-row justify-center items-center gap-12 xl:gap-24 relative min-h-[85vh]">
      <div className="absolute top-24 left-12 text-2xl font-mono text-gray-300 opacity-50">+</div>
      <div className="absolute top-24 right-12 text-2xl font-mono text-gray-300 opacity-50">+</div>
      <div className="absolute bottom-12 left-12 text-2xl font-mono text-gray-300 opacity-50">+</div>
      <div className="absolute bottom-12 right-12 text-2xl font-mono text-gray-300 opacity-50">+</div>
      
      <div className="flex flex-col space-y-6 relative z-10 w-full max-w-[550px]">
        <div className="flex items-center space-x-3">
          <span className="font-mono text-xs font-bold uppercase tracking-widest bg-black text-white px-2 py-1 brutal-shadow-sm">INIT_SEQ_01</span>
          <span className="font-mono text-xs font-bold uppercase tracking-widest border-2 border-black bg-white px-2 py-0.5 text-gray-500">v1.0.7</span>
        </div>
        <h1 className="text-3xl md:text-4xl lg:text-5xl xl:text-[5rem] text-heading leading-[0.9] tracking-tighter">
          MODEL DRIFT<br/>IS NOT AN IF.
          <span className="block mt-4 text-[#ef4444]">IT'S A WHEN.</span>
        </h1>
        <p className="text-xl md:text-2xl font-medium max-w-2xl border-l-4 border-[#111] pl-6 py-2">
          DriftGuard continuously monitors production ML models, detects behavioral change, and triggers configurable retraining workflows before silent degradation becomes an operational problem.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 pt-4">
          <Link href="#docs" className="bg-[#111] text-[#a3e635] px-8 py-3 font-black text-center brutal-border brutal-shadow brutal-shadow-hover brutal-shadow-active text-sm uppercase transition-all tracking-widest">
            Get Started
          </Link>
          <a href="https://github.com/Yugenjr/DriftGuard-AI-Sdk" target="_blank" rel="noopener noreferrer" className="bg-white text-[#111] brutal-border px-8 py-3 font-black text-center brutal-shadow brutal-shadow-hover brutal-shadow-active text-sm uppercase transition-all tracking-widest">
            View GitHub
          </a>
        </div>
        <div className="font-mono text-xs text-gray-400 uppercase tracking-widest mt-6">
          // DEPENDENCIES: PYTHON 3.8+ /// FASTAPI /// NEXT.JS
        </div>
      </div>
      
      <div className="relative mt-12 xl:mt-0 w-full max-w-[550px] flex items-center">
        <div className="absolute -top-4 -right-4 bg-[#a3e635] brutal-border px-3 py-1 z-20 font-mono text-xs font-bold rotate-6 shadow-[4px_4px_0px_0px_#111]">
          INTERACTIVE DEMO
        </div>
        <div className="absolute -left-6 -bottom-6 w-full h-full border-l-4 border-b-4 border-black opacity-10"></div>
        <div className="brutal-card p-6 md:p-8 font-mono text-xs sm:text-sm flex flex-col space-y-4 bg-white relative z-10 w-full shadow-[8px_8px_0px_0px_#111]">
          <div className="border-b-3 border-black pb-3 flex justify-between items-center">
            <span className="font-black bg-black text-white px-2 py-0.5">MODEL HEALTH</span>
            <span className="font-bold">FRAUD-DETECTOR-V1</span>
          </div>
          <div className="grid grid-cols-2 gap-y-3 pt-2">
            <div className="font-bold text-gray-500">STATUS</div>
            <div className={`${state.s === 'HEALTHY' ? 'text-green-600' : state.s === 'WARNING' ? 'text-orange-600' : 'text-red-600'} font-black bg-gray-100 px-2 py-0.5 inline-block w-max border border-gray-300`}>{state.s}</div>
            <div className="font-bold text-gray-500">VERSION</div>
            <div className="font-bold">{state.v}</div>
            <div className="font-bold text-gray-500">ACCURACY</div>
            <div className="font-bold">{step < 3 ? '96.49%' : step === 3 ? 'CALCULATING' : '97.21%'}</div>
            <div className="font-bold text-gray-500">DRIFT SCORE</div>
            <div className="font-black text-xl">{state.d.toFixed(2)}</div>
            <div className="font-bold text-gray-500">THRESHOLD</div>
            <div className="font-bold text-gray-400">0.15</div>
            <div className="font-bold text-gray-500">LATENCY</div>
            <div className="font-bold">42ms</div>
          </div>
          <div className="pt-4 border-t-3 border-black">
            <div className="mb-2 font-bold flex justify-between">
              <span>TELEMETRY STREAM</span>
              <span className="text-[10px] text-gray-400">LIVE</span>
            </div>
            <div className="w-full bg-gray-200 h-8 brutal-border relative overflow-hidden">
              <motion.div 
                className="h-full bg-black" 
                initial={{ width: '0%' }}
                animate={{ width: `${Math.min((state.d / 0.15) * 50, 100)}%` }}
                transition={{ duration: 0.5 }}
              />
              {step >= 2 && step <= 4 && (
                <div className="absolute inset-0 bg-[#ef4444]/90 flex items-center justify-center font-black text-white text-sm brutal-border border-t-0 border-b-0 tracking-widest">⚠ DRIFT BREACH</div>
              )}
            </div>
          </div>
          <div className="flex justify-between items-end pt-4 opacity-70 text-xs font-bold">
            <div>LAST CHECK: 10:45:03 UTC</div>
            <div>● MONITORING</div>
          </div>
        </div>
      </div>
    </section>
  );
}
