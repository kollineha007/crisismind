import { useState } from 'react';
import { Archive, Download, Trash2, Search, Filter, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import type { EventItem } from '../types';

export default function EventLogPanel({ events }: { events: EventItem[] }) {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const filterOptions = ['ALL', 'COMMANDER', 'GEO', 'MEDICAL', 'RESOURCE', 'SHELTER', 'WARNINGS', 'ACTIONS'];

  const filtered = events.filter((e) => {
    // Search match
    if (search.trim()) {
      const q = search.toLowerCase();
      const match = (e.message || '').toLowerCase().includes(q) ||
                    (e.event_type || '').toLowerCase().includes(q) ||
                    (e.agent || e.source || '').toLowerCase().includes(q);
      if (!match) return false;
    }

    if (filter === 'ALL') return true;
    if (filter === 'WARNINGS') return e.status === 'WARNING' || e.severity === 'WARNING';
    if (filter === 'ACTIONS') return e.event_type.includes('ACTION') || e.event_type.includes('APPROVED');
    
    const src = (e.agent || e.source || '').toUpperCase();
    return src.includes(filter);
  });

  const exportLogs = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(events, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `CrisisMind_AuditLog_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <section className="panel audit-event-log-section">
      <div className="panel-title">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Archive size={18} className="text-cyan" />
          <h2 style={{ margin: 0 }}>Persistent Event Log & Audit Trail</h2>
          <span className="badge blue">{filtered.length} Logged Events</span>
        </div>
        <button className="btn btn-sm flex-btn" onClick={exportLogs}>
          <Download size={14} /> Export Logs (JSON)
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="log-controls-bar">
        <div className="search-box">
          <Search size={14} />
          <input
            type="text"
            placeholder="Search event type, agent, or message..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="log-filter-chips">
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
      </div>

      {/* Log Table */}
      <div className="event-log-table-wrap">
        {filtered.length === 0 ? (
          <div className="empty" style={{ padding: '24px', textAlign: 'center' }}>
            No recorded system events match the selected criteria.
          </div>
        ) : (
          <table className="event-table">
            <thead>
              <tr>
                <th>TIMESTAMP</th>
                <th>EVENT TYPE</th>
                <th>AGENT / ACTOR</th>
                <th>SEVERITY</th>
                <th>DETAILS</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {[...filtered].reverse().map((evt) => {
                const isWarning = evt.status === 'WARNING' || evt.severity === 'WARNING';
                const isApproved = evt.status === 'APPROVED' || evt.event_type.includes('APPROVED');

                return (
                  <tr key={evt.id || evt.timestamp} className={isWarning ? 'row-warning' : isApproved ? 'row-approved' : ''}>
                    <td className="time-cell">
                      <Clock size={12} style={{ marginRight: 4, display: 'inline' }} />
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </td>
                    <td><b className="event-type-badge">{evt.event_type}</b></td>
                    <td>{evt.agent || evt.source?.replace('_', ' ') || 'System'}</td>
                    <td>
                      <span className={`badge ${isWarning ? 'orange' : isApproved ? 'green' : 'blue'}`}>
                        {evt.severity || 'INFO'}
                      </span>
                    </td>
                    <td className="msg-cell">{evt.message}</td>
                    <td>
                      <span className={`status-pill-sm ${evt.status?.toLowerCase() || 'completed'}`}>
                        {evt.status || 'COMPLETED'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
