import React from 'react';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

export type AgentStep = {
    id: string;
    label: string;
    status: 'pending' | 'active' | 'complete' | 'error';
    description?: string;
};

export function StatusTracker({ steps }: { steps: AgentStep[] }) {
    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50">
                <h3 className="font-semibold text-gray-900">Agent Progress</h3>
            </div>
            <div className="p-6">
                <ul className="space-y-6">
                    {steps.map((step, idx) => (
                        <li key={step.id} className="relative">
                            {idx !== steps.length - 1 && (
                                <div
                                    className={`absolute left-3 top-8 bottom-[-24px] w-[2px] ${step.status === 'complete' ? 'bg-primary-500' : 'bg-gray-200'
                                        }`}
                                />
                            )}
                            <div className="flex items-start gap-4 relative z-10">
                                <div className="bg-white mt-0.5">
                                    {step.status === 'complete' && <CheckCircle2 className="w-6 h-6 text-primary-500" />}
                                    {step.status === 'active' && <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />}
                                    {step.status === 'pending' && <Circle className="w-6 h-6 text-gray-300" />}
                                    {step.status === 'error' && <Circle className="w-6 h-6 text-red-500" fill="currentColor" />}
                                </div>
                                <div>
                                    <h4 className={`text-sm font-medium ${step.status === 'active' ? 'text-blue-700' :
                                        step.status === 'complete' ? 'text-gray-900' : 'text-gray-500'
                                        }`}>
                                        {step.label}
                                    </h4>
                                    {step.description && (
                                        <p className="text-xs text-gray-500 mt-1">{step.description}</p>
                                    )}
                                </div>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
