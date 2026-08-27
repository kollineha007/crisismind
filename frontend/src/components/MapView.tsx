import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
const icon = (color: string) => L.divIcon({ className: 'marker', html: `<span style="background:${color}"></span>`, iconSize: [18, 18] });
export default function MapView({ data, location }: { data: any; location?: any }) {
  const center: [number, number] = location ? [location.latitude, location.longitude] : [16.515, 80.645];
  return <MapContainer key={location?.id || 'default'} center={center} zoom={13} className="map"><TileLayer attribution="&copy; OpenStreetMap" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    {data.zones?.map((zone: any) => <><Circle key={zone.name} center={[zone.latitude, zone.longitude]} radius={350} pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: .18 }} /><Marker key={`${zone.name}-m`} position={[zone.latitude, zone.longitude]} icon={icon('#ef4444')}><Popup><b>{zone.name}</b><br />Population: {zone.population}<br />Flood level: {zone.severity}<br />Medical risk: {zone.medical_risk}</Popup></Marker></>)}
    {data.shelters?.map((shelter: any) => <Marker key={shelter.name} position={[shelter.latitude, shelter.longitude]} icon={icon('#22c55e')}><Popup><b>{shelter.name}</b><br />Capacity: {shelter.capacity}<br />Available: {shelter.capacity - shelter.occupancy}<br />{shelter.accessibility}</Popup></Marker>)}
    {data.hospitals?.map((hospital: any) => <Marker key={hospital.name} position={[hospital.latitude, hospital.longitude]} icon={icon('#38bdf8')}><Popup><b>{hospital.name}</b><br />Available beds: {hospital.available_beds}<br />ICU: {hospital.icu_beds}</Popup></Marker>)}
    {data.roads?.map((road: any) => <Polyline key={road.id} positions={[[center[0], center[1]], [center[0] + road.distance / 1000, center[1] + road.distance / 3000]]} pathOptions={{ color: road.status === 'BLOCKED' ? '#f97316' : '#38bdf8', weight: road.status === 'BLOCKED' ? 6 : 3, dashArray: road.status === 'BLOCKED' ? '4 8' : '7 6' }}><Popup><b>Road {road.id}</b><br />Status: {road.status}<br />Distance: {road.distance} km<br />{road.status === 'BLOCKED' ? 'Route unavailable' : 'Usable route'}</Popup></Polyline>)}
  </MapContainer>;
}
