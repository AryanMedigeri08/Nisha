import React from 'react';
import { AuditEventDTO } from '../types/review';
import { Shield, Clock, FileText, CheckCircle2, User, ArrowRight } from 'lucide-react';

interface AuditTimelineProps {
  events: AuditEventDTO[];
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-lg border border-slate-200">
        No audit events recorded for this session yet.
      </div>
    );
  }

  // Sort events chronologically (oldest to newest or newest on top)
  const sorted = [...events].sort((a, b) => (a.id > b.id ? 1 : -1));

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
      {sorted.map((ev, index) => {
        const dateObj = new Date(ev.timestamp);
        const timeStr = isNaN(dateObj.getTime())
          ? ev.timestamp
          : dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const dateStr = isNaN(dateObj.getTime())
          ? ''
          : dateObj.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });

        return (
          <div key={ev.id || index} className="relative group">
            {/* Dot marker */}
            <div className="absolute -left-6 top-1 w-3 h-3 rounded-full bg-blue-600 border-2 border-white shadow-sm ring-2 ring-blue-100" />

            <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-sm text-xs space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono font-semibold text-slate-900 bg-slate-100 px-2 py-0.5 rounded text-[11px] border border-slate-200">
                  {ev.event_type}
                </span>
                <span className="text-[11px] text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {dateStr} {timeStr}
                </span>
              </div>

              {/* State transition if present */}
              {ev.previous_state && ev.new_state && (
                <div className="flex items-center gap-2 text-slate-700 bg-slate-50 p-1.5 rounded border border-slate-100 font-mono text-[11px]">
                  <span className="px-1.5 py-0.5 bg-slate-200 text-slate-700 rounded text-[10px]">
                    {ev.previous_state}
                  </span>
                  <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                  <span className="px-1.5 py-0.5 bg-blue-100 text-blue-800 rounded font-semibold text-[10px]">
                    {ev.new_state}
                  </span>
                </div>
              )}

              {/* Actor */}
              <div className="flex items-center gap-1.5 text-slate-600">
                <User className="w-3 h-3 text-slate-400" />
                <span className="font-medium text-slate-800">{ev.actor_id}</span>
                <span className="text-slate-400">({ev.actor_role})</span>
              </div>

              {/* Details / JSON Payload */}
              {ev.details && Object.keys(ev.details).length > 0 && (
                <div className="bg-slate-50 p-2 rounded border border-slate-200/80 font-mono text-[11px] text-slate-800 break-words whitespace-pre-wrap">
                  {typeof ev.details === 'string' ? ev.details : JSON.stringify(ev.details, null, 2)}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
