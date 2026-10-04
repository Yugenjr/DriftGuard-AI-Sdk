import { ArrowRight, ArrowDown } from 'lucide-react';

import ScrollReveal from '../layout/ScrollReveal';
export default function HowItWorks() {
  const steps = ["TRAIN", "DEPLOY", "MONITOR", "DETECT DRIFT", "VALIDATE", "RETRAIN", "EVALUATE", "PROMOTE/ROLLBACK"];
  return (
    <ScrollReveal className="py-16 bg-[#111] text-[#F4F1EA] px-6 lg:px-12 border-y-4 border-black relative" id="how-it-works">
      {/* Decorative grid pattern over black */}
      <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
      
      <div className="max-w-[2000px] xl:px-24 mx-auto relative z-10">
        <div className="font-mono text-[10px] font-bold text-gray-500 mb-4 border-b border-gray-700 pb-2 inline-block">SECTION 02 // PIPELINE</div>
        <h2 className="text-3xl md:text-4xl lg:text-5xl text-heading mb-6 tracking-tighter">
          FROM PREDICTION<br/>TO RECOVERY.
        </h2>
        <p className="text-lg md:text-xl font-mono mb-16 border-l-4 border-[#a3e635] pl-6 max-w-3xl font-bold">
          The SDK captures prediction telemetry and DriftGuard evaluates model behavior autonomously.
        </p>
        <div className="flex flex-col lg:flex-row flex-wrap gap-4 items-center justify-start">
          {steps.map((step, i) => (
            <div key={step} className="flex flex-col lg:flex-row items-center">
              <div className="border-3 border-black px-4 py-3 font-black text-sm font-mono bg-[#a3e635] text-black shadow-[4px_4px_0px_0px_rgba(255,255,255,1)]">
                {i + 1}. {step}
              </div>
              {i < steps.length - 1 && (
                <div className="mx-4 hidden lg:block text-gray-500"><ArrowRight size={24} strokeWidth={4} /></div>
              )}
              {i < steps.length - 1 && (
                <div className="my-3 lg:hidden text-gray-500"><ArrowDown size={24} strokeWidth={4} /></div>
              )}
            </div>
          ))}
        </div>
      </div>
    </ScrollReveal>
  );
}
