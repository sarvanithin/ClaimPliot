import React, { useState } from 'react';
import type { Claim } from '../lib/api';

interface ClaimInputProps {
    onSubmit: (claim: Claim) => void;
    isLoading: boolean;
}

const DEFAULT_CLAIM: Claim = {
    patient_id: 'P-10042',
    procedure_code: '99214',
    diagnosis_codes: ['E11.65', 'E11.9'],
    payer: 'Medicare',
    denial_code: 'CO-50',
    denial_reason: 'Services not deemed medically necessary',
    date_of_service: '01/15/2026',
    provider_name: 'Dr. Sarah Smith, MD',
    clinical_notes: 'Patient with uncontrolled T2DM, A1c 9.2%, on metformin and glipizide. Experiencing neuropathy. Increasing dosage and scheduling frequent follow-ups.',
};

export function ClaimInput({ onSubmit, isLoading }: ClaimInputProps) {
    const [claim, setClaim] = useState<Claim>(DEFAULT_CLAIM);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        if (name === 'diagnosis_codes') {
            setClaim(prev => ({ ...prev, [name]: value.split(',').map(s => s.trim()) }));
        } else {
            setClaim(prev => ({ ...prev, [name]: value }));
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(claim);
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-100 bg-gray-50/50">
                <h2 className="text-xl font-semibold text-gray-900">Claim Details</h2>
                <p className="text-sm text-gray-500 mt-1">Input the denied claim information to generate an appeal.</p>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Procedure Code</label>
                        <input
                            type="text"
                            name="procedure_code"
                            value={claim.procedure_code}
                            onChange={handleChange}
                            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosis Codes (comma separated)</label>
                        <input
                            type="text"
                            name="diagnosis_codes"
                            value={claim.diagnosis_codes.join(', ')}
                            onChange={handleChange}
                            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Denial Code</label>
                        <input
                            type="text"
                            name="denial_code"
                            value={claim.denial_code}
                            onChange={handleChange}
                            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Payer</label>
                        <input
                            type="text"
                            name="payer"
                            value={claim.payer}
                            onChange={handleChange}
                            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            required
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Denial Reason (from EOB)</label>
                    <textarea
                        name="denial_reason"
                        value={claim.denial_reason}
                        onChange={handleChange}
                        rows={2}
                        className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all resize-none"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Clinical Notes (Optional but recommended)</label>
                    <textarea
                        name="clinical_notes"
                        value={claim.clinical_notes || ''}
                        onChange={handleChange}
                        rows={4}
                        className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all resize-none"
                        placeholder="Include relevant patient history, symptoms, and rationale for the procedure..."
                    />
                </div>

                <div className="pt-2">
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-primary-300 text-white font-medium py-3 px-6 rounded-lg shadow-sm shadow-primary-500/30 transition-all flex justify-center items-center gap-2"
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                <span>Analyzing Claim...</span>
                            </>
                        ) : (
                            <span>Generate Appeal</span>
                        )}
                    </button>
                </div>
            </form>
        </div>
    );
}
