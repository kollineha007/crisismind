import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AlertTriangle,
  Play,
  RotateCcw,
  Sparkles,
  PlusCircle,
  Shield,
  Truck,
  Building2,
  House,
  Activity,
  Layers,
  MapPin,
  Flame,
  CheckCircle,
  XCircle,
  ExternalLink
} from 'lucide-react';
import MapView from '../components/MapView';
import PlanPanel from '../components/PlanPanel';
import AgentPanel from '../components/AgentPanel';
import LiveAgentMonitor from '../components/LiveAgentMonitor';
import EventLogPanel from '../components/EventLogPanel';
import { action, getLocations, startDemo } from '../services/api';

function Page({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <>
      <div className="headline">
        <div>
          <span className="eyebrow">COMMAND CENTER MODULE</span>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </>
  );
}

function RoadModal({ roads, onClose, onDone }: any) {
  const available = roads.filter((road: any) => road.status !== 'BLOCKED');
  const [roadId, setRoadId] = useState(available[0]?.id || '');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    if (!roadId) {
      setError('No roads available to block.');
      return;
    }
    setSubmitting(true);
    try {
      const result: any = await action(`/api/routes/${encodeURIComponent(roadId)}/block`);
      onDone(result.state || result);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Unable to block road');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal panel" onClick={(e) => e.stopPropagation()}>
        <div className="panel-title">
          <h2>Simulate Road Obstruction</h2>
          <button className="btn btn-sm" onClick={onClose}>Cancel</button>
        </div>
        {available.length ? (
          <>
            <label className="modal-label">
              Select Road Segment to Obstruct
              <select value={roadId} onChange={(e) => setRoadId(e.target.value)}>
                {available.map((road: any) => (
                  <option key={road.id} value={road.id}>
                    {road.id} ({road.source} ➔ {road.destination})
                  </option>
                ))}
              </select>
            </label>
            <p className="modal-help-text">
              Blocking a road will update the geospatial network and autonomously trigger the Commander Agent to re-plan alternate evacuation routes.
            </p>
            <button className="btn warning flex-btn" disabled={submitting} onClick={submit}>
              <Flame size={14} /> {submitting ? 'Updating Topology...' : 'Enforce Roadblock'}
            </button>
          </>
        ) : (
          <p className="error">All road segments in this sector are already obstructed.</p>
        )}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
}

export function Dashboard({ state, setState, onOpenCreateModal, onRunDemo }: any) {
  const navigate = useNavigate();
  const [roadModal, setRoadModal] = useState(false);
  const [locations, setLocations] = useState<any[]>([]);
  const [isEscalating, setIsEscalating] = useState(false);

  const data = state.data || { zones: [], roads: [], shelters: [], hospitals: [], resources: [] };

  useEffect(() => {
    getLocations().then(setLocations).catch(() => undefined);
  }, []);

  const availableResources = data.resources.filter((r: any) => r.status === 'AVAILABLE').length;
  const availableBeds = data.hospitals.reduce((sum: number, h: any) => sum + (h.available_beds || 0), 0);
  const openRoutes = data.roads.filter((r: any) => r.status === 'OPEN').length;

  const handleLocationChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const locId = e.target.value;
    if (locId === 'custom') {
      const name = prompt('Enter City / Operational Theater Name:');
      if (name) {
        setState(await action('/api/crisis/location', { location_id: `custom:${name}` }));
      }
    } else {
      setState(await action('/api/crisis/location', { location_id: locId }));
    }
  };

  const handleSimulateShift = async () => {
    setIsEscalating(true);
    try {
      const updated = await action('/api/simulation/shift-state');
      setState(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setIsEscalating(false);
    }
  };

  const cards = [
    ['CRISIS SEVERITY', state.assessment?.severity || (state.active ? 'HIGH' : 'STANDBY'), state.assessment?.severity === 'CRITICAL' ? 'red' : 'amber', '/crisis'],
    ['EXPOSED POPULATION', state.crisis ? `${state.crisis.affected_population?.toLocaleString()} residents` : `${state.location?.affected_population?.toLocaleString() || '12,500'} baseline`, 'cyan', '/crisis'],
    ['SAFE EVAC ROUTES', `${openRoutes} / ${data.roads.length} Open`, 'green', '/map'],
    ['SHELTER HEADROOM', `${state.metrics?.shelter_utilization || 0}% Occupied`, 'amber', '/shelters'],
    ['TRAUMA BEDS FREE', `${availableBeds} Available`, 'blue', '/hospitals'],
  ];

  return (
    <>
      {/* Dashboard Headline & Controls */}
      <div className="headline">
        <div>
          <span className="eyebrow">
            {state.active ? 'LIVE CRISIS OPERATIONS' : 'COMMAND THEATER OVERVIEW'}
          </span>
          <h1>
            {state.active
              ? `${state.crisis.disaster_type} Response — ${state.location.name}`
              : `${state.location.name} Emergency Sector`}
          </h1>
          <p>
            {state.active
              ? state.location.risk_summary || 'Multi-agent decision support & explainable planning active'
              : 'Standby mode. Trigger an incident simulation or switch operational theater.'}
          </p>

          {/* Location Selector with Distinct Cities */}
          <div className="location-control-row">
            <label className="location-control">
              <MapPin size={14} /> SELECT LOCATION
              <select value={state.location.id} onChange={handleLocationChange}>
                {locations.map((loc: any) => (
                  <option key={loc.id} value={loc.id}>
                    {loc.name}, {loc.state} — ({loc.default_crisis || 'Emergency'})
                  </option>
                ))}
                <option value="custom">+ Custom Location</option>
              </select>
            </label>
          </div>
        </div>

        {/* Interactive Tactical Controls */}
        <div className="controls">
          <button
            className="btn btn-demo flex-btn"
            onClick={onRunDemo}
            title="Start 1-click end-to-end multi-agent demonstration"
          >
            <Play size={14} /> START DEMO
          </button>

          <button
            className="btn primary flex-btn"
            onClick={() => onOpenCreateModal?.()}
          >
            <PlusCircle size={14} /> + Create Crisis
          </button>

          <button
            className="btn warning flex-btn"
            disabled={!state.active || isEscalating}
            onClick={handleSimulateShift}
            title="Simulate flood water surge and road obstruction to trigger autonomous replanning"
          >
            <Flame size={14} /> {isEscalating ? 'Re-Planning...' : 'Simulate Situation Shift'}
          </button>

          <button
            className="btn warning flex-btn"
            disabled={!state.active}
            onClick={() => setRoadModal(true)}
          >
            Block Road
          </button>

          <button
            className="btn flex-btn"
            onClick={async () => setState(await action('/api/crisis/reset'))}
          >
            <RotateCcw size={14} /> Reset
          </button>
        </div>
      </div>

      {roadModal && <RoadModal roads={data.roads} onClose={() => setRoadModal(false)} onDone={setState} />}

      {/* KPI Cards */}
      <section className="kpis">
        {cards.map(([label, value, color, path]) => (
          <button className="kpi" key={label} onClick={() => navigate(path)}>
            <label>{label}</label>
            <strong className={color}>{value}</strong>
          </button>
        ))}
      </section>

      {/* Main Command Center Layout */}
      <div className="layout">
        {/* Left Column: Interactive Map & Plan Directives */}
        <div className="layout-left">
          <section className="panel map-panel">
            <div className="panel-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Layers size={18} className="text-cyan" />
                <h2>{state.location.name} Tactical Map Operations</h2>
              </div>
              <span className={`badge ${state.active ? 'green' : 'blue'}`}>
                {state.active ? 'LIVE INCIDENT TELEMETRY' : 'SIMULATED DATASET'}
              </span>
            </div>
            <MapView data={data} location={state.location} />
          </section>

          {/* AI Recommended Response Plan with Human In The Loop Approvals */}
          <section className="panel">
            <PlanPanel state={state} onUpdateState={setState} />
          </section>
        </div>

        {/* Right Column: Live Agent Activity Stream & Agent Network */}
        <div className="layout-right">
          <section className="panel">
            <div className="panel-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Activity size={18} className="text-purple" />
                <h2>Agent Network Status</h2>
              </div>
              <span className="badge purple">7 SPECIALIZED AGENTS</span>
            </div>
            <AgentPanel active={state.active} events={state.events} />
          </section>

          <section className="panel">
            <LiveAgentMonitor events={state.events} active={state.active} />
          </section>
        </div>
      </div>

      {/* Bottom Full-Width Event Log & Audit Trail */}
      <EventLogPanel events={state.events} />
    </>
  );
}

export function CrisisPage({ state, setState, onOpenCreateModal }: any) {
  const blocked = state.data.roads.filter((road: any) => road.status === 'BLOCKED');

  return (
    <Page title="Active Crisis Incident" subtitle={`${state.location.name} tactical incident intelligence`}>
      <section className="panel detail-grid">
        {[
          ['Incident Status', state.active ? 'ACTIVE CRISIS' : 'STANDBY / NO ACTIVE INCIDENT'],
          ['Operational Theater', state.location.name],
          ['Hazard Type', state.crisis?.disaster_type || state.location.default_crisis || 'Flood'],
          ['Severity Grade', state.assessment?.severity || state.location.severity || 'HIGH'],
          ['Water / Hazard Intensity', state.crisis ? `${state.crisis.water_level}m` : `${state.location.water_level || 2.4}m`],
          ['Exposed Demographics', state.crisis ? `${state.crisis.affected_population?.toLocaleString()} residents` : `${state.location.affected_population?.toLocaleString()} baseline`],
          ['Obstructed Road Corridors', `${blocked.length} Blocked`],
          ['Plan Generation State', state.plan ? `Plan v${state.plan.version} (${state.plan.status})` : 'Awaiting Synthesis'],
        ].map(([label, value]) => (
          <div className="detail" key={label}>
            <label>{label}</label>
            <strong>{value}</strong>
          </div>
        ))}
      </section>

      {/* Blocked Road Action List */}
      {blocked.length > 0 && (
        <section className="panel">
          <div className="panel-title">
            <h2>Obstructed Route Segments</h2>
            <span className="badge red">{blocked.length} Blocked</span>
          </div>
          {blocked.map((road: any) => (
            <div className="road-status" key={road.id}>
              <strong>🚧 {road.id} ({road.source} ➔ {road.destination})</strong>
              <span>STATUS: BLOCKED ({road.distance} km)</span>
              <button
                className="btn btn-sm success"
                onClick={async () => setState(await action(`/api/routes/${encodeURIComponent(road.id)}/open`))}
              >
                Clear & Re-Open Road
              </button>
            </div>
          ))}
        </section>
      )}

      {/* Quick Crisis Creation Trigger */}
      <section className="panel">
        <span className="eyebrow">CRISIS DECLARATION</span>
        <h2>Declare New Emergency Incident</h2>
        <p style={{ color: '#8fa3ad', fontSize: '13px', margin: '6px 0 16px' }}>
          Instantly simulate a new disaster scenario across any operational sector and trigger the multi-agent network.
        </p>
        <button className="btn primary flex-btn" onClick={() => onOpenCreateModal?.()}>
          <PlusCircle size={16} /> Open Crisis Declaration Form
        </button>
      </section>

      <EventLogPanel events={state.events} />
    </Page>
  );
}

export function MapPage({ state }: any) {
  return (
    <Page title="Geospatial Map Operations" subtitle={`${state.location.name} shared topological map and evacuation routes`}>
      <section className="panel map-full">
        <MapView data={state.data} location={state.location} />
      </section>
    </Page>
  );
}

export function AgentsPage({ state }: any) {
  return (
    <Page title="Agent Network & Telemetry" subtitle="Inspect live reasoning, execution steps, and deliverables for each agent">
      <section className="panel">
        <AgentPanel active={state.active} events={state.events} />
      </section>
      <section className="panel">
        <LiveAgentMonitor events={state.events} active={state.active} />
      </section>
      <EventLogPanel events={state.events} />
    </Page>
  );
}

function Table({ headers, rows }: any) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {headers.map((header: string) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row: any[], index: number) => (
            <tr key={index}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ResourcesPage({ state, setState }: any) {
  return (
    <Page title="Emergency Resource Logistics" subtitle="Track supply inventories, shortage alerts, and vehicle fleet deployments">
      <Table
        headers={['ASSET / ITEM', 'TYPE', 'DEPOT LOCATION', 'AVAILABLE', 'REQUIRED', 'STATUS', 'ASSIGNMENT', 'ACTION']}
        rows={state.data.resources.map((r: any) => [
          <b>{r.id}</b>,
          r.type,
          r.location,
          `${r.quantity_available !== undefined ? r.quantity_available : r.capacity} ${r.unit || 'units'}`,
          `${r.quantity_required || r.capacity} ${r.unit || 'units'}`,
          <span className={`badge ${r.status === 'AVAILABLE' ? 'green' : r.status === 'ASSIGNED' ? 'blue' : r.status === 'CRITICAL' ? 'red' : 'orange'}`}>
            {r.status}
          </span>,
          r.assigned_zone || 'Unassigned Reserve',
          <button
            className={`btn btn-sm ${r.status === 'ASSIGNED' ? 'warning' : 'success'}`}
            onClick={async () =>
              setState(
                await action(
                  `/api/resources/${encodeURIComponent(r.id)}/${r.status === 'ASSIGNED' ? 'release' : 'assign'}`,
                  r.status === 'ASSIGNED' ? undefined : { zone: 'Priority Evac Sector' }
                )
              )
            }
          >
            {r.status === 'ASSIGNED' ? 'Release Asset' : 'Dispatch'}
          </button>,
        ])}
      />
    </Page>
  );
}

export function SheltersPage({ state, setState }: any) {
  return (
    <Page title="Relief Shelter Directory" subtitle="Capacity tracking, occupancy rates, and safety certifications">
      <Table
        headers={['SHELTER NAME', 'SECTOR', 'TOTAL CAPACITY', 'OCCUPANCY', 'AVAILABLE BEDS', 'SAFETY GRADE', 'STATUS', 'ACTION']}
        rows={state.data.shelters.map((s: any) => {
          const rem = s.capacity - s.occupancy;
          return [
            <b>{s.name}</b>,
            s.zone,
            `${s.capacity?.toLocaleString()} beds`,
            `${s.occupancy?.toLocaleString()} evacuees`,
            <span style={{ color: rem > 100 ? '#22c55e' : '#f97316', fontWeight: 600 }}>{rem?.toLocaleString()} beds</span>,
            <span className={`badge ${s.safety_level === 'HIGH' ? 'green' : s.safety_level === 'MEDIUM' ? 'amber' : 'red'}`}>{s.safety_level || 'HIGH'}</span>,
            <span className={`badge ${s.status === 'OPEN' ? 'green' : 'orange'}`}>{s.status}</span>,
            <button
              className="btn btn-sm primary"
              onClick={async () => {
                const count = Number(prompt(`Evacuees to allocate to ${s.name} (Max ${rem}):`, '100'));
                if (count) {
                  setState(await action(`/api/shelters/${encodeURIComponent(s.name)}/allocate`, { people: count }));
                }
              }}
            >
              Allocate Evacuees
            </button>,
          ];
        })}
      />
    </Page>
  );
}

export function HospitalsPage({ state, setState }: any) {
  return (
    <Page title="Hospital & Medical Trauma Center Capacity" subtitle="Audited bed availability, ICU bays, and emergency ambulance assets">
      <Table
        headers={['FACILITY NAME', 'AVAILABLE BEDS', 'TOTAL CAPACITY', 'ICU UNITS', 'AMBULANCES', 'TRAUMA STATUS', 'STATUS', 'ACTION']}
        rows={state.data.hospitals.map((h: any) => [
          <b>{h.name}</b>,
          <span style={{ color: '#0ea5e9', fontWeight: 600 }}>{h.available_beds} beds free</span>,
          `${h.total_beds} beds`,
          `${h.icu_beds} ICU Bays`,
          `${h.ambulances} Ambulances`,
          <span className={`badge ${h.trauma_ready ? 'green' : 'orange'}`}>{h.trauma_ready ? 'TRAUMA READY' : 'GENERAL'}</span>,
          <span className={`badge ${h.status === 'OPERATIONAL' ? 'green' : 'orange'}`}>{h.status}</span>,
          <button
            className="btn btn-sm primary"
            onClick={async () => {
              const count = Number(prompt(`Beds to reserve at ${h.name} (Max ${h.available_beds}):`, '5'));
              if (count) {
                setState(await action(`/api/hospitals/${encodeURIComponent(h.name)}/reserve`, { beds: count }));
              }
            }}
          >
            Reserve Beds
          </button>,
        ])}
      />
    </Page>
  );
}

export function AlertsPage({ state, setState }: any) {
  const [language, setLanguage] = useState('English');
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async (lang: string) => {
    setGenerating(true);
    try {
      const updated = await action('/api/alerts/generate', {
        language: lang,
        context: `${state.crisis?.disaster_type || 'Flood'} emergency in ${state.location.name}; mandatory evacuation in progress`,
      });
      setState(updated);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Page title="Multilingual Citizen Emergency Broadcasts" subtitle="Operator-verified emergency advisories in English, Telugu, and Hindi">
      <div className="panel">
        <h2>Generate Verified Public Alert</h2>
        <p style={{ color: '#8fa3ad', fontSize: '13px' }}>
          Select language to synthesize targeted emergency instructions based on verified safe corridors and shelter assignments.
        </p>
        <div className="controls" style={{ marginTop: '14px' }}>
          {['English', 'Telugu', 'Hindi'].map((lang) => (
            <button
              key={lang}
              className={`btn ${language === lang ? 'primary' : ''}`}
              disabled={generating}
              onClick={() => {
                setLanguage(lang);
                handleGenerate(lang);
              }}
            >
              Broadcast in {lang}
            </button>
          ))}
        </div>
      </div>

      <div className="alerts-feed">
        {state.alerts.map((alert: any) => (
          <div className="panel alert-card" key={alert.id}>
            <div className="alert-card-head">
              <span className="badge red">{alert.type} — {alert.priority}</span>
              <span className="badge blue">{alert.language}</span>
              <time style={{ marginLeft: 'auto', color: '#718590', fontSize: '11px' }}>
                {new Date(alert.created_at).toLocaleTimeString()}
              </time>
            </div>
            <h3 style={{ margin: '10px 0', fontSize: '16px', lineHeight: '1.5' }}>{alert.message}</h3>
            <div className="alert-card-foot">
              <small>Distribution: SMS Gateway, Siren Systems, Radio Broadcasts</small>
              <span className="badge green">STATUS: ACTIVE</span>
            </div>
          </div>
        ))}
      </div>
    </Page>
  );
}

export function AuditPage({ state }: any) {
  return (
    <Page title="Auditable Decision History & Traceability" subtitle="Cryptographically traceable record of all agent deliberations and operator approvals">
      <EventLogPanel events={state.events} />
    </Page>
  );
}

export function MetricsPage({ state }: any) {
  return (
    <Page title="Telemetry & Performance Metrics" subtitle="Real-time multi-agent execution telemetry and crisis containment indicators">
      <section className="kpis metric-kpis">
        {Object.entries(state.metrics || {}).map(([key, value]) => (
          <div className="kpi" key={key}>
            <label>{key.replace(/_/g, ' ')}</label>
            <strong className="cyan">{String(value)}</strong>
          </div>
        ))}
      </section>
    </Page>
  );
}

export function MonitorPage({ state, wsStatus }: any) {
  return (
    <Page title="System Infrastructure & Network Health" subtitle="Live backend server telemetry, WebSocket status, and AI engine status">
      <section className="kpis metric-kpis">
        <div className="kpi">
          <label>API SERVER</label>
          <strong className="green">ONLINE</strong>
        </div>
        <div className="kpi">
          <label>WEBSOCKET CONNECTION</label>
          <strong className={wsStatus === 'CONNECTED' ? 'green' : 'amber'}>{wsStatus}</strong>
        </div>
        <div className="kpi">
          <label>AI ENGINE</label>
          <strong className="blue">{state.ai_mode}</strong>
        </div>
        <div className="kpi">
          <label>DATABASE</label>
          <strong>IN-MEMORY CACHE</strong>
        </div>
      </section>

      <section className="panel">
        <LiveAgentMonitor events={state.events} active={state.active} />
      </section>
    </Page>
  );
}

