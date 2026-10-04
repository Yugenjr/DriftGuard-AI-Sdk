import { ArrowRight } from 'lucide-react';

import ScrollReveal from '../layout/ScrollReveal';
export default function Architecture() {
  const blocks = [
    { name: "CUSTOMER APP", color: "bg-[#F4F1EA]", text: "text-black" },
    { name: "DRIFTGUARD SDK", color: "bg-[#a3e635]", text: "text-black" },
    { name: "FASTAPI CORE", color: "bg-[#111]", text: "text-white" },
    { name: "POSTGRES & REDIS", color: "bg-[#F4F1EA]", text: "text-black" },
    { name: "MODEL REGISTRY", color: "bg-[#f97316]", text: "text-white" },
    { name: "TELEMETRY ENGINE", color: "bg-[#111]", text: "text-white" },
    { name: "RETRAINING WORKFLOW", color: "bg-[#a3e635]", text: "text-black" },
    { name: "PROMETHEUS/GRAFANA", color: "bg-gray-300", text: "text-black" },
    { name: "AWS S3 / MLFLOW", color: "bg-gray-300", text: "text-black" },
  ];

  return (
    <ScrollReveal className="py-16 px-6 lg:px-12 bg-[#111] text-white brutal-border border-l-0 border-r-0 relative" id="architecture">
      {/* Decorative grid pattern over black */}
      <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
      
      <div className="max-w-[2000px] xl:px-24 mx-auto relative z-10">
        <div className="font-mono text-[10px] font-bold text-gray-400 mb-4 border-b border-gray-700 pb-2 inline-block">SECTION 04 // ARCHITECTURE</div>
        <h2 className="text-3xl md:text-4xl lg:text-5xl text-heading mb-16 tracking-tighter">UNDER THE HOOD.</h2>
        
        <div className="flex flex-wrap gap-4 items-center justify-start">
          {blocks.map((b, i) => (
            <div key={i} className="flex items-center my-2">
              <div className={`border-3 border-black px-6 py-4 font-black font-mono text-xs sm:text-sm shadow-[4px_4px_0px_0px_#F4F1EA] ${b.color} ${b.text}`}>
                {b.name}
              </div>
              {i < blocks.length - 1 && (
                <div className="mx-2 sm:mx-4 text-gray-500"><ArrowRight size={24} strokeWidth={3} /></div>
              )}
            </div>
          ))}
        </div>
      </div>
    </ScrollReveal>
  );
}
