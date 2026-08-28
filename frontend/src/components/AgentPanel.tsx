import { useState } from 'react';
import { Brain, Map, House, HeartPulse, Truck, Radio, Check, LoaderCircle, AlertTriangle, ShieldCheck, Activity, Info, X } from 'lucide-react';

const icons: Record<string, any> = {
  'Commander Agent': Brain,
  'Crisis Assessment Agent': Activity,
  'Geo Agent': Map,
  'Shelter Agent': House,
  'Medical Agent': HeartPulse,
  'Resource Agent': Truck,
  'Communication Agent': Radio,
};

const AGENT_DETAILS: Record<string, { role: string; task: string; process: string[]; outputs: string }> = {
  'Commander Agent': {
    role: 'Central Response Orchestration & Multi-Agent Consensus',
    task: 'Aggregate findings, formulate prioritized directives, coordinate replanning cycles',
    process: [
      'Ingest incident parameters and regional telemetry',
      'Delegate domain inquiries to Geo, Medical, Resource, and Shelter agents',
      'Synthesize tactical directives with confidence scoring and explainability',
      'Enforce human-in-the-loop approval gates before simulated action execution',
      'Autonomously trigger replanning cycles upon operational state changes'
    ],
    outputs: 'Versioned Response Plan with prioritized directives, explainability log, and audit trails'
  },
  'Crisis Assessment Agent': {
    role: 'Disaster Severity Scoring & Population Risk Zoning',
    task: 'Calculate hazard severity index and classify population exposure',
    process: [
      'Ingest flood water levels, precipitation rates, or seismic intensity',
      'Cross-reference affected population against municipal density charts',
      'Classify disaster severity: LOW / MEDIUM / HIGH / CRITICAL',
      'Establish priority evacuation zones and medical risk ratings'
    ],
    outputs: 'Incident severity rating, urgency classification, and priority zone designations'
  },
  'Geo Agent': {
    role: 'Geographic Topology, Road Accessibility & Safe Corridors',
    task: 'Scan road network for flood inundation and identify clear transit corridors',
    process: [
      'Scan regional road segments against hydrological flood modeling',
      'Isolate submerged, blocked, or structurally compromised road links',
      'Compute shortest safe transit corridors to highland shelters',
      'Recommend traffic perimeter blocks and bypass routes'
    ],
    outputs: 'Safe evacuation routes, blocked roads list, and corridor distance calculations'
  },
  'Medical Agent': {
    role: 'Hospital Capacity, ICU Availability & Triage Allocation',
    task: 'Monitor trauma center readiness and allocate acute emergency beds',
    process: [
      'Poll bed registries across all regional emergency hospitals',
      'Calculate available standard beds, ICU units, and active ambulances',
      'Project emergency casualty surge rates based on disaster severity',
      'Designate primary receiving trauma center and reserve bed allocations'
    ],
    outputs: 'Hospital capacity allocations, ICU bed reservations, and ambulance dispatch orders'
  },
  'Resource Agent': {
    role: 'Emergency Inventory Tracking & Multi-Zone Logistics Dispatch',
    task: 'Track relief inventories (water, food, kits) and mobilize vehicle fleets',
    process: [
      'Audit central warehouse stock: Potable Water, Rations, Trauma Kits, Boats',
      'Detect critical supply deficits and trigger procurement warnings',
      'Assign transit buses and rescue watercraft to priority evacuation zones',
      'Formulate supply convoy dispatch schedules'
    ],
    outputs: 'Asset assignments (Buses/Boats/Trucks) and supply deficit mitigation orders'
  },
  'Shelter Agent': {
    role: 'Relief Shelter Capacity Matching & Safety Grading',
    task: 'Evaluate relief shelter elevation, structural safety, and bed vacancies',
    process: [
      'Audit live occupancy sensor feeds from designated relief structures',
      'Filter out low-ground facilities vulnerable to flood water ingress',
      'Match displaced zone populations to highest-rated safe shelters',
      'Coordinate shelter opening and reception staff readiness'
    ],
    outputs: 'Primary safe shelter designations, vacancy allocations, and safety ratings'
  },
  'Communication Agent': {
    role: 'Multilingual Public Alert & Citizen Warning Broadcasts',
    task: 'Generate geo-targeted emergency advisories in English, Telugu, and Hindi',
    process: [
      'Translate commander directives into verified citizen-safe instructions',
      'Format emergency SMS broadcasts, siren scripts, and radio bulletins',
      'Ensure multilingual clarity across local linguistic demographics',
      'Coordinate with public safety media networks'
    ],
    outputs: 'Multilingual citizen alert broadcasts and public emergency advisories'
  }
};

