import type { Incident } from '@/lib/types';
import SeverityBadge from './SeverityBadge';
import CategoryTag from './CategoryTag';

interface IncidentCardProps {
  incident: Incident;
}

export default function IncidentCard({ incident }: IncidentCardProps) {
  const borderColor = {
    critical: 'border-l-red-600',
    high: 'border-l-orange-500',
    medium: 'border-l-amber-500',
    low: 'border-l-emerald-500',
    none: 'border-l-gray-400',
  }[incident.severity] || 'border-l-gray-400';

  const timeAgo = incident.last_seen
    ? formatTimeAgo(new Date(incident.last_seen))
    : '';

  const sourceTime = incident.source_created_at
    ? formatTimestamp(new Date(incident.source_created_at))
    : null;

  return (
    <div className={`bg-white rounded-[14px] border border-gray-200 p-3.5 shadow-sm border-l-[3px] ${borderColor} flex flex-col`}>
      <div className="flex items-center gap-2 mb-2">
        <SeverityBadge severity={incident.severity} />
        <span className="ml-auto text-[11px] text-gray-500">{timeAgo}</span>
      </div>
      <h4 className="text-sm font-semibold text-gray-900 mb-1.5 leading-snug">{incident.title}</h4>
      <p className="text-[12.5px] text-gray-600 leading-relaxed mb-2.5 line-clamp-2">
        {incident.summary}
      </p>

      {/* Source link + timestamp */}
      {incident.source_url && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1.5 mb-2.5 flex items-center gap-2 text-[11.5px]">
          <svg className="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          <a
            href={incident.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-pink-600 hover:text-pink-700 font-medium truncate"
          >
            {incident.source_author ? `@${incident.source_author}` : 'View source'}
          </a>
          {sourceTime && (
            <span className="ml-auto text-gray-500 whitespace-nowrap shrink-0">{sourceTime}</span>
          )}
        </div>
      )}

      <div className="flex items-center gap-2 text-[11.5px] text-gray-500 flex-wrap mt-auto">
        {incident.platforms?.map((p) => (
          <span key={p} className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-[11px] font-medium">
            {p === 'twitter' ? 'X' : 'Reddit'}
          </span>
        ))}
        {incident.category && <CategoryTag category={incident.category} />}
        {incident.trend_pct != null && incident.trend_pct > 0 && (
          <span className="text-red-600 font-semibold text-[11.5px]">
            ▲ {incident.trend_pct.toFixed(0)}%
          </span>
        )}
        <span>{incident.post_count} posts</span>
      </div>
    </div>
  );
}

function formatTimeAgo(date: Date): string {
  const diff = Date.now() - date.getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return `${Math.floor(diff / 60000)}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function formatTimestamp(date: Date): string {
  const month = date.toLocaleString('en-US', { month: 'short' });
  const day = date.getDate();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${month} ${day}, ${hours}:${minutes}`;
}
