export default function TechStrip() {
  const techs = ["PYTHON SDK", "SCIKIT-LEARN", "PYTORCH", "HUGGING FACE", "FASTAPI", "PROMETHEUS", "GRAFANA", "MLFLOW", "AWS S3"];
  return (
    <div className="w-full border-y-3 border-black bg-white py-3 overflow-hidden flex whitespace-nowrap shadow-[0px_4px_0px_0px_#111]">
      <div className="flex animate-marquee space-x-12 px-12 w-max">
        {[...techs, ...techs, ...techs, ...techs, ...techs, ...techs, ...techs, ...techs].map((tech, i) => (
          <div key={i} className="flex items-center space-x-4">
            <span className="w-1.5 h-1.5 bg-black rounded-full"></span>
            <span className="font-mono font-black text-xs tracking-widest uppercase">
              {tech}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
