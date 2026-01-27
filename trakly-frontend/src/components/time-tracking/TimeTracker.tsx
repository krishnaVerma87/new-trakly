import { useState, useEffect } from 'react';
import { TimeLogResponse, TimeLogSummary } from '@/types';
import { timeLogService } from '@/lib/services/time-log.service';
import toast from 'react-hot-toast';
import { formatDistanceToNow } from 'date-fns';

interface TimeTrackerProps {
  issueId: string;
}

export const TimeTracker: React.FC<TimeTrackerProps> = ({ issueId }) => {
  const [timeLogs, setTimeLogs] = useState<TimeLogResponse[]>([]);
  const [summary, setSummary] = useState<TimeLogSummary | null>(null);
  const [activeTimer, setActiveTimer] = useState<TimeLogResponse | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showManualEntry, setShowManualEntry] = useState(false);
  const [manualMinutes, setManualMinutes] = useState<number>(0);
  const [manualDescription, setManualDescription] = useState('');
  const [timerDescription, setTimerDescription] = useState('');

  useEffect(() => {
    loadTimeLogs();
    loadSummary();
  }, [issueId]);

  // Update elapsed time every second when timer is active
  useEffect(() => {
    if (activeTimer) {
      const interval = setInterval(() => {
        const start = new Date(activeTimer.started_at);
        const now = new Date();
        const elapsed = Math.floor((now.getTime() - start.getTime()) / 1000);
        setElapsedTime(elapsed);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [activeTimer]);

  const loadTimeLogs = async () => {
    try {
      setLoading(true);
      const response = await timeLogService.getIssueTimeLogs(issueId);
      setTimeLogs(response.data);

      // Check if there's an active timer
      const active = response.data.find(log => !log.ended_at);
      if (active) {
        setActiveTimer(active);
      }
    } catch (error: any) {
      console.error('Error loading time logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const response = await timeLogService.getTimeSummary(issueId);
      setSummary(response.data);
    } catch (error: any) {
      console.error('Error loading time summary:', error);
    }
  };

  const handleStartTimer = async () => {
    try {
      const response = await timeLogService.startTimer(issueId, timerDescription || undefined);
      setActiveTimer(response.data);
      setTimeLogs([response.data, ...timeLogs]);
      setTimerDescription('');
      toast.success('Timer started');
    } catch (error: any) {
      toast.error(error.message || 'Failed to start timer');
    }
  };

  const handleStopTimer = async () => {
    if (!activeTimer) return;

    try {
      const response = await timeLogService.stopTimer(activeTimer.id);
      setActiveTimer(null);
      setElapsedTime(0);
      await loadTimeLogs();
      await loadSummary();
      toast.success(`Timer stopped: ${response.data.duration_minutes} minutes logged`);
    } catch (error: any) {
      toast.error(error.message || 'Failed to stop timer');
    }
  };

  const handleManualEntry = async () => {
    if (manualMinutes <= 0) {
      toast.error('Please enter a valid duration');
      return;
    }

    try {
      await timeLogService.logTime(issueId, manualMinutes, manualDescription || undefined);
      setManualMinutes(0);
      setManualDescription('');
      setShowManualEntry(false);
      await loadTimeLogs();
      await loadSummary();
      toast.success('Time logged successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to log time');
    }
  };

  const handleDeleteLog = async (logId: string) => {
    if (!confirm('Are you sure you want to delete this time log?')) return;

    try {
      await timeLogService.deleteTimeLog(logId);
      await loadTimeLogs();
      await loadSummary();
      toast.success('Time log deleted');
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete time log');
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatMinutes = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      {summary && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-blue-900">Total Time Logged</div>
              <div className="text-2xl font-bold text-blue-600">{summary.total_time_hours}h</div>
              <div className="text-xs text-blue-600 mt-1">{summary.log_count} log entries</div>
            </div>
            <div className="text-right">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      )}

      {/* Timer Controls */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Time Tracker</h3>
          <button
            onClick={() => setShowManualEntry(!showManualEntry)}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            {showManualEntry ? 'Cancel' : '+ Manual Entry'}
          </button>
        </div>

        {activeTimer ? (
          <div className="space-y-3">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-green-900">Timer Running</div>
                  <div className="text-3xl font-mono font-bold text-green-600 mt-1">
                    {formatDuration(elapsedTime)}
                  </div>
                  {activeTimer.description && (
                    <div className="text-sm text-green-700 mt-1">{activeTimer.description}</div>
                  )}
                  <div className="text-xs text-green-600 mt-1">
                    Started {formatDistanceToNow(new Date(activeTimer.started_at), { addSuffix: true })}
                  </div>
                </div>
                <button
                  onClick={handleStopTimer}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                >
                  Stop Timer
                </button>
              </div>
            </div>
          </div>
        ) : showManualEntry ? (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration (minutes)
              </label>
              <input
                type="number"
                value={manualMinutes || ''}
                onChange={(e) => setManualMinutes(parseInt(e.target.value) || 0)}
                className="input w-full"
                placeholder="e.g., 30"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description (optional)
              </label>
              <input
                type="text"
                value={manualDescription}
                onChange={(e) => setManualDescription(e.target.value)}
                className="input w-full"
                placeholder="What did you work on?"
              />
            </div>
            <button
              onClick={handleManualEntry}
              className="btn-primary w-full"
            >
              Log Time
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description (optional)
              </label>
              <input
                type="text"
                value={timerDescription}
                onChange={(e) => setTimerDescription(e.target.value)}
                className="input w-full"
                placeholder="What are you working on?"
              />
            </div>
            <button
              onClick={handleStartTimer}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Start Timer
            </button>
          </div>
        )}
      </div>

      {/* Time Log History */}
      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Time Log History</h3>
        </div>
        <div className="divide-y divide-gray-200">
          {timeLogs.filter(log => log.ended_at).length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-400">
              No time logs yet
            </div>
          ) : (
            timeLogs.filter(log => log.ended_at).map((log) => (
              <div key={log.id} className="px-4 py-3 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-blue-600">
                        {formatMinutes(log.duration_minutes || 0)}
                      </span>
                      {log.description && (
                        <span className="text-sm text-gray-600">- {log.description}</span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {log.user_name && <span>{log.user_name} · </span>}
                      {new Date(log.started_at).toLocaleString()} - {log.ended_at && new Date(log.ended_at).toLocaleString()}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteLog(log.id)}
                    className="text-red-600 hover:text-red-700 ml-2"
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
