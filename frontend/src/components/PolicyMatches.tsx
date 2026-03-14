import React from 'react';
import type { PolicyReference } from '../lib/api';
import { BookOpen, CheckCircle2 } from 'lucide-react';

export function PolicyMatches({ policies }: { policies: PolicyReference[] }) {
    if (policies.length === 0) return null;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-indigo-600" />
                    <h3 className="font-semibold text-gray-900">Retrieved Policy Evidence</h3>
                </div>
                <span className="bg-indigo-100 text-indigo-700 text-xs font-semibold px-2 py-1 rounded-full">
                    {policies.length} Match{policies.length > 1 ? 'es' : ''}
                </span>
            </div>
            <div className="divide-y divide-gray-100">
                {policies.map((policy, idx) => (
                    <div key={idx} className="p-5">
                        <div className="flex justify-between items-start mb-2">
                            <h4 className="font-medium text-sm text-gray-900 flex items-center gap-2">
                                {policy.source}
                                <span className="text-gray-400 text-xs font-normal">({policy.section})</span>
                            </h4>
                        </div>
                        <p className="text-sm text-gray-600 italic bg-gray-50 p-3 rounded-lg border border-gray-100/50 mb-3">
                            "{policy.text}"
                        </p>
                        <div className="flex gap-2 items-start text-sm">
                            <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                            <p className="text-emerald-700/80 font-medium">
                                <span className="text-emerald-800">Relevance:</span> {policy.relevance}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
