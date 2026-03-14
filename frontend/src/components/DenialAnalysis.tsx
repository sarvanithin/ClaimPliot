import React from 'react';
import type { DenialAnalysis as DenialAnalysisType } from '../lib/api';
import { AlertCircle, Target, Activity } from 'lucide-react';

export function DenialAnalysis({ analysis }: { analysis: DenialAnalysisType }) {
    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary-600" />
                <h3 className="font-semibold text-gray-900">Agent Analysis</h3>
            </div>
            <div className="p-5 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-3">
                        <span className="text-xs text-gray-500 uppercase tracking-wide font-medium">Category</span>
                        <p className="mt-1 font-medium text-gray-900 capitalize text-sm">
                            {analysis.denial_category.replace('_', ' ')}
                        </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                        <span className="text-xs text-gray-500 uppercase tracking-wide font-medium">Denial Code</span>
                        <p className="mt-1 font-medium text-gray-900 text-sm">
                            {analysis.denial_code}
                        </p>
                    </div>
                </div>

                <div className="flex gap-3 items-start border-l-4 border-amber-400 pl-4 py-1">
                    <AlertCircle className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
                    <div>
                        <h4 className="text-sm font-medium text-gray-900">Root Cause</h4>
                        <p className="text-sm text-gray-600 mt-1">{analysis.root_cause}</p>
                    </div>
                </div>

                <div className="flex gap-3 items-start border-l-4 border-primary-500 pl-4 py-1">
                    <Target className="w-5 h-5 text-primary-600 mt-0.5 shrink-0" />
                    <div>
                        <h4 className="text-sm font-medium text-gray-900">Appeal Strategy</h4>
                        <p className="text-sm text-gray-600 mt-1">{analysis.appeal_strategy}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
