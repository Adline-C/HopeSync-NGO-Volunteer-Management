import React from 'react';

export default function ProfileDashboard({ user, level, levelProgress, hoursToNextLevel, badges }) {
  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col justify-between h-full">
      {/* Header Profile Section */}
      <div>
        <div className="flex items-center gap-4 mb-5">
          <div className="h-12 w-12 shrink-0 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div className="min-w-0">
            <h2 className="text-lg font-bold text-slate-800 truncate" title={user.username}>{user.username}</h2>
            <span className="text-xs text-indigo-600 font-semibold bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-100 inline-block mt-1">
              Level {level} Volunteer
            </span>
          </div>
        </div>

        {/* Contribution stats */}
        <div className="mt-4 bg-slate-50/50 p-4 rounded-xl border border-slate-100">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Total Hours Contributed</span>
          <span className="text-4xl font-black text-indigo-600 tracking-tight mt-1 block">
            {user.total_hours} <span className="text-sm font-semibold text-slate-400">hrs</span>
          </span>
        </div>

        {/* Dynamic Level Progress bar */}
        <div className="mt-6">
          <div className="flex justify-between text-xs font-bold text-slate-500 mb-2">
            <span>Level {level}</span>
            <span>{Math.round(levelProgress)}% to Level {level + 1}</span>
          </div>
          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
            <div 
              className="bg-indigo-600 h-full transition-all duration-500 rounded-full" 
              style={{ width: `${levelProgress}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-400 mt-2 block">
            Accumulate {hoursToNextLevel} more hour{hoursToNextLevel !== 1 ? 's' : ''} to level up.
          </span>
        </div>
      </div>

      {/* Badges / Milestones Section */}
      <div className="border-t border-slate-100 pt-5 mt-6">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-4">Milestones & Achievements</span>
        <div className="grid grid-cols-2 gap-3">
          {badges.map((badge) => (
            badge.is_unlocked ? (
              /* Unlocked Achievement Grid Card */
              <div 
                key={badge.id}
                className="bg-gradient-to-br from-amber-50/30 to-amber-50 border border-amber-200/60 p-3.5 rounded-xl shadow-sm shadow-amber-200/50 hover:scale-[1.02] transition-transform duration-200 flex flex-col justify-between"
                title={badge.description}
              >
                <div className="flex items-center gap-2.5">
                  <div className="bg-amber-100 text-amber-600 p-2 rounded-lg shrink-0 flex items-center justify-center">
                    <i className={`fa-solid ${badge.icon} text-sm`} />
                  </div>
                  <span className="text-xs font-bold text-amber-800 leading-snug truncate">{badge.name}</span>
                </div>
                <span className="text-[9px] text-amber-600 mt-3 font-semibold flex items-center gap-1">
                  <i className="fa-solid fa-lock-open text-[8px]" /> Unlocked
                </span>
              </div>
            ) : (
              /* Locked Achievement Card */
              <div 
                key={badge.id}
                className="bg-white border border-slate-200/80 p-3.5 rounded-xl opacity-60 filter grayscale hover:grayscale-0 hover:opacity-100 hover:border-indigo-100 hover:shadow-sm hover:scale-[1.02] transition-all duration-200 flex flex-col justify-between"
                title={badge.description}
              >
                <div className="flex items-center gap-2.5">
                  <div className="bg-slate-100 text-slate-400 p-2 rounded-lg shrink-0 flex items-center justify-center">
                    <i className={`fa-solid ${badge.icon} text-sm`} />
                  </div>
                  <span className="text-xs font-semibold text-slate-500 leading-snug truncate">{badge.name}</span>
                </div>
                <span className="text-[9px] text-slate-400 mt-3 font-medium">
                  Need {badge.hours_required}h ({user.total_hours}/{badge.hours_required}h)
                </span>
              </div>
            )
          ))}
        </div>
      </div>
    </div>
  );
}
