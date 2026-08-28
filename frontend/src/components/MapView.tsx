import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Custom high-contrast emergency marker generators
const createEmergencyIcon = (emoji: string, bg: string, border: string = '#ffffff') =>
  L.divIcon({
    className: 'custom-map-icon',
    html: `<div style="background:${bg}; border:2px solid ${border}; border-radius:50%; width:30px; height:30px; display:flex; align-items:center; justify-content:center; font-size:14px; box-shadow:0 0 12px ${bg}88; color:white;">${emoji}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });

const icons = {
  epicenter: createEmergencyIcon('🔴', '#ef4444', '#fee2e2'),
  criticalZone: createEmergencyIcon('⚠️', '#f97316', '#ffedd5'),
  warningZone: createEmergencyIcon('🟡', '#eab308', '#fef08a'),
  safeZone: createEmergencyIcon('🟢', '#22c55e', '#dcfce7'),
  hospital: createEmergencyIcon('🏥', '#0ea5e9', '#e0f2fe'),
  shelter: createEmergencyIcon('🏠', '#10b981', '#d1fae5'),
  resource: createEmergencyIcon('🚑', '#8b5cf6', '#ede9fe'),
};

export default function MapView({ data, location, onSelectLocation }: { data: any; location?: any; onSelectLocation?: (item: any) => void }) {
  const center: [number, number] = location ? [location.latitude, location.longitude] : [16.5062, 80.6480];

  return (
    <div className="map-wrapper" style={{ position: 'relative' }}>
      <MapContainer
        key={location?.id || 'default-map'}
        center={center}
        zoom={13}
        className="map"
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        {/* Crisis Epicenter Pin */}
        <Marker position={center} icon={icons.epicenter}>
          <Popup>
            <div className="map-popup-card">
              <span className="badge red">CRISIS EPICENTER</span>
              <h4 style={{ margin: '4px 0', fontSize: '14px' }}>{location?.name || 'Incident Sector'}</h4>
              <p style={{ margin: '3px 0', fontSize: '12px' }}>Severity: <b>{location?.severity || 'HIGH'}</b></p>
              <p style={{ margin: '3px 0', fontSize: '12px' }}>Affected Population: <b>{location?.affected_population?.toLocaleString() || '12,500'}</b></p>
            </div>
          </Popup>
        </Marker>

        {/* Zones */}
        {data?.zones?.map((zone: any) => {
          const isCritical = zone.severity === 'CRITICAL' || zone.severity === 'HIGH';
          const color = isCritical ? '#ef4444' : zone.severity === 'MEDIUM' ? '#f59e0b' : '#22c55e';
          const icon = isCritical ? icons.criticalZone : zone.severity === 'MEDIUM' ? icons.warningZone : icons.safeZone;

          return (
            <div key={zone.name}>
              <Circle
                center={[zone.latitude, zone.longitude]}
                radius={420}
                pathOptions={{ color, fillColor: color, fillOpacity: 0.22, weight: 2 }}
              />
              <Marker position={[zone.latitude, zone.longitude]} icon={icon}>
                <Popup>
                  <div className="map-popup-card">
                    <span className={`badge ${isCritical ? 'red' : 'amber'}`}>{zone.severity} RISK ZONE</span>
                    <h4 style={{ margin: '4px 0', fontSize: '14px' }}>{zone.name}</h4>
                    <div style={{ fontSize: '12px', marginTop: '6px', lineHeight: '1.6' }}>
                      <div>Exposed Population: <b>{zone.population?.toLocaleString()}</b></div>
                      <div>Medical Risk: <b>{zone.medical_risk}</b></div>
                      <div>Status: <b>{zone.evacuation_status}</b></div>
                    </div>
                  </div>
                </Popup>
              </Marker>
            </div>
          );
        })}

        {/* Shelters */}
        {data?.shelters?.map((shelter: any) => {
          const remaining = shelter.capacity - shelter.occupancy;
          const isFull = remaining <= 50;

          return (
            <Marker key={shelter.name} position={[shelter.latitude, shelter.longitude]} icon={icons.shelter}>
              <Popup>
                <div className="map-popup-card">
                  <span className={`badge ${isFull ? 'orange' : 'green'}`}>RELIEF SHELTER</span>
                  <h4 style={{ margin: '4px 0', fontSize: '14px' }}>{shelter.name}</h4>
                  <div style={{ fontSize: '12px', marginTop: '6px', lineHeight: '1.6' }}>
                    <div>Capacity: <b>{shelter.capacity?.toLocaleString()}</b></div>
                    <div>Occupancy: <b>{shelter.occupancy?.toLocaleString()}</b></div>
                    <div>Available Vacancy: <b style={{ color: '#22c55e' }}>{remaining?.toLocaleString()} beds</b></div>
                    <div>Safety Grade: <b>{shelter.safety_level || 'HIGH'}</b></div>
                    <div>Accessibility: <small>{shelter.accessibility}</small></div>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Hospitals */}
        {data?.hospitals?.map((hospital: any) => (
          <Marker key={hospital.name} position={[hospital.latitude, hospital.longitude]} icon={icons.hospital}>
            <Popup>
              <div className="map-popup-card">
                <span className="badge blue">EMERGENCY HOSPITAL</span>
                <h4 style={{ margin: '4px 0', fontSize: '14px' }}>{hospital.name}</h4>
                <div style={{ fontSize: '12px', marginTop: '6px', lineHeight: '1.6' }}>
                  <div>Available Beds: <b style={{ color: '#0ea5e9' }}>{hospital.available_beds} / {hospital.total_beds}</b></div>
                  <div>ICU Units: <b>{hospital.icu_beds}</b></div>
                  <div>Ambulances: <b>{hospital.ambulances}</b></div>
                  <div>Status: <b>{hospital.status}</b></div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Roads & Evacuation Corridors */}
        {data?.roads?.map((road: any) => {
          const isBlocked = road.status === 'BLOCKED';
          const isAtRisk = road.status === 'AT_RISK';
          const lineColor = isBlocked ? '#ef4444' : isAtRisk ? '#f59e0b' : '#06b6d4';

          return (
            <Polyline
              key={road.id}
              positions={[
                [center[0] - (road.distance * 0.003), center[1] - (road.distance * 0.003)],
                [center[0] + (road.distance * 0.004), center[1] + (road.distance * 0.004)],
              ]}
              pathOptions={{
                color: lineColor,
                weight: isBlocked ? 6 : 4,
                dashArray: isBlocked ? '6 8' : isAtRisk ? '8 6' : undefined,
                opacity: 0.85,
              }}
            >
              <Popup>
                <div className="map-popup-card">
                  <span className={`badge ${isBlocked ? 'red' : isAtRisk ? 'orange' : 'green'}`}>
                    {road.status === 'BLOCKED' ? 'ROAD BLOCKED' : road.status === 'AT_RISK' ? 'ROUTE AT RISK' : 'SAFE CORRIDOR'}
                  </span>
                  <h4 style={{ margin: '4px 0', fontSize: '13px' }}>{road.id}</h4>
                  <p style={{ margin: '4px 0', fontSize: '12px' }}>
                    Segment: <b>{road.source}</b> ➔ <b>{road.destination}</b>
                  </p>
                  <p style={{ margin: '2px 0', fontSize: '12px' }}>Distance: <b>{road.distance} km</b></p>
                </div>
              </Popup>
            </Polyline>
          );
        })}
      </MapContainer>

      {/* Map Legend */}
      <div className="map-legend">
        <span className="legend-item"><span className="dot red"></span> 🔴 Crisis / Blocked</span>
        <span className="legend-item"><span className="dot amber"></span> 🟠 High Risk</span>
        <span className="legend-item"><span className="dot green"></span> 🟢 Safe Zone</span>
        <span className="legend-item"><span className="dot blue"></span> 🏥 Hospital</span>
        <span className="legend-item"><span className="dot teal"></span> 🏠 Shelter</span>
        <span className="legend-item"><span className="dot cyan"></span> 🛣 Safe Route</span>
      </div>
    </div>
  );
}

