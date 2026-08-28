export interface LocationProfile {
  id: string;
  name: string;
  state: string;
  latitude: number;
  longitude: number;
  default_crisis?: string;
  severity?: string;
  affected_population?: number;
  water_level?: number;
  blocked_roads?: number;
  risk_summary?: string;
}

export interface Zone {
  name: string;
  population: number;
  severity: string;
  medical_risk: string;
  latitude: number;
  longitude: number;
  evacuation_status: string;
}

export interface Road {
  id: string;
  source: string;
  destination: string;
  distance: number;
  status: 'OPEN' | 'BLOCKED' | 'AT_RISK';
  risk_level?: string;
}

export interface Shelter {
  name: string;
  zone: string;
  latitude: number;
  longitude: number;
  capacity: number;
  occupancy: number;
  accessibility: string;
  status: string;
  safety_level: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface Hospital {
  name: string;
  latitude: number;
  longitude: number;
  total_beds: number;
  available_beds: number;
  icu_beds: number;
  ambulances: number;
  status: string;
  trauma_ready?: boolean;
}

export interface ResourceItem {
  id: string;
  type: string;
  unit?: string;
  quantity_available?: number;
  quantity_required?: number;
  location: string;
  capacity: number;
  status: 'AVAILABLE' | 'ASSIGNED' | 'UNAVAILABLE' | 'CRITICAL' | 'LOW';
  assigned_zone?: string | null;
}

export interface Recommendation {
  id: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  action: string;
  reason: string;
  agent: string;
  affected_area: string;
  affected_count?: number;
  assigned_resource?: string;
  approval_status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXECUTED';
  execution_status?: 'NOT_EXECUTED' | 'SIMULATED' | 'COMPLETED';
  what?: string;
  data_used?: string[];
  confidence?: number;
  alternatives?: string[];
  action_type?: string;
}

export interface ResponsePlan {
  version: number;
  status: string;
  created_at: string;
  recommendations: Recommendation[];
  explanation: string[];
  changes?: string[];
}

export interface EventItem {
  id: string;
  timestamp: string;
  event_type: string;
  severity: string;
  source: string;
  agent_id?: string;
  agent?: string;
  message: string;
  location: string;
  data?: any;
  status?: string;
}

export interface AgentInfo {
  name: string;
  role?: string;
  purpose?: string;
  status: 'WAITING' | 'RUNNING' | 'COMPLETED' | 'WARNING' | 'APPROVED' | 'REJECTED';
  last_message?: string;
  current_task?: string;
  execution_count?: number;
  last_started?: string;
  last_completed?: string;
}

export interface CrisisState {
  active: boolean;
  demo_mode: boolean;
  ai_mode: string;
  location: LocationProfile;
  crisis: {
    disaster_type: string;
    location: string;
    description?: string;
    water_level: number;
    affected_population: number;
    blocked_roads: number;
    reports?: string[];
  } | null;
  assessment: {
    disaster_type: string;
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    affected_population: number;
    priority_zones: string[];
    urgency: string;
    medical_risk: string;
    evacuation_required: boolean;
    reasoning: string;
  } | null;
  plan: ResponsePlan | null;
  previous_plan: ResponsePlan | null;
  data: {
    zones: Zone[];
    roads: Road[];
    shelters: Shelter[];
    hospitals: Hospital[];
    resources: ResourceItem[];
  };
  events: EventItem[];
  audit: any[];
  alerts: any[];
  reports: any[];
  agent_logs: Record<string, EventItem[]>;
  agent_states: Record<string, AgentInfo>;
  created_at: string | null;
  updated_at: string | null;
  metrics: Record<string, any>;
}