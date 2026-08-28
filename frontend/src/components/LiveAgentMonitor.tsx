import { useState } from 'react';
import { Terminal, Activity, Brain, Map, House, HeartPulse, Truck, Radio, Check, LoaderCircle, AlertTriangle, ShieldCheck, Filter } from 'lucide-react';
import type { EventItem } from '../types';

const agentIcons: Record<string, any> = {
  'Commander Agent': Brain,
  'Commander': Brain,
  'Crisis Assessment Agent': Activity,
  'Crisis Assessment': Activity,
  'Geo Agent': Map,
  'Geo': Map,
  'Shelter Agent': House,
  'Shelter': House,
  'Medical Agent': HeartPulse,
  'Medical': HeartPulse,
  'Resource Agent': Truck,
  'Resource': Truck,
  'Communication Agent': Radio,
  'Communication': Radio,
  'Human Commander': ShieldCheck,
  'System': Terminal,
};

export default function LiveAgentMonitor({ events, active }: { events: EventItem[]; active: boolean }) {
  const [filter, setFilter] = useState('ALL');

  const filterOptions = ['ALL', 'COMMANDER', 'GEO', 'MEDICAL', 'RESOURCE', 'SHELTER', 'ACTIONS'];

  const filteredEvents = events.filter((e) => {
    if (filter === 'ALL') return true;
    if (filter === 'ACTIONS') return e.event_type.includes('ACTION') || e.event_type.includes('APPROVED');
    const agentMatch = (e.agent || e.source || '').toUpperCase();
    return agentMatch.includes(filter);
  });

  const latestEvents = [...filteredEvents].reverse().slice(0, 18);

  return (
    <div className="live-monitor-card">
      <div className="live-monitor-head">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div className={`status-dot ${active ? 'pulse-green' : 'standby'}`}></div>
          <span className="eyebrow" style={{ color: '#38bdf8' }}>LIVE AGENT ACTIVITY MONITOR</span>
        </div>
        <div className="monitor-badge">
          {active ? 'STREAMING REAL-TIME EVENTS' : 'AGENT NETWORK IDLE'}
        </div>
      </div>

      {/* Filter Chips */}
      <div className="filter-chips">
        {filterOptions.map((opt) => (
          <button
            key={opt}
            className={`chip-btn ${filter === opt ? 'active' : ''}`}
            onClick={() => setFilter(opt)}
          >
            {opt}
          </button>
        ))}
      </div>

      {/* Terminal Event Stream */}
      <div className="monitor-event-stream">
        {latestEvents.length === 0 ? (
          <div className="empty-stream">
            <Terminal size={22} className="text-muted" />
            <p>No recent execution events match this filter.</p>
          </div>
        ) : (
          latestEvents.map((evt, idx) => {
            const agentName = evt.agent || evt.source?.replace('_', ' ') || 'System';
            const IconComp = agentIcons[agentName] || agentIcons[evt.source] || Terminal;
            const isWorking = evt.status === 'RUNNING' || evt.status === 'WORKING';
            const isWarning = evt.status === 'WARNING';
            const isApproved = evt.status === 'APPROVED';
            const isComplete = evt.status === 'COMPLETED';

            return (
              <div key={evt.id || idx} className={`stream-item ${isWorking ? 'item-working' : isWarning ? 'item-warning' : ''}`}>
                <div className="stream-time">
                  <time>{new Date(evt.timestamp).toLocaleTimeString()}</time>
                </div>

                <div className="stream-agent-icon">
                  <IconComp size={14} className={isWorking ? 'spin text-amber' : 'text-cyan'} />
                </div>

                <div className="stream-content">
                  <div className="stream-meta">
                    <span className="stream-agent-name">{agentName}</span>
                    <span className="stream-type">[{evt.event_type}]</span>
                  </div>
                  <div className="stream-message">{evt.message}</div>
                </div>

                <div className="stream-status">
                  <span className={`pill-badge ${isWorking ? 'pill-working' : isWarning ? 'pill-warning' : isApproved ? 'pill-approved' : 'pill-complete'}`}>
                    {isWorking ? 'RUNNING' : isWarning ? 'WARNING' : isApproved ? 'APPROVED' : 'COMPLETED'}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
