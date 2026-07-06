export type Asset = {
  asset_id: string;
  asset_name: string;
  asset_type: string;
  risk_score: number;
  health_score: number;
  risk_level: string;
  sensor_status: string;
  compliance_status: string;
  total_compliance_gaps: number;
  open_or_delayed_work_orders: string[];
  connected_sensors: string[];
  critical_story: string;
  source_documents: string[];
  pid_reference: string;
};

export type SensorSignal = {
  sensor_name: string;
  latest_value: number;
  unit: string;
  latest_status: string;
  trend_direction: string;
  source_dataset?: string;
};

export type HealthScore = {
  asset_id: string;
  asset_name: string;
  asset_type: string;
  risk_score: number;
  health_score: number;
  health_label: string;
  risk_level: string;
  sensor_status: string;
  sensor_signals: SensorSignal[];
  summary: string;
};

export type MaintenanceEvent = {
  event_id: string;
  asset_id: string;
  asset_name: string;
  event_type: string;
  priority: string;
  status: string;
  created_date: string;
  due_date: string;
  description: string;
  linked_document: string;
  compliance_related: string;
};

export type DashboardSummary = {
  total_assets: number;
  high_risk_assets: string[];
  medium_risk_assets?: string[];
  low_risk_assets?: string[];
  total_compliance_gaps: number;
  high_severity_gaps: string[];
  medium_severity_gaps?: string[];
  open_work_orders?: string[];
  delayed_work_orders?: string[];
  knowledge_graph_nodes: number;
  knowledge_graph_edges: number;
  demo_story: string;
};

export type KnowledgeGraphSummary = {
  node_count: number;
  edge_count: number;
};

export type DashboardOverview = {
  summary: DashboardSummary;
  assets: Asset[];
  health_scores: HealthScore[];
  top_maintenance_events: MaintenanceEvent[];
  knowledge_graph?: KnowledgeGraphSummary;
};

export type AskRequest = {
  question: string;
  asset_id?: string | null;
  top_k: number;
};

export type RetrievedContext = {
  score: number;
  chunk_id: string;
  document_id: string;
  document_title: string;
  document_type: string;
  section_title: string;
  asset_ids: string[];
  tags: string[];
  relative_path: string;
  chunk_text: string;
};

export type Citation = {
  citation_id: string;
  document_id: string;
  document_title: string;
  document_type: string;
  section_title: string;
  relative_path: string;
  evidence_excerpt: string;
};

export type AskResponse = {
  question: string;
  detected_assets: string[];
  answer_type: string;
  answer: string;
  answer_mode: string;
  confidence_score: number;
  supporting_sources: string[];
  citations: Citation[];
  retrieved_context: RetrievedContext[];
  suggested_followups: string[];
};

export type PidNodeType =
  | "Asset"
  | "Valve"
  | "Instrument"
  | "Line";

export type PidNode = {
  id: string;
  label: string;
  type: PidNodeType;
  asset_id?: string;
  x_percent: number;
  y_percent: number;
  status: string;
  risk_level: string;
  description: string;
};

export type PidConnection = {
  source: string;
  target: string;
  relationship: string;
};

export type PidResponse = {
  pid_id: string;
  title: string;
  description: string;
  image_url: string;
  nodes: PidNode[];
  connections: PidConnection[];
};

export type GraphNode = {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  relationship: string;
  properties: Record<string, unknown>;
};

