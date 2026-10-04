import ScrollReveal from '../layout/ScrollReveal';
export default function Problem() {
  return (
    <ScrollReveal className="py-16 px-6 lg:px-12 max-w-[2000px] xl:px-24 mx-auto relative" id="product">
      <div className="absolute top-0 right-12 w-px h-24 bg-black opacity-20"></div>
      <div className="font-mono text-[10px] font-bold text-gray-400 mb-4 border-b border-gray-300 pb-2 inline-block">SECTION 01 // THE PROBLEM</div>
      
      <h2 className="text-3xl md:text-4xl lg:text-5xl text-heading mb-10 tracking-tighter">
        YOUR MODEL DIDN'T FAIL<br/>WHEN YOU DEPLOYED IT.<br/>
        <span className="text-gray-400">IT FAILED LATER.</span>
      </h2>
      <div className="grid lg:grid-cols-2 gap-10 mb-16 items-start">
        <p className="text-lg md:text-xl font-medium leading-relaxed max-w-2xl">
          Production ML models operate in changing environments. Input distributions shift. User behavior changes. Relationships between features and outcomes change. Performance degrades silently.
        </p>
        <p className="text-base md:text-lg font-mono font-bold leading-relaxed bg-[#111] text-[#F4F1EA] p-6 brutal-shadow-active brutal-border shadow-[6px_6px_0px_0px_#a3e635]">
          Traditional deployment pipelines do not automatically mean the model remains healthy forever. Deployment is a starting point, not a health check.
        </p>
      </div>
      <div className="grid md:grid-cols-3 gap-6">
        {[
          { num: "01", title: "DATA CHANGES", desc: "Real-world data naturally drifts away from historical training sets." },
          { num: "02", title: "MODEL BEHAVIOR", desc: "The relationship between inputs and targets fundamentally shifts over time." },
          { num: "03", title: "PERFORMANCE DEGRADES", desc: "Business metrics plummet silently because the pipeline lacks observability." }
        ].map(card => (
          <div key={card.num} className="brutal-card p-6 flex flex-col h-full relative group hover:bg-[#a3e635] transition-colors">
            <span className="font-mono text-5xl font-black opacity-10 absolute top-4 right-4 group-hover:opacity-30 transition-opacity">{card.num}</span>
            <h3 className="text-xl font-black mb-3 mt-8 uppercase tracking-tight">{card.title}</h3>
            <p className="font-mono text-xs leading-relaxed font-bold text-gray-700 group-hover:text-black">{card.desc}</p>
          </div>
        ))}
      </div>
    </ScrollReveal>
  );
}
