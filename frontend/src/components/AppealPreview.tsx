import React, { useState } from 'react';
import type { AppealLetter as AppealLetterType } from '../lib/api';
import { Copy, Check, Download, Mail } from 'lucide-react';

export function AppealPreview({ appeal }: { appeal: AppealLetterType }) {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(appeal.full_text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const downloadText = () => {
        const element = document.createElement("a");
        const file = new Blob([appeal.full_text], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = "Appeal_Letter.txt";
        document.body.appendChild(element); // Required for this to work in FireFox
        element.click();
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mt-6">
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Mail className="w-5 h-5 text-gray-700" />
                    <h3 className="font-semibold text-gray-900">Generated Appeal Letter</h3>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={handleCopy}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                        {copied ? 'Copied' : 'Copy Text'}
                    </button>
                    <button
                        onClick={downloadText}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary-700 bg-primary-50 border border-primary-100 rounded-lg hover:bg-primary-100 transition-colors"
                    >
                        <Download className="w-4 h-4" />
                        Download
                    </button>
                </div>
            </div>

            <div className="p-6">
                <div className="bg-gray-50 p-6 rounded-lg text-sm text-gray-800 font-sans leading-relaxed whitespace-pre-wrap border border-gray-200/60 shadow-inner overflow-x-auto">
                    {appeal.full_text}
                </div>

                {appeal.attachments_needed && appeal.attachments_needed.length > 0 && (
                    <div className="mt-4 p-4 border border-blue-100 bg-blue-50/50 rounded-lg">
                        <h4 className="text-sm font-semibold text-blue-900 mb-2">Required Attachments for Submission:</h4>
                        <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
                            {appeal.attachments_needed.map((item, i) => (
                                <li key={i}>{item}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
