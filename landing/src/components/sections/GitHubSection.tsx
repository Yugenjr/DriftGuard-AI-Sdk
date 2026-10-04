import ScrollReveal from '../layout/ScrollReveal';
export default function GitHubSection() {
  return (
    <ScrollReveal className="py-16 px-6 lg:px-12 bg-[#a3e635] text-[#111] text-center relative overflow-hidden brutal-border border-l-0 border-r-0 border-t-0">
      {/* Decorative grid pattern over lime */}
      <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'linear-gradient(to right, #111 1px, transparent 1px), linear-gradient(to bottom, #111 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
      
      <div className="max-w-[2000px] xl:px-24 mx-auto relative z-10">
        <h2 className="text-4xl md:text-5xl lg:text-7xl text-heading mb-10 tracking-tighter leading-[0.9]">
          DRIFTGUARD<br/>IS BUILT TO BE<br/><span className="bg-white px-4 border-4 border-[#111] shadow-[8px_8px_0px_0px_#111] inline-block mt-4">INSPECTED.</span>
        </h2>
        <div className="flex flex-col items-center justify-center space-y-6 mt-16">
          <div className="font-mono text-lg md:text-xl mb-6 bg-white text-black p-4 border-3 border-[#111] inline-block font-black shadow-[6px_6px_0px_0px_#111]">
            pip install driftguard-ai-sdk
          </div>
          <div className="flex flex-col sm:flex-row gap-4">
            <a href="https://github.com/Yugenjr/DriftGuard-AI-Sdk" target="_blank" rel="noopener noreferrer" className="bg-[#111] text-white border-3 border-black px-8 py-3 font-black text-sm md:text-base shadow-[6px_6px_0px_0px_rgba(255,255,255,1)] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] uppercase transition-all tracking-widest">
              VIEW SOURCE →
            </a>
            <a href="https://pypi.org/project/driftguard-ai-sdk/" target="_blank" rel="noopener noreferrer" className="bg-white text-black border-3 border-black px-8 py-3 font-black text-sm md:text-base shadow-[6px_6px_0px_0px_#111] hover:translate-x-[-2px] hover:translate-y-[-2px] hover:shadow-[8px_8px_0px_0px_#111] uppercase transition-all tracking-widest">
              PyPI
            </a>
          </div>
          <div className="font-mono text-[10px] md:text-xs font-black text-[#111] mt-12 flex flex-wrap justify-center gap-3 max-w-2xl">
            <span className="border-2 border-[#111] bg-white px-2 py-1 shadow-[2px_2px_0px_0px_#111]">PRODUCTION VALIDATION</span>
            <span className="border-2 border-[#111] bg-white px-2 py-1 shadow-[2px_2px_0px_0px_#111]">SDK</span>
            <span className="border-2 border-[#111] bg-white px-2 py-1 shadow-[2px_2px_0px_0px_#111]">MODEL REGISTRY</span>
            <span className="border-2 border-[#111] bg-white px-2 py-1 shadow-[2px_2px_0px_0px_#111]">DRIFT DETECTION</span>
            <span className="border-2 border-[#111] bg-white px-2 py-1 shadow-[2px_2px_0px_0px_#111]">RETRAINING</span>
          </div>
        </div>
      </div>
    </ScrollReveal>
  );
}
