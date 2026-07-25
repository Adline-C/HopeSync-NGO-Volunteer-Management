import React from 'react';
import { QRCodeSVG } from 'qrcode.react';

export default function VolunteerCard({ volunteer }) {
  const verificationUrl = `https://hopesync.org/verify/${volunteer.username}`;

  return (
    <div className="max-w-md mx-auto p-4 flex flex-col items-center">
      <!-- Wallet-style ID Card container -->
      <div className="w-full max-w-sm bg-gradient-to-b from-indigo-700 to-indigo-900 text-white rounded-3xl shadow-xl overflow-hidden border border-indigo-600/30 flex flex-col justify-between aspect-[2.5/4] sm:aspect-[3/5]">
        
        <!-- Header -->
        <div className="px-6 py-5 border-b border-indigo-600/30 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-white/10 p-1.5 rounded-lg">
              <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-12.728l.707.707m12.728 12.728l.707-.707M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="font-bold tracking-wider text-sm bg-gradient-to-r from-emerald-400 to-white bg-clip-text text-transparent">HopeSync</span>
          </div>
          <span className="text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full">
            ACTIVE
          </span>
        </div>

        {/* Body / QR Code Block */}
        <div className="px-6 py-6 flex flex-col items-center justify-center flex-grow bg-slate-900/40">
          {/* Dynamic styled QR Code Container */}
          <div className="bg-white p-4 rounded-2xl shadow-inner flex items-center justify-center border-4 border-indigo-500/20 w-[172px] h-[172px]">
            <QRCodeSVG
              value={verificationUrl}
              size={140}
              bgColor={"#ffffff"}
              fgColor={"#312e81"}
              level={"H"}
              includeMargin={false}
              imageSettings={{
                src: "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2310b981'><circle cx='12' cy='12' r='10'/></svg>",
                x: undefined,
                y: undefined,
                height: 24,
                width: 24,
                excavate: true,
              }}
            />
          </div>
          <span className="text-[11px] font-mono tracking-widest text-indigo-200 mt-4 bg-indigo-950/40 px-3 py-1 rounded border border-indigo-800/30 break-all select-all">
            ID: {volunteer.username}
          </span>
        </div>

        {/* Footer / Volunteer Details */}
        <div className="px-6 py-5 bg-indigo-950 border-t border-indigo-900 flex flex-col gap-1">
          <div className="flex flex-col">
            <span className="text-[9px] uppercase tracking-widest text-indigo-400 font-bold">Volunteer</span>
            <span className="text-base font-bold tracking-tight text-white leading-none mt-1">
              {volunteer.first_name || volunteer.username} {volunteer.last_name || ''}
            </span>
            <span className="text-xs text-indigo-300 font-medium truncate mt-0.5">{volunteer.email}</span>
          </div>
          
          <div className="flex justify-between items-center border-t border-indigo-900 pt-3 mt-2 text-[10px] text-indigo-400">
            <span>Joined: {volunteer.date_joined || 'Recent'}</span>
            <span>Hours: {volunteer.total_hours || '0.0'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
