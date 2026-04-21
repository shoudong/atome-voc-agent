import type { Incident } from '@/lib/types';
import SeverityBadge from './SeverityBadge';
import CategoryTag from './CategoryTag';
import { STATUS_MAP } from '@/lib/constants';

interface IncidentTableProps {
  incidents: Incident[];
}

export default function IncidentTable({ incidents }: IncidentTableProps) {
  return (
    <table className="w-full border-collapse text-[13px]">
      <thead>
        <tr>
          {['Sev', 'Incident', 'Source', 'Category', 'Channel', 'Posts', '24h Change', 'Status'].map((h) => (
            <th
              key={h}
              className="text-left text-[11px] uppercase tracking-wider text-gray-500 font-semibold px-2.5 py-2 border-b border-gray-200 bg-gray-50"
            >
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {incidents.map((inc) => {
          const status = STATUS_MAP[inc.status as keyof typeof STATUS_MAP] || STATUS_MAP.new;
          return (
            <tr key={inc.id} className="hover:bg-gray-50 group">
              <td className="px-2.5 py-3 border-b border-gray-100">
                <SeverityBadge severity={inc.severity} />
              </td>
              <td className="px-2.5 py-3 border-b border-gray-100">
                <div className="font-semibold text-gray-900">{inc.title}</div>
                <div className="text-[11.5px] text-gray-500">
                  {inc.incident_code} &middot; {inc.post_count} posts
                </div>
              </td>
              <td className="px-2.5 py-3 border-b border-gray-100 max-w-[180px]">
                {inc.source_url ? (
                  <div>
                    <a
                      href={inc.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-pink-600 hover:underline text-[11.5px] truncate block"
                    >
                      @{inc.source_author || 'link'}
                    </a>
                    {inc.source_created_at && (
                      <div className="text-[10.5px] text-gray-400">
                        {new Date(inc.source_created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </div>
                    )}
                  </div>
                ) : (
                  <span className="text-gray-400 text-[11px]">-</span>
                )}
              </td>
              <td className="px-2.5 py-3 border-b border-gray-100">
                {inc.category && <CategoryTag category={inc.category} />}
              </td>
              <td className="px-2.5 py-3 border-b border-gray-100">
                {inc.platforms?.map((p) => (
                  <span key={p} className="mr-1">
                    {p === 'twitter' ? 'X' : 'Reddit'}
                  </span>
                ))}
              </td>
              <td className="px-2.5 py-3 border-b border-gray-100 font-semibold">
                {inc.post_count}
              </td>
              <td className="px-2.5 py-3 border-b border-gray-100">
                {inc.trend_pct != null && inc.trend_pct > 0 && (
                  <span className="text-red-600 font-semibold text-[11.5px]">
                    ▲ {inc.trend_pct.toFixed(0)}%
                  </span>
                )}
              </td>
              <td className="px-2.5 py-3 border-b border-gray-100">
                <span
                  className="inline-block px-2 py-0.5 rounded-full text-[11px] font-semibold"
                  style={{ backgroundColor: status.bg, color: status.text }}
                >
                  {status.label}
                </span>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
