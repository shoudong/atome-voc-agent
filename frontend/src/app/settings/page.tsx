'use client';

import { useState } from 'react';
import * as api from '@/lib/api';

export default function SettingsPage() {
  const [crawlStatus, setCrawlStatus] = useState<string | null>(null);

  const handleCrawl = async (platform: string) => {
    try {
      setCrawlStatus(`Starting ${platform} crawl...`);
      const result = await api.triggerCrawl(platform, 24);
      setCrawlStatus(result.message || 'Crawl started');
    } catch {
      setCrawlStatus('Failed to start crawl. Is the backend running?');
    }
  };

  return (
    <div>
      <div className="mb-4">
        <h1 className="text-[22px] font-bold text-gray-900 tracking-tight">Settings</h1>
        <p className="text-[13px] text-gray-500 mt-1">System configuration and manual operations</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Crawl controls */}
        <div className="bg-white rounded-[14px] border border-gray-200 shadow-sm p-5">
          <h3 className="text-sm font-bold text-gray-900 mb-3.5">Manual Crawl</h3>
          <p className="text-xs text-gray-600 mb-4">
            Trigger a crawl job manually. Automated crawls run at 8 AM and 8 PM PHT.
          </p>
          <div className="flex gap-2 mb-3">
            <button
              onClick={() => handleCrawl('reddit')}
              className="px-4 py-2 bg-[#FF4500] text-white rounded-lg text-sm font-semibold hover:opacity-90"
            >
              Crawl Reddit
            </button>
            <button
              onClick={() => handleCrawl('twitter')}
              className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-semibold hover:opacity-90"
            >
              Crawl X/Twitter
            </button>
            <button
              onClick={() => handleCrawl('all')}
              className="px-4 py-2 bg-pink-500 text-white rounded-lg text-sm font-semibold hover:opacity-90"
            >
              Crawl All
            </button>
          </div>
          {crawlStatus && (
            <div className="text-xs text-gray-600 bg-gray-50 rounded p-2">{crawlStatus}</div>
          )}
        </div>

        {/* System info */}
        <div className="bg-white rounded-[14px] border border-gray-200 shadow-sm p-5">
          <h3 className="text-sm font-bold text-gray-900 mb-3.5">System Info</h3>
          <div className="space-y-2 text-[13px]">
            <div className="flex justify-between py-1.5 border-b border-gray-100">
              <span className="text-gray-500">Brand</span>
              <span className="font-semibold">atome_ph</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-gray-100">
              <span className="text-gray-500">Market</span>
              <span className="font-semibold">Philippines</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-gray-100">
              <span className="text-gray-500">Platforms</span>
              <span className="font-semibold">X/Twitter + Reddit</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-gray-100">
              <span className="text-gray-500">LLM Model</span>
              <span className="font-semibold">Claude Sonnet</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-gray-100">
              <span className="text-gray-500">Crawl Schedule</span>
              <span className="font-semibold">8 AM, 8 PM PHT</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-gray-500">Digest Schedule</span>
              <span className="font-semibold">9 AM PHT</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
