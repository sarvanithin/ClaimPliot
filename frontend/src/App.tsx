import React, { useState } from 'react';
import { ClaimInput } from './components/ClaimInput';
import { DenialAnalysis } from './components/DenialAnalysis';
import { PolicyMatches } from './components/PolicyMatches';
import { AppealPreview } from './components/AppealPreview';
import { StatusTracker } from './components/StatusTracker';
import type { AgentStep } from './components/StatusTracker';
import { analyzeClaim } from './lib/api';
import type { Claim, AppealResult } from './lib/api';
import { FileText, Activity } from 'lucide-react';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AppealResult | null>(null);
  const [steps, setSteps] = useState<AgentStep[]>([
    { id: '1', label: 'Classify Denial', status: 'pending' },
    { id: '2', label: 'Retrieve Policy Context', status: 'pending' },
    { id: '3', label: 'Analyze Medical Necessity', status: 'pending' },
    { id: '4', label: 'Draft Appeal Letter', status: 'pending' },
    { id: '5', label: 'Self-Critique & Refine', status: 'pending' },
  ]);

  const handleSubmitClaim = async (claim: Claim) => {
    setIsLoading(true);
    setResult(null);
    setSteps(steps.map(s => ({ ...s, status: 'pending' })));

    // Simulate progress updates for the UI
    setTimeout(() => setSteps(s => s.map((step, i) => i === 0 ? { ...step, status: 'active' } : step)), 500);
    setTimeout(() => setSteps(s => s.map((step, i) => i === 0 ? { ...step, status: 'complete' } : i === 1 ? { ...step, status: 'active' } : step)), 1500);
    setTimeout(() => setSteps(s => s.map((step, i) => i === 1 ? { ...step, status: 'complete' } : i === 2 ? { ...step, status: 'active' } : step)), 3000);
    setTimeout(() => setSteps(s => s.map((step, i) => i === 2 ? { ...step, status: 'complete' } : i === 3 ? { ...step, status: 'active' } : step)), 4500);
    setTimeout(() => setSteps(s => s.map((step, i) => i === 3 ? { ...step, status: 'complete' } : i === 4 ? { ...step, status: 'active' } : step)), 6500);

    try {
      const response = await analyzeClaim(claim);
      setResult(response);
      setSteps(s => s.map(step => ({ ...step, status: 'complete' })));
    } catch (error) {
      console.error('Failed to analyze claim:', error);
      alert('Failed to analyze claim. Ensure the backend is running.');
      setSteps(s => s.map(step => step.status === 'active' ? { ...step, status: 'error' } : step));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center gap-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center shadow-lg shadow-primary-500/20">
            <Activity className="text-white w-5 h-5" />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
            ClaimPilot
          </h1>
          <span className="ml-2 px-2.5 py-0.5 rounded-full bg-primary-50 text-primary-700 text-xs font-medium border border-primary-100">
            AI Appeal Agent
          </span>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-5 space-y-6">
          <ClaimInput onSubmit={handleSubmitClaim} isLoading={isLoading} />
        </div>

        <div className="lg:col-span-7 space-y-6">
          {isLoading && (
            <div className="space-y-6">
              <StatusTracker steps={steps} />
            </div>
          )}

          {!isLoading && !result && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                <FileText className="text-gray-400 w-8 h-8" />
              </div>
              <h3 className="text-lg font-medium text-gray-900">Waiting for Data</h3>
              <p className="text-gray-500 mt-2 max-w-md">
                Enter claim details and clinical notes on the left. ClaimPilot will classify the denial, retrieve relevant policy, and draft an appeal.
              </p>
            </div>
          )}

          {result && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 fill-mode-forwards">
              <DenialAnalysis analysis={result.analysis} />
              <PolicyMatches policies={result.policies} />
              <AppealPreview appeal={result.appeal} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
