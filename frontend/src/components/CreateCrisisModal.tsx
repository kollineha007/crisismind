import { useState } from 'react';
import { AlertOctagon, X, Sparkles, MapPin, Users, Activity, FileText } from 'lucide-react';
import { action } from '../services/api';

const CRISIS_TYPES = [
  'Flood',
  'Heavy Rain & Waterlogging',
  'Coastal Cyclone & Storm Surge',
  'Earthquake & Structural Collapse',
  'Urban Fire & Industrial Hazard',
  'Severe Heatwave & AQI Surge',
  'Multi-Vehicle Transit Accident',
  'Other Emergency'
];

const SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export default function CreateCrisisModal({
  locations,
  currentLocationId,
  onClose,
  onCrisisCreated,
}: {
  locations: any[];
  currentLocationId: string;
  onClose: () => void;
  onCrisisCreated: (newState: any) => void;
}) {
  const [disasterType, setDisasterType] = useState('Flood');
  const [selectedLocId, setSelectedLocId] = useState(currentLocationId || 'vijayawada');
  const [severity, setSeverity] = useState('HIGH');
  const [affectedPopulation, setAffectedPopulation] = useState(12500);
  const [waterLevel, setWaterLevel] = useState(2.8);
  const [description, setDescription] = useState(
    'Rapid riverbank breach causing flash inundation across municipal wards. Transit routes obstructed; urgent evacuation required.'
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      // 1. Shift location if different
      if (selectedLocId !== currentLocationId) {
        await action('/api/crisis/location', { location_id: selectedLocId });
      }

      const matchedLoc = locations.find((l) => l.id === selectedLocId) || { name: selectedLocId };

      // 2. Submit crisis and start full multi-agent analysis
      const result = await action('/api/crisis/analyze', {
        disaster_type: disasterType,
        location: matchedLoc.name,
        water_level: Number(waterLevel),
        affected_population: Number(affectedPopulation),
        blocked_roads: severity === 'CRITICAL' ? 3 : severity === 'HIGH' ? 2 : 1,
        description,
      });

      onCrisisCreated(result);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to start AI crisis analysis');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal panel create-crisis-modal" onClick={(e) => e.stopPropagation()}>
        <div className="panel-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="icon-badge red">
              <AlertOctagon size={20} />
            </div>
            <div>
              <h2 style={{ margin: 0 }}>Declare Crisis Incident</h2>
              <span className="eyebrow">TRIGGER MULTI-AGENT SYNTHESIS WORKFLOW</span>
            </div>
          </div>
          <button className="btn btn-sm" onClick={onClose}><X size={16} /></button>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-row-2">
            <label className="form-field">
              <span><Activity size={14} /> Crisis Type</span>
              <select value={disasterType} onChange={(e) => setDisasterType(e.target.value)}>
                {CRISIS_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span><MapPin size={14} /> Operational Theater (Location)</span>
              <select value={selectedLocId} onChange={(e) => setSelectedLocId(e.target.value)}>
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>{loc.name}, {loc.state}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="form-row-3">
            <label className="form-field">
              <span>Severity Level</span>
              <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
                {SEVERITIES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </label>

            <label className="form-field">
              <span><Users size={14} /> Exposed Population</span>
              <input
                type="number"
                min="100"
                max="500000"
                step="100"
                value={affectedPopulation}
                onChange={(e) => setAffectedPopulation(Number(e.target.value))}
              />
            </label>

            <label className="form-field">
              <span>Water / Hazard Level (m)</span>
              <input
                type="number"
                min="0"
                max="10"
                step="0.1"
                value={waterLevel}
                onChange={(e) => setWaterLevel(Number(e.target.value))}
              />
            </label>
          </div>

          <label className="form-field">
            <span><FileText size={14} /> Incident Overview & Distress Dispatch Description</span>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter situational details..."
            />
          </label>

          <div className="modal-actions">
            <button type="button" className="btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn primary flex-btn" disabled={isSubmitting}>
              <Sparkles size={16} />
              {isSubmitting ? 'Agents Analyzing Crisis...' : 'START AI MULTI-AGENT ANALYSIS'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
