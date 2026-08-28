import type { CrisisState } from '../types';

// Support VITE_API_URL for Render deployment, fallback to same host on port 8000
const rawBase = import.meta.env.VITE_API_URL || (window.location.port === '5173' ? `http://${window.location.hostname}:8000` : window.location.origin);
export const API_BASE = rawBase.replace(/\/+$/, '');

// Compute WebSocket URL
function getWebSocketUrl(): string {
  if (import.meta.env.VITE_API_URL) {
    const parsed = new URL(import.meta.env.VITE_API_URL);
    const wsProto = parsed.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${wsProto}//${parsed.host}/ws/crisis`;
  }
  const isSecure = window.location.protocol === 'https:';
  const wsProto = isSecure ? 'wss:' : 'ws:';
  const host = window.location.hostname || 'localhost';
  const port = window.location.port === '5173' ? '8000' : window.location.port;
  return `${wsProto}//${host}${port ? `:${port}` : ''}/ws/crisis`;
}

export async function getState(): Promise<CrisisState> {
  const res = await fetch(`${API_BASE}/api/crisis/current`);
  if (!res.ok) throw new Error('Crisis Command Center API unavailable');
  return res.json();
}

export async function getLocations() {
  const res = await fetch(`${API_BASE}/api/crisis/locations`);
  if (!res.ok) throw new Error('Location registry unavailable');
  return res.json();
}

export async function action(path: string, body?: unknown): Promise<CrisisState> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || 'Emergency command action failed');
  }
  return res.json() as Promise<CrisisState>;
}

export async function approveAction(actionId: string): Promise<CrisisState> {
  return action(`/api/actions/${encodeURIComponent(actionId)}/approve`);
}

export async function rejectAction(actionId: string, reason?: string): Promise<CrisisState> {
  return action(`/api/actions/${encodeURIComponent(actionId)}/reject`, { reason: reason || 'Rejected by operator' });
}

export async function startDemo(): Promise<CrisisState> {
  return action('/api/simulation/demo-run');
}

export function connect(onEvent: (e: any) => void): WebSocket {
  const wsUrl = getWebSocketUrl();
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onEvent(data);
    } catch {
      // ignore
    }
  };
  return ws;
}

