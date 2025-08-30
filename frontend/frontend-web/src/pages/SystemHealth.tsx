import React, { useEffect, useMemo, useRef, useState } from 'react';
import { vantaApi, buildSystemHealthWsUrl } from '../api';

interface DbStatus {
  status?: 'ok' | 'error' | 'skipped';
  error?: string;
  reason?: string;
  latency_ms?: number;
  version?: string;
}

interface SystemMetrics {
  cpu_percent?: number;
  memory_percent?: number;
  memory_available_gb?: number;
  disk_percent?: number;
  disk_free_gb?: number;
  network_bytes_sent?: number;
  network_bytes_recv?: number;
  process_memory_mb?: number;
  load_average?: number[] | null;
  boot_time?: string;
  timestamp?: string;
}

interface SnapshotResponse {
  status: string;
  system: SystemMetrics;
  databases: {
    postgres?: DbStatus;
    mongo?: DbStatus;
    redis?: DbStatus;
    timestamp?: string;
  };
  generated_at: string;
}

export default function SystemHealth() {
  const [snapshot, setSnapshot] = useState<SnapshotResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [live, setLive] = useState<boolean>(true);
  const [aiLoading, setAiLoading] = useState<boolean>(false);
  const [aiResult, setAiResult] = useState<any | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const wsUrl = useMemo(() => buildSystemHealthWsUrl(2), []);

  // Initial fetch
  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await vantaApi.getSystemHealth();
        setSnapshot(data);
        setError(null);
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load snapshot');
      }
    };
    load();
  }, []);

  // Live WS connection
  useEffect(() => {
    if (!live) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data && data.system && data.databases) {
            setSnapshot(data);
          }
        } catch (_) {
          // ignore parse errors
        }
      };
      ws.onerror = () => {
        setError('WebSocket error');
      };
      ws.onclose = () => {
        // attempt to reconnect if still live
        if (live) {
          setTimeout(() => setLive(true), 2000);
        }
      };
    } catch (e: any) {
      setError('Failed to open WebSocket');
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [live, wsUrl]);

  const requestAI = async () => {
    setAiLoading(true);
    setAiResult(null);
    try {
      const { data } = await vantaApi.getSystemHealthAI();
      setAiResult(data);
      setError(null);
    } catch (e: any) {
      const msg = e?.response?.status === 503
        ? 'AI analysis not available (GitHub Models disabled).'
        : (e?.response?.data?.detail || e?.message || 'AI analysis failed');
      setError(msg);
    } finally {
      setAiLoading(false);
    }
  };

  const badge = (s?: DbStatus) => {
    if (!s) return <span className="px-2 py-1 rounded bg-gray-200 text-gray-700">n/a</span>;
    if (s.status === 'ok') return <span className="px-2 py-1 rounded bg-green-100 text-green-700">OK {s.latency_ms ? `(${s.latency_ms}ms)` : ''}</span>;
    if (s.status === 'skipped') return <span className="px-2 py-1 rounded bg-yellow-100 text-yellow-700">Skipped{ s.reason ? `: ${s.reason}` : ''}</span>;
    return <span className="px-2 py-1 rounded bg-red-100 text-red-700">Error{ s.error ? `: ${s.error}` : ''}</span>;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">System Health</h1>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={live} onChange={() => setLive(!live)} />
            <span>Live updates</span>
          </label>
          <button onClick={requestAI} disabled={aiLoading} className="px-3 py-2 bg-indigo-600 text-white rounded disabled:opacity-60">
            {aiLoading ? 'Analyzing…' : 'Run AI Analysis'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded bg-red-50 text-red-700 border border-red-200">{error}</div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-4 rounded border bg-white">
          <h2 className="font-medium mb-3">System Metrics</h2>
          {!snapshot ? (
            <div>Loading…</div>
          ) : (
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>CPU:</div><div>{snapshot.system.cpu_percent ?? '—'}%</div>
              <div>Memory:</div><div>{snapshot.system.memory_percent ?? '—'}% ({snapshot.system.memory_available_gb?.toFixed?.(2)} GB free)</div>
              <div>Disk:</div><div>{snapshot.system.disk_percent ?? '—'}% ({snapshot.system.disk_free_gb?.toFixed?.(2)} GB free)</div>
              <div>Network sent/recv:</div><div>{snapshot.system.network_bytes_sent ?? '—'} / {snapshot.system.network_bytes_recv ?? '—'}</div>
              <div>Process RSS:</div><div>{snapshot.system.process_memory_mb ?? '—'} MB</div>
              <div>Load avg:</div><div>{Array.isArray(snapshot.system.load_average) ? snapshot.system.load_average.join(', ') : '—'}</div>
              <div>Boot time:</div><div>{snapshot.system.boot_time ?? '—'}</div>
              <div>Updated:</div><div>{snapshot.system.timestamp ?? snapshot.generated_at}</div>
            </div>
          )}
        </div>

        <div className="p-4 rounded border bg-white">
          <h2 className="font-medium mb-3">Databases</h2>
          {!snapshot ? (
            <div>Loading…</div>
          ) : (
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between"><span>PostgreSQL</span>{badge(snapshot.databases.postgres)}</div>
              <div className="flex items-center justify-between"><span>MongoDB</span>{badge(snapshot.databases.mongo)}</div>
              <div className="flex items-center justify-between"><span>Redis</span>{badge(snapshot.databases.redis)}</div>
              <div className="text-xs text-gray-500">Checked at: {snapshot.databases.timestamp ?? snapshot.generated_at}</div>
            </div>
          )}
        </div>
      </div>

      {aiResult && (
        <div className="p-4 rounded border bg-white">
          <h2 className="font-medium mb-3">AI Analysis</h2>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(aiResult, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
