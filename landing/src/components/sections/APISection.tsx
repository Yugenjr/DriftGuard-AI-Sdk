import ScrollReveal from '../layout/ScrollReveal';
export default function APISection() {
  return (
    <ScrollReveal className="py-16 px-6 lg:px-12 bg-white brutal-border border-l-0 border-r-0" id="docs">
      <div className="max-w-[2000px] xl:px-24 mx-auto grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <div className="font-mono text-[10px] font-bold text-gray-400 mb-4 border-b border-gray-300 pb-2 inline-block">SECTION 06 // API</div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl text-heading mb-6 tracking-tighter">API-FIRST DESIGN.</h2>
          <p className="text-lg font-medium mb-10 max-w-xl">Every action in DriftGuard is accessible via a REST API. Integrate monitoring triggers into your existing infrastructure seamlessly.</p>
          <button className="bg-[#111] text-[#a3e635] px-6 py-3 font-black brutal-border brutal-shadow-sm brutal-shadow-hover brutal-shadow-active text-sm uppercase transition-all tracking-widest">
            View API Docs →
          </button>
        </div>
        <div className="border-3 border-black p-6 bg-[#111] text-white font-mono text-sm space-y-4 shadow-[6px_6px_0px_0px_#a3e635]">
          <div className="flex flex-col sm:flex-row sm:space-x-4 border-b border-gray-800 pb-3">
            <span className="text-[#a3e635] font-black w-14">POST</span>
            <span>/models/register</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:space-x-4 border-b border-gray-800 pb-3">
            <span className="text-[#a3e635] font-black w-14">POST</span>
            <span>/predict/&#123;model_id&#125;</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:space-x-4 border-b border-gray-800 pb-3">
            <span className="text-blue-400 font-black w-14">GET</span>
            <span>/drift/&#123;model_id&#125;</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:space-x-4 border-b border-gray-800 pb-3">
            <span className="text-[#a3e635] font-black w-14">POST</span>
            <span>/retrain/&#123;model_id&#125;</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:space-x-4 border-b border-gray-800 pb-3">
            <span className="text-blue-400 font-black w-14">GET</span>
            <span>/metrics</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:space-x-4">
            <span className="text-blue-400 font-black w-14">GET</span>
            <span>/models</span>
          </div>
        </div>
      </div>
    </ScrollReveal>
  );
}
