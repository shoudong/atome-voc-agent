'use client';

import { useEffect, useState } from 'react';
import TrendChart from '@/components/TrendChart';
import SeverityDonut from '@/components/SeverityDonut';
import { CATEGORIES } from '@/lib/constants';
import type { TrendPoint, CategoryCount, SeverityCount } from '@/lib/types';
import * as api from '@/lib/api';

export default function AnalyticsPage() {
  const [days, setDays] = useState(7);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [categories, setCategories] = useState<CategoryCount[]>([]);
  const [severity, setSeverity] = useState<{ items: SeverityCount[]; total: number } | null>(null);

  useEffect(() => {
    Promise.all([
      api.getTrend(days),
      api.getCategories(days),
      api.getSeverityDistribution(days),
    ])
      .then(([trendData, catData, sevData]) => {
        setTrend(trendData.points || []);
        setCategories(catData.items || []);
        setSeverity(sevData);
      })
      .catch(() => {});
  }, [days]);

  const maxCatCount = Math.max(...categories.map((c) => c.count), 1);

  return (
    <div>
      <div className="flex items-end justify-between mb-4">
        <div>
          <h1 className="text-[22px] font-bold text-gray-900 tracking-tight">Analytics</h1>
          <p className="text-[13px] text-gray-500 mt-1">Complaint trends and distributions</p>
        </div>
        <div className="flex gap-1.5 bg-white p-1 border border-gray-200 rounded-[10px]">
          {[{ label: '7d', value: 7 }, { label: '30d', value: 30 }, { label: '90d', value: 90 }].map((r) => (
            <button
              key={r.value}
              onClick={() => setDays(r.value)}
              className={`px-3 py-1.5 text-[12.5px] rounded-md ${
                days === r.value ? 'bg-pink-500 text-white font-semibold' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* Trend chart */}
      <div className="bg-white rounded-[14px] border border-gray-200 shadow-sm p-5 mb-4">
        <h3 className="text-sm font-bold text-gray-900 mb-3.5">Complaint volume trend</h3>
        <TrendChart data={trend} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Severity */}
        <div className="bg-white rounded-[14px] border border-gray-200 shadow-sm p-5">
          <h3 className="text-sm font-bold text-gray-900 mb-3.5">Severity distribution</h3>
          {severity && <SeverityDonut data={severity.items} total={severity.total} />}
        </div>

        {/* Categories */}
        <div className="bg-white rounded-[14px] border border-gray-200 shadow-sm p-5">
          <h3 className="text-sm font-bold text-gray-900 mb-3.5">Category breakdown</h3>
          {categories.map((cat) => {
            const label = CATEGORIES.find((c) => c.key === cat.category)?.label || cat.category;
            return (
              <div key={cat.category} className="grid grid-cols-[150px_1fr_50px] items-center gap-2.5 py-1.5 text-[13px]">
                <div className="text-gray-700 truncate">{label}</div>
                <div className="bg-gray-100 rounded h-2.5 overflow-hidden">
                  <div
                    className="h-full rounded bg-gradient-to-r from-pink-500 to-pink-300"
                    style={{ width: `${(cat.count / maxCatCount) * 100}%` }}
                  />
                </div>
                <div className="text-right font-semibold text-gray-800 text-[12.5px]">{cat.count}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
