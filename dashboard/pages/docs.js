import React, { useState } from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import { Book, Code, Webhook, Zap, ChevronRight } from 'lucide-react';
import { withAuth } from '../hooks/useAuth';

function Docs() {
  const [activeSection, setActiveSection] = useState('quickstart');

  const navItems = [
    { id: 'quickstart', label: 'Quickstart', icon: Zap },
    { id: 'sdk', label: 'SDK Reference', icon: Code },
    { id: 'webhooks', label: 'Webhooks & CI/CD', icon: Webhook },
  ];

  return (
    <Layout>
      <Head>
        <title>Documentation - DriftGuard</title>
      </Head>

      <div className="max-w-6xl mx-auto h-[calc(100vh-theme(spacing.16))] flex">
        {/* Docs Sidebar */}
        <div className="w-64 flex-shrink-0 py-8 pr-8 border-r border-white/10">
          <h2 className="text-sm font-bold text-[#ededed] mb-6 tracking-wide flex items-center">
            <Book className="w-4 h-4 mr-2 text-[#24b47e]" />
            DOCUMENTATION
          </h2>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-xl transition-all ${
                    isActive
                      ? 'bg-[#18181b] text-[#24b47e] shadow-sm'
                      : 'text-[#a1a1aa] hover:text-[#ededed] hover:bg-[#18181b]/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 mr-3 ${isActive ? 'text-[#24b47e]' : 'text-[#52525b]'}`} />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Docs Content */}
        <div className="flex-1 overflow-y-auto py-8 pl-10 pr-6">
          <div className="max-w-3xl prose prose-invert prose-p:text-[#a1a1aa] prose-headings:text-[#ededed] prose-a:text-[#24b47e] prose-code:text-[#ededed] prose-code:bg-[#18181b] prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-xl prose-code:border prose-code:border-white/10 prose-pre:bg-[#18181b] prose-pre:border prose-pre:border-white/10">
            
            {activeSection === 'quickstart' && (
              <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                <h1 className="text-3xl font-bold tracking-tight mb-2">Quickstart</h1>
                <p className="text-lg text-[#a1a1aa] mb-8 leading-relaxed">
                  Get DriftGuard running in your ML pipeline in under 5 minutes.
                </p>

                <h3 className="text-xl font-semibold mt-10 mb-4 border-b border-white/10 pb-2">1. Install the SDK</h3>
                <p className="mb-4 text-[#a1a1aa]">Install the DriftGuard Python SDK into your inference environment:</p>
                <div className="relative group mb-8">
                  <pre className="p-4 rounded-xl bg-[#18181b] border border-white/10 overflow-x-auto">
                    <code className="text-sm font-mono text-[#ededed]">pip install driftguard</code>
                  </pre>
                </div>

                <h3 className="text-xl font-semibold mt-10 mb-4 border-b border-white/10 pb-2">2. Initialize in your API</h3>
                <p className="mb-4 text-[#a1a1aa]">Import DriftGuard and initialize it with your project's API Key. You can rotate this key anytime from Settings.</p>
                <div className="relative group mb-8">
                  <pre className="p-4 rounded-xl bg-[#18181b] border border-white/10 overflow-x-auto">
                    <code className="text-sm font-mono text-[#ededed]">{`from fastapi import FastAPI
from driftguard import DriftGuard

dg = DriftGuard(
    model_id="fraud-detector-v1",
    api_key="dg-your-secret-key",
    drift_threshold=0.15,
    expected_features=["amount", "location_score", "velocity"]
)

app = FastAPI()`}</code>
                  </pre>
                </div>

                <h3 className="text-xl font-semibold mt-10 mb-4 border-b border-white/10 pb-2">3. Log Predictions</h3>
                <p className="mb-4 text-[#a1a1aa]">Wrap your model inference function to log telemetry asynchronously without blocking your API.</p>
                <div className="relative group mb-8">
                  <pre className="p-4 rounded-xl bg-[#18181b] border border-white/10 overflow-x-auto">
                    <code className="text-sm font-mono text-[#ededed]">{`@app.post("/predict")
def predict(features: list[float]):
    prediction = model.predict([features])
    
    # Non-blocking async telemetry log
    dg.log_prediction(
        features=features,
        prediction=prediction
    )
    
    return {"fraud_probability": prediction}`}</code>
                  </pre>
                </div>
              </div>
            )}

            {activeSection === 'sdk' && (
              <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                <h1 className="text-3xl font-bold tracking-tight mb-2">SDK Reference</h1>
                <p className="text-lg text-[#a1a1aa] mb-8 leading-relaxed">
                  Complete API documentation for the Python SDK.
                </p>

                <div className="space-y-12">
                  <div>
                    <h3 className="text-lg font-bold font-mono text-[#24b47e] mb-2 flex items-center">
                      <ChevronRight className="w-4 h-4 mr-1" />
                      DriftGuard.__init__
                    </h3>
                    <p className="mb-4 text-[#a1a1aa]">Initializes the telemetry client. Fails silently if connection cannot be established to prevent blocking your main thread.</p>
                    <table className="w-full text-left text-sm mb-6 border-collapse">
                      <thead>
                        <tr className="border-b border-white/10 text-[#ededed]">
                          <th className="pb-2 font-medium">Argument</th>
                          <th className="pb-2 font-medium">Type</th>
                          <th className="pb-2 font-medium">Description</th>
                        </tr>
                      </thead>
                      <tbody className="text-[#a1a1aa]">
                        <tr className="border-b border-white/10/50">
                          <td className="py-3 font-mono text-xs">model_id</td>
                          <td className="py-3 font-mono text-xs">str</td>
                          <td className="py-3">Unique identifier for this model.</td>
                        </tr>
                        <tr className="border-b border-white/10/50">
                          <td className="py-3 font-mono text-xs">api_key</td>
                          <td className="py-3 font-mono text-xs">str</td>
                          <td className="py-3">Your project API key.</td>
                        </tr>
                        <tr className="border-b border-white/10/50">
                          <td className="py-3 font-mono text-xs">drift_threshold</td>
                          <td className="py-3 font-mono text-xs">float</td>
                          <td className="py-3">The ADWIN score threshold (0.0-1.0) to trigger alerts.</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {activeSection === 'webhooks' && (
              <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                <h1 className="text-3xl font-bold tracking-tight mb-2">Webhooks & CI/CD</h1>
                <p className="text-lg text-[#a1a1aa] mb-8 leading-relaxed">
                  Connect DriftGuard to your existing infrastructure.
                </p>
                <div className="bg-[#18181b] border border-white/10 rounded-xl p-6 mb-8">
                  <h4 className="font-semibold text-[#ededed] mb-2">How it works</h4>
                  <p className="text-sm leading-relaxed mb-4 text-[#a1a1aa]">
                    When the DriftGuard SDK detects that your live telemetry has breached the `drift_threshold`, the central dashboard is immediately notified.
                    If you have configured a Webhook URL, the dashboard will fire a POST request to your orchestrator (Airflow, AWS SageMaker, Jenkins) containing the event details.
                  </p>
                  <p className="text-sm font-semibold text-[#24b47e]">
                    This enables fully autonomous, zero-touch retraining pipelines.
                  </p>
                </div>

                <h3 className="text-xl font-semibold mt-8 mb-4 border-b border-white/10 pb-2">Webhook Payload (POST)</h3>
                <div className="relative group mb-8">
                  <pre className="p-4 rounded-xl bg-[#18181b] border border-white/10 overflow-x-auto">
                    <code className="text-sm font-mono text-[#ededed]">{`{
  "event_id": 1042,
  "model_id": "fraud-detector-v1",
  "drift_score": 0.18,
  "callback_url": "https://api.driftguard.ai/retrain/fraud-detector-v1/complete"
}`}</code>
                  </pre>
                </div>

                <h3 className="text-xl font-semibold mt-8 mb-4 border-b border-white/10 pb-2">Completing the Loop</h3>
                <p className="mb-4 text-[#a1a1aa]">Once your massive GPU cluster finishes training the new model, it must POST back to the `callback_url` to complete the event and update the dashboard:</p>
                <div className="relative group mb-8">
                  <pre className="p-4 rounded-xl bg-[#18181b] border border-white/10 overflow-x-auto">
                    <code className="text-sm font-mono text-[#ededed]">{`POST https://api.driftguard.ai/retrain/fraud-detector-v1/complete

{
  "event_id": 1042,
  "validation_passed": true,
  "new_version": "1.0.1",
  "new_accuracy": 0.942,
  "old_accuracy": 0.891
}`}</code>
                  </pre>
                </div>
              </div>
            )}
            
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default withAuth(Docs);
