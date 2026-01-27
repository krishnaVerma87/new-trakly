import { useEffect, useState } from 'react';
import { dashboardService, BugTrendsData } from '@/lib/services/dashboard.service';
import toast from 'react-hot-toast';

interface BugTrendsChartProps {
  projectId?: string;
  days?: number;
}

export const BugTrendsChart: React.FC<BugTrendsChartProps> = ({ projectId, days = 30 }) => {
  const [data, setData] = useState<BugTrendsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(days);

  useEffect(() => {
    loadTrends();
  }, [projectId, timeRange]);

  const loadTrends = async () => {
    try {
      setLoading(true);
      const response = await dashboardService.getBugTrends(projectId, timeRange);
      setData(response.data);
    } catch (error: any) {
      toast.error('Failed to load bug trends');
      console.error('Error loading bug trends:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) return null;

  const maxValue = Math.max(
    ...data.timeline.map(d => Math.max(d.created, d.resolved)),
    1
  );

  // Simple line chart dimensions
  const width = 800;
  const height = 300;
  const padding = { top: 20, right: 20, bottom: 60, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Sample points for visualization (show every nth point for clarity)
  const sampleRate = Math.max(1, Math.floor(data.timeline.length / 30));
  const sampledData = data.timeline.filter((_, i) => i % sampleRate === 0);

  const getX = (index: number) => (index / (sampledData.length - 1 || 1)) * chartWidth + padding.left;
  const getY = (value: number) => height - padding.bottom - (value / maxValue) * chartHeight;

  // Generate path for created line
  const createdPath = sampledData.map((d, i) =>
    `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.created)}`
  ).join(' ');

  // Generate path for resolved line
  const resolvedPath = sampledData.map((d, i) =>
    `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(d.resolved)}`
  ).join(' ');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Bug Trend Analysis</h2>
          <p className="text-sm text-gray-500 mt-1">
            Bugs created vs resolved over time
          </p>
        </div>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="input text-sm"
        >
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
          <option value={30}>Last 30 days</option>
          <option value={60}>Last 60 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600">Total Open Bugs</div>
          <div className="text-2xl font-bold text-red-600 mt-1">{data.total_open}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600">Created (Period)</div>
          <div className="text-2xl font-bold text-orange-600 mt-1">
            {data.timeline.reduce((sum, d) => sum + d.created, 0)}
          </div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600">Resolved (Period)</div>
          <div className="text-2xl font-bold text-green-600 mt-1">
            {data.timeline.reduce((sum, d) => sum + d.resolved, 0)}
          </div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-sm text-gray-600">Net Change</div>
          <div className={`text-2xl font-bold mt-1 ${
            data.timeline.reduce((sum, d) => sum + d.created - d.resolved, 0) > 0
              ? 'text-red-600'
              : 'text-green-600'
          }`}>
            {data.timeline.reduce((sum, d) => sum + d.created - d.resolved, 0) > 0 ? '+' : ''}
            {data.timeline.reduce((sum, d) => sum + d.created - d.resolved, 0)}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <svg width={width} height={height} className="w-full">
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
            const y = height - padding.bottom - ratio * chartHeight;
            return (
              <g key={ratio}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 10}
                  y={y + 4}
                  textAnchor="end"
                  className="text-xs fill-gray-500"
                >
                  {Math.round(maxValue * ratio)}
                </text>
              </g>
            );
          })}

          {/* X-axis labels (show first, middle, last) */}
          {[0, Math.floor(sampledData.length / 2), sampledData.length - 1].map((index) => {
            if (index >= sampledData.length) return null;
            const d = sampledData[index];
            return (
              <text
                key={index}
                x={getX(index)}
                y={height - padding.bottom + 20}
                textAnchor="middle"
                className="text-xs fill-gray-600"
              >
                {new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </text>
            );
          })}

          {/* Created line */}
          <path
            d={createdPath}
            fill="none"
            stroke="#f59e0b"
            strokeWidth="2"
          />

          {/* Resolved line */}
          <path
            d={resolvedPath}
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
          />

          {/* Legend */}
          <g transform={`translate(${width - padding.right - 150}, ${padding.top})`}>
            <rect x="0" y="0" width="15" height="3" fill="#f59e0b" />
            <text x="20" y="5" className="text-xs fill-gray-700">Created</text>

            <rect x="0" y="15" width="15" height="3" fill="#10b981" />
            <text x="20" y="20" className="text-xs fill-gray-700">Resolved</text>
          </g>
        </svg>
      </div>

      {/* Breakdown by Severity and Priority */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* By Severity */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Open Bugs by Severity</h3>
          <div className="space-y-2">
            {Object.entries(data.by_severity).map(([severity, count]) => (
              <div key={severity} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 capitalize">{severity}</span>
                <span className="font-semibold text-gray-900">{count}</span>
              </div>
            ))}
            {Object.keys(data.by_severity).length === 0 && (
              <p className="text-sm text-gray-400">No open bugs</p>
            )}
          </div>
        </div>

        {/* By Priority */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Open Bugs by Priority</h3>
          <div className="space-y-2">
            {Object.entries(data.by_priority).map(([priority, count]) => (
              <div key={priority} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 capitalize">{priority}</span>
                <span className="font-semibold text-gray-900">{count}</span>
              </div>
            ))}
            {Object.keys(data.by_priority).length === 0 && (
              <p className="text-sm text-gray-400">No open bugs</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
