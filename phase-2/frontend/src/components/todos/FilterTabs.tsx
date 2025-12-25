'use client';

import type { StatusFilter } from '@/types';

interface FilterTabsProps {
  activeFilter: StatusFilter;
  onFilterChange: (filter: StatusFilter) => void;
  counts?: {
    all: number;
    remaining: number;
    completed: number;
  };
}

const filters: { value: StatusFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'remaining', label: 'Remaining' },
  { value: 'completed', label: 'Completed' },
];

export default function FilterTabs({ activeFilter, onFilterChange, counts }: FilterTabsProps) {
  return (
    <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
      {filters.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => onFilterChange(value)}
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            activeFilter === value
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          aria-pressed={activeFilter === value}
        >
          {label}
          {counts && (
            <span className="ml-1.5 text-xs text-gray-400">
              ({counts[value]})
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
