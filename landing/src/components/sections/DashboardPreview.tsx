import ScrollReveal from '../layout/ScrollReveal';
export default function DashboardPreview() {
  return (
    <ScrollReveal className="py-16 px-6 lg:px-12 max-w-[2000px] xl:px-24 mx-auto relative">
      <div className="font-mono text-[10px] font-bold text-gray-400 mb-4 border-b border-gray-300 pb-2 inline-block">SECTION 05 // VISIBILITY</div>
      <h2 className="text-3xl md:text-4xl lg:text-5xl text-heading mb-12 tracking-tighter">OBSERVABILITY<br/>DASHBOARD.</h2>
      
      <div className="brutal-border p-4 md:p-6 bg-[#111] flex flex-col space-y-4 shadow-[8px_8px_0px_0px_#a3e635]">
        <div className="flex justify-between items-center border-b-3 border-gray-700 pb-3">
          <div className="font-black text-xl md:text-2xl tracking-tighter text-white">DRIFTGUARD CONSOLE</div>
          <div className="font-mono text-[10px] md:text-xs bg-[#a3e635] text-black px-2 py-1 font-black tracking-widest">[ SYS.ONLINE ]</div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
          <div className="border-3 border-black p-3 bg-white shadow-[4px_4px_0px_0px_#F4F1EA]">
            <div className="text-[10px] font-bold mb-1 text-gray-500">MODEL HEALTH</div>
            <div className="text-2xl lg:text-3xl font-black text-[#a3e635]">96.49%</div>
          </div>
          <div className="border-3 border-black p-3 bg-white shadow-[4px_4px_0px_0px_#F4F1EA]">
            <div className="text-[10px] font-bold mb-1 text-gray-500">DRIFT SCORE</div>
            <div className="text-2xl lg:text-3xl font-black text-orange-500">0.08</div>
          </div>
          <div className="border-3 border-black p-3 bg-white shadow-[4px_4px_0px_0px_#F4F1EA]">
            <div className="text-[10px] font-bold mb-1 text-gray-500">LATENCY</div>
            <div className="text-2xl lg:text-3xl font-black">42ms</div>
          </div>
          <div className="border-3 border-black p-3 bg-white shadow-[4px_4px_0px_0px_#F4F1EA]">
            <div className="text-[10px] font-bold mb-1 text-gray-500">MODEL VERSION</div>
            <div className="text-2xl lg:text-3xl font-black">1.0.4</div>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-4 pt-2">
          <div className="md:col-span-2 border-3 border-black p-4 bg-[#F4F1EA] h-64 flex flex-col shadow-[4px_4px_0px_0px_#F4F1EA]">
            <div className="text-xs font-black mb-4 font-mono border-b-2 border-black pb-2 flex justify-between">
              <span>DRIFT OVER TIME</span>
              <span className="text-gray-500">LIMIT: 0.15</span>
            </div>
            {/* CSS Bar Chart to replace the weird SVG line graph */}
            <div className="flex-1 border-l-3 border-b-3 border-black flex items-end justify-between px-2 pt-4 space-x-1 relative">
              <div className="absolute top-[30%] left-0 w-full border-t-2 border-dashed border-orange-500 z-0"></div>
              {[40, 45, 30, 50, 60, 45, 55, 75, 95, 80, 50, 40, 30].map((h, i) => (
                <div key={i} className={`w-full border-2 border-black z-10 ${h > 70 ? 'bg-red-500' : 'bg-[#111]'}`} style={{ height: `${h}%` }}></div>
              ))}
            </div>
          </div>
          
          <div className="border-3 border-black p-4 bg-white h-64 font-mono text-xs flex flex-col shadow-[4px_4px_0px_0px_#F4F1EA]">
            <div className="text-xs font-black mb-4 border-b-2 border-black pb-2">DEPLOYMENT STATE</div>
            <div className="flex-1 flex flex-col justify-start space-y-4 pt-2">
              <div className="flex justify-between border-b border-dashed border-gray-300 pb-1">
                <span className="font-bold text-gray-500">STAGE</span><span className="bg-[#a3e635] border-2 border-black px-1 py-0.5 font-black text-black text-[10px]">CHAMPION</span>
              </div>
              <div className="flex justify-between border-b border-dashed border-gray-300 pb-1">
                <span className="font-bold text-gray-500">RETRAINING</span><span className="font-bold text-[10px]">NO ACTIVE JOB</span>
              </div>
              <div className="flex justify-between border-b border-dashed border-gray-300 pb-1">
                <span className="font-bold text-gray-500">REGION</span><span className="font-bold text-[10px]">AWS</span>
              </div>
              <div className="flex justify-between pb-1">
                <span className="font-bold text-gray-500">LAST EVENT</span><span className="font-bold text-[10px]">10:45:03</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ScrollReveal>
  );
}