export type KnowledgeGraphResponse = {
  artifact: string;
  generated_at: string;
  node_count: number;
  edge_count: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type RcaTopRootCause = {
  cause_id: string;
  title: string;
  category: string;
  confidence: number;
};

export type RcaCaseSummary = {
  case_id: string;
  title: string;
  asset_id: string;
  asset_name: string;
  asset_type: string;
  incident_status: string;
  severity: string;
  detected_at: string;
  problem_statement: string;
  summary: string;
  overall_confidence: number;
  top_root_cause: RcaTopRootCause | null;
  timeline_event_count: number;
  causal_chain_step_count: number;
  root_cause_count: number;
  corrective_action_count: number;
  evidence_count: number;
};

export type RcaCaseFilters = {
  asset_id: string | null;
  severity: string | null;
  incident_status: string | null;
};

export type RcaCaseListResponse = {
  artifact: string;
  generated_at: string;
  total_count: number;
  filtered_count: number;
  filters: RcaCaseFilters;
  cases: RcaCaseSummary[];
};

export type RcaTimelineEvent = {
  event_id: string;
  timestamp: string;
  event_type: string;
  title: string;
  description: string;
  severity: string;
  evidence_ids: string[];
};

export type RcaCausalStep = {
  step_id: string;
  sequence: number;
  category: string;
  title: string;
  description: string;
  confidence: number;
  evidence_ids: string[];
};

export type RcaRootCause = {
  rank: number;
  cause_id: string;
  title: string;
  category: string;
  confidence: number;
  reasoning: string;
  evidence_ids: string[];
  counter_evidence: string[];
};

export type RcaCorrectiveAction = {
  action_id: string;
  priority: string;
  title: string;
  description: string;
  owner_role: string;
  status: string;
  due_in_hours: number;
  linked_cause_ids: string[];
  verification_metric: string;
};

export type RcaEvidence = {
  evidence_id: string;
  document_id: string;
  document_title: string;
  document_type: string;
  section_title: string;
  excerpt: string;
  relative_path: string;
};

export type RcaCase = {
  case_id: string;
  title: string;
  asset_id: string;
  asset_name: string;
  asset_type: string;
  incident_status: string;
  severity: string;
  detected_at: string;
  problem_statement: string;
  summary: string;
  overall_confidence: number;
  symptoms: string[];
  timeline: RcaTimelineEvent[];
  causal_chain: RcaCausalStep[];
  root_causes: RcaRootCause[];
  corrective_actions: RcaCorrectiveAction[];
  evidence: RcaEvidence[];
  recommendation_summary: string;
};

export type RcaStatistics = {
  total_cases: number;
  average_confidence: number;
  total_root_causes: number;
  total_corrective_actions: number;
  total_evidence_items: number;
  severity_counts: Record<string, number>;
  status_counts: Record<string, number>;
  asset_counts: Record<string, number>;
};

export type RcaEvidenceResponse = {
  case_id: string;
  asset_id: string;
  evidence: RcaEvidence;
};

export type RcaAssetCasesResponse = {
  asset_id: string;
  case_count: number;
  cases: RcaCase[];
};

export type MaintenancePriority =
  | "Critical"
  | "High"
  | "Medium"
  | "Low";

export type MaintenanceStatus =
  | "Open"
  | "Delayed"
  | "In Progress"
  | "Planned"
  | "Completed"
  | "Cancelled";

export type MaintenanceType =
  | "Corrective"
  | "Condition-Based"
  | "Verification"
  | "Predictive"
  | "Preventive";

export type MaintenanceWorkOrder = {
  work_order_id: string;
  asset_id: string;
  title: string;
  description: string;
  maintenance_type: MaintenanceType;
  priority: MaintenancePriority;
  status: MaintenanceStatus;
  created_at: string;
  due_at: string;
  owner_role: string;
  source_type: string;
  source_id: string;
  linked_rca_case_id: string | null;
  linked_root_cause_ids: string[];
  linked_evidence_ids: string[];
  risk_score: number;
  confidence: number;
  required_procedure: string;
  safety_requirements: string[];
  parts_required: string[];
  estimated_duration_hours: number;
  verification_metric: string;
  completion_notes: string | null;
};

export type MaintenanceWorkOrderFilters = {
  asset_id: string | null;
  priority: string | null;
  status: string | null;
  maintenance_type: string | null;
  rca_case_id: string | null;
  due_date: string | null;
  due_before: string | null;
  due_after: string | null;
};

export type MaintenanceWorkOrdersResponse = {
  total: number;
  work_orders: MaintenanceWorkOrder[];
  filters: MaintenanceWorkOrderFilters;
};

export type MaintenanceStatistics = {
  total_work_orders: number;
  open_work_orders: number;
  overdue_work_orders: number;
  high_risk_work_orders: number;
  rca_linked_work_orders: number;
  average_risk_score: number;
  average_confidence: number;
  status_counts: Record<string, number>;
  priority_counts: Record<string, number>;
  maintenance_type_counts: Record<string, number>;
  asset_counts: Record<string, number>;
};

export type MaintenanceRecommendation = {
  rank: number;
  work_order_id: string;
  asset_id: string;
  title: string;
  priority: MaintenancePriority;
  status: MaintenanceStatus;
  risk_score: number;
  confidence: number;
  due_at: string;
  owner_role: string;
  linked_rca_case_id: string | null;
  recommendation: string;
};

export type MaintenanceRecommendationsResponse = {
  total: number;
  asset_id: string | null;
  recommendations: MaintenanceRecommendation[];
};

export type MaintenanceFilterState = {
  assetId: string;
  priority: string;
  status: string;
  maintenanceType: string;
  rcaCaseId: string;
  dueDate: string;
};