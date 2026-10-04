import ScrollReveal from '../layout/ScrollReveal';
export default function Timeline() {
  const events = [
    { time: "10:41:02", msg: "PREDICTION TELEMETRY RECEIVED" },
    { time: "10:43:17", msg: "DRIFT SCORE > THRESHOLD", alert: true },
    { time: "10:43:18", msg: "RETRAINING REQUEST CREATED" },
    { time: "10:44:02", msg: "TRAINING PIPELINE STARTED" },
    { time: "10:44:51", msg: "MODEL VALIDATION PASSED", success: true },
    { time: "10:45:03", msg: "MODEL VERSION 1.0.5 READY" },
    { time: "10:45:11", msg: "DEPLOYMENT UPDATED", success: true }
  ];
  return (
    <ScrollReveal className="py-16 px-6 lg:px-12 bg-[#F4F1EA] max-w-[1200px] mx-auto">
      <div className="font-mono text-[10px] font-bold text-gray-400 mb-4 border-b border-gray-300 pb-2 inline-block text-center w-full">SECTION 07 // EVENT LOG</div>
      <h2 className="text-4xl md:text-5xl text-heading mb-10 text-center tracking-tighter">EVENT STREAM</h2>
      <div className="brutal-card p-6 md:p-8 bg-white font-mono text-sm space-y-4">
        {events.map((e, i) => (
          <div key={i} className={`flex flex-col sm:flex-row sm:items-center space-y-1 sm:space-y-0 sm:space-x-6 border-b-2 border-dashed border-gray-200 pb-3 ${e.alert ? 'text-[#ef4444] font-black' : e.success ? 'text-black bg-[#a3e635] px-2 py-0.5 font-black inline-block' : 'font-bold text-gray-600'}`}>
            <div className="w-24 shrink-0 tracking-widest text-xs opacity-70">{e.time}</div>
            <div className="tracking-tight">{e.msg}</div>
          </div>
        ))}
      </div>
    </ScrollReveal>
  );
}