export default function AgentPanel({ active, events }: { active: boolean; events: any[] }) {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const agentNames = [
    'Commander Agent',
    'Crisis Assessment Agent',
    'Geo Agent',
    'Shelter Agent',
    'Medical Agent',
    'Resource Agent',
    'Communication Agent'
  ];

  return (
    <>
      <div className="agent-grid">
        {agentNames.map((name) => {
          const shortName = name.replace(' Agent', '');
          const lastEvent = [...events].reverse().find(
            (e) => e.agent === name || e.agent === shortName || e.source?.includes(shortName.toUpperCase().replace(' ', '_'))
          );

          const isWorking = active && (!lastEvent || lastEvent.status === 'RUNNING' || lastEvent.status === 'WORKING');
          const isWarning = lastEvent?.status === 'WARNING';
          const isApproved = lastEvent?.status === 'APPROVED';
          const isComplete = active && !isWorking && lastEvent?.status === 'COMPLETED';

          const IconComponent = icons[name] || Brain;
          const details = AGENT_DETAILS[name];

          return (
            <button
              className={`agent-card-row ${isWorking ? 'agent-working' : ''}`}
              key={name}
              onClick={() => setSelectedAgent(name)}
            >
              <div className="agent-icon-wrapper">
                <IconComponent size={20} className={isWorking ? 'spin text-amber' : 'text-cyan'} />
              </div>

              <div className="agent-info-content">
                <div className="agent-name-role">
                  <strong>{name}</strong>
                  <span className="agent-subrole">{details?.role.split('&')[0]}</span>
                </div>
                <small className="agent-msg">
                  {lastEvent?.message || (active ? 'Executing tactical analysis...' : 'Standby — awaiting crisis input')}
                </small>
              </div>

              <div className="agent-status-col">
                <span className={`status-pill ${isWorking ? 'working' : isWarning ? 'warning' : isApproved ? 'approved' : isComplete ? 'complete' : 'waiting'}`}>
                  {isWorking ? (
                    <><LoaderCircle size={12} className="spin" /> ANALYZING</>
                  ) : isWarning ? (
                    <><AlertTriangle size={12} /> ALERT</>
                  ) : isApproved ? (
                    <><ShieldCheck size={12} /> APPROVED</>
                  ) : isComplete ? (
                    <><Check size={12} /> COMPLETED</>
                  ) : (
                    <>● STANDBY</>
                  )}
                </span>
                <span className="agent-click-hint">Inspect ➔</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <div className="modal-backdrop" onClick={() => setSelectedAgent(null)}>
          <div className="modal panel agent-modal" onClick={(e) => e.stopPropagation()}>
            <div className="panel-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span className="brand-mark">AI</span>
                <div>
                  <h2 style={{ margin: 0 }}>{selectedAgent}</h2>
                  <span className="eyebrow">{AGENT_DETAILS[selectedAgent]?.role}</span>
                </div>
              </div>
              <button className="btn btn-sm" onClick={() => setSelectedAgent(null)}><X size={16} /></button>
            </div>

            <div className="agent-modal-body">
              <div className="modal-section">
                <label className="modal-label">CURRENT OPERATIONAL TASK</label>
                <p className="task-desc">{AGENT_DETAILS[selectedAgent]?.task}</p>
              </div>

              <div className="modal-section">
                <label className="modal-label">AUTONOMOUS REASONING & EXECUTION PROCESS</label>
                <ul className="process-list">
                  {AGENT_DETAILS[selectedAgent]?.process.map((step, idx) => (
                    <li key={idx}>
                      <span className="step-num">{idx + 1}</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="modal-section">
                <label className="modal-label">DATA OUTPUTS & DIRECTIVE DELIVERABLES</label>
                <div className="output-box">{AGENT_DETAILS[selectedAgent]?.outputs}</div>
              </div>

              <div className="modal-section">
                <label className="modal-label">RECENT AGENT EXECUTION LOGS</label>
                <div className="agent-modal-logs">
                  {events
                    .filter((e) => e.agent === selectedAgent || e.agent === selectedAgent.replace(' Agent', ''))
                    .slice(-5)
                    .reverse()
                    .map((log, idx) => (
                      <div key={idx} className="log-row">
                        <time>{new Date(log.timestamp).toLocaleTimeString()}</time>
                        <b>{log.event_type}</b>
                        <p>{log.message}</p>
                      </div>
                    ))}
                  {events.filter((e) => e.agent === selectedAgent || e.agent === selectedAgent.replace(' Agent', '')).length === 0 && (
                    <div className="empty-sm">No recorded events for this agent yet.</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

