import React, { useState } from 'react';
import { updateWebhookUrl } from '../lib/api';
import { CloudRain, Save, Link as LinkIcon, CheckCircle2 } from 'lucide-react';

export default function WebhookConfig({ modelId, initialUrl = '' }) {
  const [webhookUrl, setWebhookUrl] = useState(initialUrl || '');
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    setSaved(false);
    
    try {
      await updateWebhookUrl(modelId, webhookUrl);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#09090b] border border-white/10 rounded-xl overflow-hidden shadow-sm mt-8 font-sans">
      <div className="border-b border-white/10 px-6 py-5 flex items-center space-x-3 bg-gradient-to-r from-[#111111] to-[#000000]">
        <div className="p-1.5 bg-[#ffffff]/10 rounded-xl ring-1 ring-inset ring-[#ffffff]/20">
          <CloudRain className="w-4 h-4 text-[#ffffff]" />
        </div>
        <h2 className="text-base font-semibold tracking-tight text-[#ededed]">Cloud Retraining Webhook (Airflow Integration)</h2>
      </div>
      
      <div className="p-6 bg-[#09090b]">
        <p className="text-sm text-[#a1a1aa] mb-6 max-w-3xl leading-relaxed">
          Configure an external orchestrator (like Apache Airflow, Kubeflow, or AWS SageMaker) to handle model retraining when drift is detected. DriftGuard will POST a JSON payload to this URL instead of running the retraining pipeline locally.
        </p>
        
        <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <div className="relative flex-1 group">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none transition-colors group-focus-within:text-[#ededed] text-[#52525b]">
              <LinkIcon className="h-4 w-4" />
            </div>
            <input
              type="text"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              placeholder="https://airflow.mycompany.com/api/v1/dags/retrain_model/dagRuns"
              className="block w-full pl-10 pr-4 py-2.5 bg-[#09090b] border border-white/10 rounded-xl text-sm text-[#ededed] placeholder-[#52525b] focus:outline-none focus:border-[#666666] focus:ring-1 focus:ring-[#666666] transition-all shadow-inner"
            />
          </div>
          
          <button
            onClick={handleSave}
            disabled={loading}
            className={`flex items-center justify-center px-5 py-2.5 rounded-xl font-medium text-sm transition-all shadow-sm ${
              saved 
                ? 'bg-transparent border border-[#10b981] text-[#10b981]'
                : 'bg-[#ededed] hover:bg-[#ffffff] text-[#000000] border border-transparent active:scale-95'
            } disabled:opacity-50`}
          >
            {saved ? (
              <>
                <CheckCircle2 className="w-4 h-4 mr-2" />
                <span>Saved</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                <span>{loading ? 'Saving...' : 'Save Webhook'}</span>
              </>
            )}
          </button>
        </div>
        
        {error && (
          <div className="mt-4 p-3 bg-[#7f1d1d]/10 border border-[#7f1d1d]/50 rounded-xl">
            <p className="text-sm text-[#f87171] flex items-center">
              <span className="w-1.5 h-1.5 rounded-full bg-[#f87171] mr-2"></span>
              {error}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
