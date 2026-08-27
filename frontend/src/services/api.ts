import type { CrisisState } from '../types';
const host = window.location.hostname || 'localhost';
const BASE = `http://${host}:8000`;
export async function getState():Promise<CrisisState>{const r=await fetch(`${BASE}/api/crisis/current`); if(!r.ok) throw Error('Backend unavailable'); return r.json();}
export async function getLocations(){const r=await fetch(`${BASE}/api/locations`); if(!r.ok) throw Error('Locations unavailable'); return r.json();}
export async function action(path:string, body?:unknown){const r=await fetch(`${BASE}${path}`,{method:'POST',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined}); if(!r.ok) throw Error((await r.text())||'Action failed'); return r.json() as Promise<CrisisState>;}
export function connect(onEvent:(e:any)=>void){const ws=new WebSocket(`ws://${host}:8000/ws/crisis`); ws.onmessage=e=>onEvent(JSON.parse(e.data)); return ws;}
