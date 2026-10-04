import ScrollReveal from '../layout/ScrollReveal';
export default function SDKSection() {
  return (
    <ScrollReveal className="py-16 px-6 lg:px-12 max-w-[2000px] xl:px-24 mx-auto" id="sdk">
      <div className="font-mono text-[10px] font-bold text-gray-400 mb-4 border-b border-gray-300 pb-2 inline-block">SECTION 03 // INTEGRATION</div>
      
      <div className="grid lg:grid-cols-2 gap-12 items-start">
        <div>
          <h2 className="text-3xl md:text-4xl lg:text-5xl text-heading mb-6 leading-[0.9] tracking-tighter">
            INTEGRATE IN MINUTES.<br/>
            <span className="bg-[#a3e635] px-2 mt-2 inline-block border-2 border-black">NOT IN A MIGRATION PROJECT.</span>
          </h2>
          <p className="text-lg font-medium mb-10 mt-6 max-w-xl">
            Keep your inference code. Add model intelligence around it. 
            DriftGuard wraps your existing model and automatically handles telemetry streaming and drift monitoring asynchronously.
          </p>
          <div className="space-y-4 font-mono font-bold text-sm">
            <div className="flex items-center space-x-4 border-b border-gray-300 pb-3">
              <div className="bg-[#111] text-white w-8 h-8 flex items-center justify-center brutal-shadow-sm">1</div>
              <div>Install SDK</div>
            </div>
            <div className="flex items-center space-x-4 border-b border-gray-300 pb-3">
              <div className="bg-[#111] text-white w-8 h-8 flex items-center justify-center brutal-shadow-sm">2</div>
              <div>Initialize DriftGuard</div>
            </div>
            <div className="flex items-center space-x-4 border-b border-gray-300 pb-3">
              <div className="bg-[#111] text-white w-8 h-8 flex items-center justify-center brutal-shadow-sm">3</div>
              <div>Wrap the existing model</div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="bg-[#111] text-white w-8 h-8 flex items-center justify-center brutal-shadow-sm">4</div>
              <div>Continue using model.predict()</div>
            </div>
          </div>
        </div>
        
        <div className="bg-[#111] p-6 brutal-border shadow-[8px_8px_0px_0px_#a3e635] relative text-[#F4F1EA] font-mono text-xs sm:text-sm overflow-x-auto w-full">
          <div className="absolute top-0 left-0 bg-[#a3e635] text-black px-3 py-1 border-b-3 border-r-3 border-black font-black text-[10px] uppercase tracking-widest">PYTHON EXAMPLE</div>
          <pre className="pt-8 whitespace-pre-wrap">
<span className="text-gray-500"># Install via pip</span>{"\n"}
<span className="text-gray-500"># pip install driftguard-ai-sdk</span>{"\n\n"}
<span className="text-pink-400">from</span> driftguard <span className="text-pink-400">import</span> DriftGuard{"\n\n"}
<span className="text-gray-500"># Initialize client</span>{"\n"}
dg = DriftGuard({"\n"}
    model_id=<span className="text-[#a3e635]">"fraud-detector-v1"</span>,{"\n"}
    api_url=<span className="text-[#a3e635]">"https://YOUR-DRIFTGUARD-API"</span>,{"\n"}
    api_key=<span className="text-[#a3e635]">"YOUR_API_KEY"</span>,{"\n"}
    drift_threshold=<span className="text-[#60a5fa]">0.15</span>,{"\n"}
    auto_retrain=<span className="text-[#60a5fa]">True</span>{"\n"}
){"\n\n"}
<span className="text-gray-500"># Wrap your existing model (Scikit-learn, etc)</span>{"\n"}
model = dg.wrap(trained_model){"\n\n"}
<span className="text-gray-500"># Business as usual</span>{"\n"}
prediction = model.predict(features)
          </pre>
        </div>
      </div>
      
      <div className="mt-20 border-t-3 border-black pt-12 grid lg:grid-cols-2 gap-8 items-stretch">
        <div className="brutal-card p-6 bg-gray-200 opacity-70 grayscale relative overflow-hidden">
          <div className="font-black text-xl mb-6 uppercase tracking-tight">Without DriftGuard</div>
          <div className="font-mono font-bold space-y-3 text-xs">
            <div className="bg-white p-2 border-2 border-black">model.predict(X)</div>
            <div className="text-center text-gray-500">+</div>
            <div className="bg-white p-2 border-2 border-black border-dashed text-gray-600">custom telemetry logic</div>
            <div className="text-center text-gray-500">+</div>
            <div className="bg-white p-2 border-2 border-black border-dashed text-gray-600">custom drift math</div>
            <div className="text-center text-gray-500">+</div>
            <div className="bg-white p-2 border-2 border-black border-dashed text-gray-600">custom alerting/webhooks</div>
            <div className="text-center text-gray-500">+</div>
            <div className="bg-white p-2 border-2 border-black border-dashed text-gray-600">custom retraining triggers</div>
          </div>
        </div>
        
        <div className="brutal-card p-6 bg-[#a3e635] flex flex-col justify-center">
          <div className="font-black text-xl mb-6 uppercase tracking-tight">With DriftGuard</div>
          <div className="font-mono font-bold space-y-4 text-sm">
            <div className="bg-white p-4 border-3 border-black shadow-[4px_4px_0px_0px_#111]">model = dg.wrap(model)</div>
            <div className="text-center text-2xl font-black">↓</div>
            <div className="bg-white p-4 border-3 border-black shadow-[4px_4px_0px_0px_#111]">model.predict(X)</div>
          </div>
          <p className="mt-8 text-sm font-black text-center uppercase tracking-widest border-t-2 border-black pt-4">Keep your inference code.<br/>Add model intelligence around it.</p>
        </div>
      </div>
    </ScrollReveal>
  );
}
