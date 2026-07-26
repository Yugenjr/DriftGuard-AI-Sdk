import React from 'react';
import { useRouter } from 'next/router';
import StatusBadge from './StatusBadge';
import { formatPercent, getAccuracyColor } from '../lib/utils';
import { Calendar, ArrowRight, Layers3 } from 'lucide-react';

export default function ModelCard({ model }) {
  const router = useRouter();

  const handleDetails = () => {
    router.push(`/models/${model.model_id}`);
  };

  const accuracyVal = model.accuracy !== undefined && model.accuracy !== null ? model.accuracy : 0.0;
  const accuracyColorClass = getAccuracyColor(accuracyVal);
  const formattedAccuracy = model.accuracy !== undefined && model.accuracy !== null ? formatPercent(model.accuracy) : "N/A";

  // Parse features list
  let features = [];
  try {
    if (typeof model.features === 'string') {
      features = JSON.parse(model.features);
    } else if (Array.isArray(model.features)) {
      features = model.features;
    }
  } catch (e) {
    features = [];
  }

  const shownFeatures = features.slice(0, 3);
  const remainingCount = features.length - 3;

  return (
    <div className="bg-[#121214] border border-white/10 hover:border-white/20 p-5 rounded-xl shadow-sm hover:shadow-md hover:-translate-y-[1px] flex flex-col justify-between space-y-5 transition-all duration-300 group">
      {/* Top row */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3 min-w-0">
          <span className="p-1.5 bg-white/5 rounded-md text-[#ededed] border border-white/5 group-hover:text-[#24b47e] transition-colors">
            <Layers3 className="w-4 h-4" />
          </span>
          <h3 className="text-[15px] font-semibold text-[#ededed] truncate tracking-tight" title={model.model_id}>
            {model.model_id}
          </h3>
        </div>
        <StatusBadge status={model.status !== null && model.status !== undefined ? model.status : 'N/A'} />
      </div>

      {/* Accuracy meter */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs font-medium text-[#a1a1aa]">
          <span>Champion Accuracy</span>
          <span className="text-[#ededed] font-mono tracking-tight">{formattedAccuracy}</span>
        </div>
        <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden border border-white/5">
          <div
            className={`h-full bg-current rounded-full transition-all duration-700 ease-out ${accuracyColorClass}`}
            style={{ width: `${Math.min(100, (accuracyVal > 1.0 ? accuracyVal : accuracyVal * 100))}%` }}
          />
        </div>
      </div>

      {/* Threshold & Features list */}
      <div className="space-y-3 pt-1">
        <div className="flex justify-between text-xs font-medium text-[#a1a1aa]">
          <span>Drift Threshold</span>
          <span className="text-[#a1a1aa] font-mono">{model.drift_threshold !== null && model.drift_threshold !== undefined ? model.drift_threshold.toFixed(2) : 'N/A'}</span>
        </div>
        {features.length > 0 && (
          <div className="flex flex-wrap gap-1.5 items-center">
            {shownFeatures.map((feat, idx) => (
              <span key={idx} className="px-2 py-0.5 text-[10px] font-mono rounded-md bg-white/5 border border-white/5 text-[#a1a1aa] tracking-tight">
                {feat}
              </span>
            ))}
            {remainingCount > 0 && (
              <span className="text-[10px] text-[#52525b] font-medium tracking-tight">
                +{remainingCount} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Footer Details action button */}
      <div className="flex items-center justify-between pt-4 border-t border-white/5 mt-auto">
        <div className="flex items-center text-[11px] text-[#a1a1aa] space-x-1.5 font-mono">
          <Calendar className="w-3.5 h-3.5 opacity-50" />
          <span>{model.version !== null && model.version !== undefined ? `v${model.version}` : 'N/A'}</span>
        </div>
        <button
          onClick={handleDetails}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-white/5 hover:bg-white/10 text-xs font-medium text-[#ededed] transition-all cursor-pointer active:scale-95 group/btn"
        >
          <span>View Details</span>
          <ArrowRight className="w-3.5 h-3.5 group-hover/btn:translate-x-0.5 transition-transform" />
        </button>
      </div>
    </div>
  );
}
