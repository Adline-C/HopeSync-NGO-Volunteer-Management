import React from 'react';

export default function CertificateModule({ volunteer, downloadUrl, cardUrl }) {
  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col justify-between h-full space-y-6">
      {/* Module Title Header */}
      <div className="flex items-center gap-3">
        <div className="bg-indigo-50 text-indigo-600 p-2.5 rounded-xl shrink-0 flex items-center justify-center">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <div>
          <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-widest block">Verifications</span>
          <h3 className="text-base font-bold text-slate-800 leading-tight">Verified Certifications</h3>
        </div>
      </div>

      {/* Description Text */}
      <p className="text-xs text-slate-500 leading-relaxed">
        Access your official, system-generated transcript. Download a verified community service certificate or retrieve your digital ID.
      </p>

      {/* Grid aligned action section */}
      <div className="grid grid-cols-1 gap-3 pt-2">
        <a 
          href={downloadUrl}
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shadow-emerald-100 hover:shadow-emerald-200 transition-all duration-150 flex items-center justify-center gap-2 text-xs text-center"
        >
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Get PDF Certificate
        </a>

        <a 
          href={cardUrl}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shadow-indigo-100 hover:shadow-indigo-200 transition-all duration-150 flex items-center justify-center gap-2 text-xs text-center"
        >
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 014 0" />
          </svg>
          Show ID Card
        </a>
      </div>
    </div>
  );
}
