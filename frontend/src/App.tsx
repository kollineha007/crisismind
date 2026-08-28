import { useCallback, useEffect, useState } from 'react';
import { NavLink, Route, Routes } from 'react-router-dom';
import { Activity, AlertTriangle, Archive, BarChart3, Building2, House, LayoutDashboard, Map as MapIcon, Shield, Truck, Play, PlusCircle, Sparkles, Terminal, Info } from 'lucide-react';
import { getState, startDemo } from './services/api';
import { useCrisisWebSocket } from './hooks/useCrisisWebSocket';
import { Dashboard, CrisisPage, MapPage, AgentsPage, ResourcesPage, SheltersPage, HospitalsPage, AlertsPage, AuditPage, MetricsPage, MonitorPage } from './pages/Pages';
import CreateCrisisModal from './components/CreateCrisisModal';

const nav = [
  ['Dashboard', '/dashboard', LayoutDashboard],
  ['Active Crisis', '/crisis', AlertTriangle],
  ['Map Operations', '/map', MapIcon],
  ['Agent Network', '/agents', Activity],
  ['Resources', '/resources', Truck],
  ['Shelters', '/shelters', House],
  ['Hospitals', '/hospitals', Building2],
  ['Alert Center', '/alerts', Shield],
  ['Audit Trail', '/audit', Archive],
  ['Metrics', '/metrics', BarChart3],
  ['System Monitor', '/monitor', Terminal],
] as const;

export default function App() {
  const [state, setState] = useState<any>(null);
  const [error, setError] = useState('');
  const [wsStatus, setWsStatus] = useState<'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING'>('RECONNECTING');
  const [isDemoRunning, setIsDemoRunning] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [locations, setLocations] = useState<any[]>([]);

  const refresh = useCallback((next: any) => setState(next), []);
  const updateWsStatus = useCallback((status: 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING') => setWsStatus(status), []);

  useEffect(() => {
    getState()
      .then((s) => {
        setState(s);
        fetch(`${import.meta.env.VITE_API_URL || (window.location.port === '5173' ? `http://${window.location.hostname}:8000` : window.location.origin)}/api/crisis/locations`)
          .then((r) => r.json())
          .then(setLocations)
          .catch(() => undefined);
      })
      .catch(() => setError('CrisisMind backend service initializing... (Start FastAPI on port 8000)'));
  }, []);

  useCrisisWebSocket(refresh, updateWsStatus);

  const handleRunDemo = async () => {
    setIsDemoRunning(true);
    try {
      const updated = await startDemo();
      setState(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setIsDemoRunning(false);
    }
  };

  if (!state) {
    return (
      <div className="app loading-screen">
        <div className="loading-box">
          <div className="brand-mark pulse-glow">✦</div>
          <h2>Initializing CrisisMind AI Command Center...</h2>
          <p>Connecting to multi-agent orchestrator & telemetry pipeline</p>
          {error && <span className="error-text">{error}</span>}
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Top Banner - Simulated Data Disclaimer for Judges */}
      <div className="sim-disclaimer-banner">
        <span><b>AI EXPO DEMONSTRATION PROTOTYPE:</b> System uses simulated disaster telemetry to exhibit autonomous multi-agent coordination, explainable planning & human oversight. Future versions support live government GIS, sensor feeds & hospital APIs.</span>
      </div>

      {/* Top Navigation Bar */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">✦</div>
          <div>
            <div className="brand-title">
              CRISIS MIND
              <span className="brand-badge">AGENTIC AI</span>
            </div>
            <small>AI CRISIS COMMAND CENTER</small>
          </div>
        </div>

        {/* Action Controls in Header */}
        <div className="header-actions">
          <button
            className="btn btn-demo flex-btn"
            disabled={isDemoRunning}
            onClick={handleRunDemo}
            title="Run complete 1-click autonomous multi-agent demonstration"
          >
            <Play size={14} className={isDemoRunning ? 'spin' : ''} />
            {isDemoRunning ? 'RUNNING DEMO SEQUENCE...' : 'START DEMO'}
          </button>

          <button
            className="btn primary flex-btn"
            onClick={() => setShowCreateModal(true)}
          >
            <PlusCircle size={14} /> + CREATE CRISIS
          </button>
        </div>

        {/* Live System Status Telemetry */}
        <div className="top-meta">
          <span className="online">SYSTEM OPERATIONAL</span>
          <span className="telemetry-pill">WS: {wsStatus}</span>
          <span className="telemetry-pill ai-mode">{state.ai_mode}</span>
          {state.active && (
            <span className="badge red pulse-badge">
              ACTIVE CRISIS: {state.crisis?.disaster_type?.toUpperCase()}
            </span>
          )}
        </div>
      </header>

      {/* Main Shell */}
      <div className="shell">
        <aside className="sidebar">
          <div className="nav-label">COMMAND CENTER CONSOLE</div>
          {nav.map(([name, path, Icon]) => (
            <NavLink className="nav-item" to={path} key={path}>
              <Icon size={16} />
              <span>{name}</span>
            </NavLink>
          ))}

          <div className="sidebar-agent-summary">
            <div className="sidebar-agent-title">
              <Sparkles size={13} color="#a855f7" /> AGENT ORCHESTRATION
            </div>
            <div className="sidebar-agent-list">
              <span className="agent-pill">Commander</span>
              <span className="agent-pill">Geo</span>
              <span className="agent-pill">Medical</span>
              <span className="agent-pill">Resource</span>
              <span className="agent-pill">Shelter</span>
            </div>
          </div>

          <div className="footer-note">
            <Info size={13} style={{ marginBottom: 4 }} />
            AI-generated recommendations are decision-support outputs. Critical emergency actions require authorization by trained human personnel.
          </div>
        </aside>

        <main className="main">
          {error && <div className="error">{error}</div>}
          <Routes>
            <Route path="/" element={<Dashboard state={state} setState={setState} onOpenCreateModal={() => setShowCreateModal(true)} onRunDemo={handleRunDemo} />} />
            <Route path="/dashboard" element={<Dashboard state={state} setState={setState} onOpenCreateModal={() => setShowCreateModal(true)} onRunDemo={handleRunDemo} />} />
            <Route path="/crisis" element={<CrisisPage state={state} setState={setState} onOpenCreateModal={() => setShowCreateModal(true)} />} />
            <Route path="/map" element={<MapPage state={state} />} />
            <Route path="/agents" element={<AgentsPage state={state} />} />
            <Route path="/resources" element={<ResourcesPage state={state} setState={setState} />} />
            <Route path="/shelters" element={<SheltersPage state={state} setState={setState} />} />
            <Route path="/hospitals" element={<HospitalsPage state={state} setState={setState} />} />
            <Route path="/alerts" element={<AlertsPage state={state} setState={setState} />} />
            <Route path="/audit" element={<AuditPage state={state} />} />
            <Route path="/metrics" element={<MetricsPage state={state} />} />
            <Route path="/monitor" element={<MonitorPage state={state} wsStatus={wsStatus} />} />
          </Routes>
        </main>
      </div>

      {/* Modal for Creating Custom Crisis */}
      {showCreateModal && (
        <CreateCrisisModal
          locations={locations.length ? locations : [state.location]}
          currentLocationId={state.location.id}
          onClose={() => setShowCreateModal(false)}
          onCrisisCreated={(newState) => setState(newState)}
        />
      )}
    </div>
  );
}

