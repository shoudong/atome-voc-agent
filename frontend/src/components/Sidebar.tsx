'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  {
    section: 'Monitor',
    items: [
      { href: '/overview', label: 'Overview', badge: null },
      { href: '/incidents', label: 'Incidents', badge: null },
      { href: '/alerts', label: 'Alerts', badge: null },
      { href: '/analytics', label: 'Analytics', badge: null },
    ],
  },
  {
    section: 'Manage',
    items: [
      { href: '/feedback', label: 'Feedback queue', badge: null },
      { href: '/taxonomy', label: 'Taxonomy', badge: null },
      { href: '/routing', label: 'Routing matrix', badge: null },
      { href: '/settings', label: 'Settings', badge: null },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="bg-white border-r border-gray-200 px-3.5 py-5 sticky top-0 h-screen overflow-y-auto">
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-2 pb-4 border-b border-gray-100 mb-3.5">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-pink-500 to-pink-700 flex items-center justify-center text-white font-extrabold text-[15px] shadow-[0_2px_6px_rgba(240,53,106,0.35)]">
          A
        </div>
        <div>
          <div className="font-bold text-[15px] text-gray-900 leading-tight">Atome VoC</div>
          <div className="text-[11px] text-gray-500">PH &middot; Early Warning</div>
        </div>
      </div>

      {navItems.map((section) => (
        <div key={section.section}>
          <div className="text-[11px] uppercase tracking-wider text-gray-400 px-2 pt-3.5 pb-1.5">
            {section.section}
          </div>
          {section.items.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13.5px] mb-0.5 transition-colors ${
                  active
                    ? 'bg-pink-50 text-pink-700 font-semibold'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      ))}
    </aside>
  );
}
