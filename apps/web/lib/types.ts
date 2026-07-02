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
