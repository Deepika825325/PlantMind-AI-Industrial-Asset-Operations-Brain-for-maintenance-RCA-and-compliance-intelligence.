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

export type AskResponse = {
  question: string;
  detected_assets: string[];
  answer: string;
  answer_mode: string;
  supporting_sources: string[];
  retrieved_context: RetrievedContext[];
};