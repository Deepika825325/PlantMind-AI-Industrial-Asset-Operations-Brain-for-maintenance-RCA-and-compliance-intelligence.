import type {
  RcaAssetCasesResponse,
  RcaCase,
  RcaCaseListResponse,
  RcaEvidenceResponse,
  RcaStatistics,
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}

export async function apiPost<TRequest, TResponse>(
  path: string,
  body: TRequest
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}

export type RcaCaseQuery = {
  assetId?: string;
  severity?: string;
  incidentStatus?: string;
};

export async function getRcaCases(
  filters: RcaCaseQuery = {}
): Promise<RcaCaseListResponse> {
  const searchParams = new URLSearchParams();

  if (filters.assetId?.trim()) {
    searchParams.set("asset_id", filters.assetId.trim());
  }

  if (filters.severity?.trim()) {
    searchParams.set("severity", filters.severity.trim());
  }

  if (filters.incidentStatus?.trim()) {
    searchParams.set(
      "incident_status",
      filters.incidentStatus.trim()
    );
  }

  const queryString = searchParams.toString();

  return apiGet<RcaCaseListResponse>(
    `/rca${queryString ? `?${queryString}` : ""}`
  );
}

export async function getRcaCase(
  caseId: string
): Promise<RcaCase> {
  const normalizedCaseId = caseId.trim();

  if (!normalizedCaseId) {
    throw new Error("RCA case ID is required");
  }

  return apiGet<RcaCase>(
    `/rca/${encodeURIComponent(normalizedCaseId)}`
  );
}

export async function getRcaStatistics(): Promise<RcaStatistics> {
  return apiGet<RcaStatistics>("/rca/statistics");
}

export async function getRcaCasesForAsset(
  assetId: string
): Promise<RcaAssetCasesResponse> {
  const normalizedAssetId = assetId.trim();

  if (!normalizedAssetId) {
    throw new Error("Asset ID is required");
  }

  return apiGet<RcaAssetCasesResponse>(
    `/rca/asset/${encodeURIComponent(normalizedAssetId)}`
  );
}

export async function getRcaEvidence(
  caseId: string,
  evidenceId: string
): Promise<RcaEvidenceResponse> {
  const normalizedCaseId = caseId.trim();
  const normalizedEvidenceId = evidenceId.trim();

  if (!normalizedCaseId) {
    throw new Error("RCA case ID is required");
  }

  if (!normalizedEvidenceId) {
    throw new Error("RCA evidence ID is required");
  }

  return apiGet<RcaEvidenceResponse>(
    `/rca/${encodeURIComponent(
      normalizedCaseId
    )}/evidence/${encodeURIComponent(normalizedEvidenceId)}`
  );
}