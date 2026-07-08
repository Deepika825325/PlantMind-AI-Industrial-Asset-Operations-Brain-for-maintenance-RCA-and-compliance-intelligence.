import type {
  RcaAssetCasesResponse,
  RcaCase,
  RcaCaseListResponse,
  RcaEvidenceResponse,
  RcaStatistics,
} from "@/lib/types";

const BROWSER_API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

const SERVER_API_BASE_URL =
  process.env.API_INTERNAL_BASE_URL ??
  BROWSER_API_BASE_URL;

export const API_BASE_URL =
  typeof window === "undefined"
    ? SERVER_API_BASE_URL
    : BROWSER_API_BASE_URL;

const API_TIMEOUT_MS = 15000;

export type ApiErrorDetails =
  | Record<string, unknown>
  | unknown[]
  | null;

type ApiRequestErrorOptions = {
  message: string;
  code: string;
  status: number | null;
  requestId: string | null;
  details?: ApiErrorDetails;
  backendUnavailable?: boolean;
  cause?: unknown;
};

export class ApiRequestError extends Error {
  readonly code: string;
  readonly status: number | null;
  readonly requestId: string | null;
  readonly details: ApiErrorDetails;
  readonly backendUnavailable: boolean;

  constructor(options: ApiRequestErrorOptions) {
    super(options.message, {
      cause: options.cause,
    });

    this.name = "ApiRequestError";
    this.code = options.code;
    this.status = options.status;
    this.requestId = options.requestId;
    this.details = options.details ?? null;
    this.backendUnavailable = options.backendUnavailable ?? false;

    Object.setPrototypeOf(
      this,
      ApiRequestError.prototype
    );
  }
}

type StructuredApiError = {
  code?: unknown;
  message?: unknown;
  request_id?: unknown;
  details?: unknown;
};

type ApiRequestOptions = Omit<
  RequestInit,
  "signal"
> & {
  timeoutMs?: number;
};

function isRecord(
  value: unknown
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function getStringValue(
  value: unknown
): string | null {
  if (
    typeof value !== "string" ||
    !value.trim()
  ) {
    return null;
  }

  return value.trim();
}

function normalizeErrorDetails(
  value: unknown
): ApiErrorDetails {
  if (
    Array.isArray(value) ||
    isRecord(value)
  ) {
    return value;
  }

  return null;
}

function isUnavailableStatus(
  status: number
): boolean {
  return [
    502,
    503,
    504,
  ].includes(status);
}

async function parseErrorResponse(
  response: Response
): Promise<ApiRequestError> {
  let payload: unknown = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  const structuredError: StructuredApiError | null =
    isRecord(payload) &&
    isRecord(payload.error)
      ? payload.error
      : null;

  const requestId =
    getStringValue(
      structuredError?.request_id
    ) ||
    getStringValue(
      response.headers.get(
        "X-Request-ID"
      )
    );

  const code =
    getStringValue(
      structuredError?.code
    ) ||
    (
      response.status === 404
        ? "RESOURCE_NOT_FOUND"
        : "API_REQUEST_FAILED"
    );

  const message =
    getStringValue(
      structuredError?.message
    ) ||
    (
      response.status === 404
        ? "The requested resource was not found."
        : (
          `PlantMind API request failed with ` +
          `status ${response.status}.`
        )
    );

  return new ApiRequestError({
    message,
    code,
    status: response.status,
    requestId,
    details: normalizeErrorDetails(
      structuredError?.details
    ),
    backendUnavailable: isUnavailableStatus(
      response.status
    ),
  });
}

function createNetworkError(
  error: unknown,
  timedOut: boolean
): ApiRequestError {
  if (timedOut) {
    return new ApiRequestError({
      message: (
        "The PlantMind backend did not respond " +
        "within the allowed time."
      ),
      code: "API_REQUEST_TIMEOUT",
      status: null,
      requestId: null,
      backendUnavailable: true,
      cause: error,
    });
  }

  return new ApiRequestError({
    message: (
      "The PlantMind backend is unavailable. " +
      "Confirm that the API service is running."
    ),
    code: "BACKEND_UNAVAILABLE",
    status: null,
    requestId: null,
    backendUnavailable: true,
    cause: error,
  });
}

async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const {
    timeoutMs = API_TIMEOUT_MS,
    headers,
    ...requestOptions
  } = options;

  const controller = new AbortController();

  let timedOut = false;

  const timeoutId = setTimeout(
    () => {
      timedOut = true;
      controller.abort();
    },
    timeoutMs
  );

  let response: Response;

  try {
    response = await fetch(
      apiUrl(path),
      {
        ...requestOptions,
        headers,
        cache: "no-store",
        signal: controller.signal,
      }
    );
  } catch (error) {
    throw createNetworkError(
      error,
      timedOut
    );
  } finally {
    clearTimeout(timeoutId);
  }

  if (!response.ok) {
    throw await parseErrorResponse(
      response
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  try {
    return await response.json() as T;
  } catch (error) {
    throw new ApiRequestError({
      message: (
        "PlantMind received an invalid " +
        "response from the backend."
      ),
      code: "INVALID_API_RESPONSE",
      status: response.status,
      requestId: response.headers.get(
        "X-Request-ID"
      ),
      backendUnavailable: false,
      cause: error,
    });
  }
}

export function apiUrl(
  path: string
): string {
  const normalizedPath = path.startsWith(
    "/"
  )
    ? path
    : `/${path}`;

  return `${API_BASE_URL}${normalizedPath}`;
}

export async function apiGet<T>(
  path: string
): Promise<T> {
  return apiRequest<T>(
    path,
    {
      method: "GET",
    }
  );
}

export async function apiPost<
  TRequest,
  TResponse
>(
  path: string,
  body: TRequest
): Promise<TResponse> {
  return apiRequest<TResponse>(
    path,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    }
  );
}

export function isApiRequestError(
  error: unknown
): error is ApiRequestError {
  return error instanceof ApiRequestError;
}

export function isBackendUnavailableError(
  error: unknown
): boolean {
  return (
    error instanceof ApiRequestError &&
    error.backendUnavailable
  );
}

export function getApiErrorMessage(
  error: unknown
): string {
  if (error instanceof ApiRequestError) {
    return error.message;
  }

  if (
    error instanceof Error &&
    error.message.trim()
  ) {
    return error.message;
  }

  return (
    "PlantMind could not complete " +
    "the requested operation."
  );
}

export function getApiErrorRequestId(
  error: unknown
): string | null {
  if (error instanceof ApiRequestError) {
    return error.requestId;
  }

  return null;
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
    searchParams.set(
      "asset_id",
      filters.assetId.trim()
    );
  }

  if (filters.severity?.trim()) {
    searchParams.set(
      "severity",
      filters.severity.trim()
    );
  }

  if (filters.incidentStatus?.trim()) {
    searchParams.set(
      "incident_status",
      filters.incidentStatus.trim()
    );
  }

  const queryString =
    searchParams.toString();

  return apiGet<RcaCaseListResponse>(
    `/rca${queryString ? `?${queryString}` : ""}`
  );
}

export async function getRcaCase(
  caseId: string
): Promise<RcaCase> {
  const normalizedCaseId =
    caseId.trim();

  if (!normalizedCaseId) {
    throw new ApiRequestError({
      message: "RCA case ID is required.",
      code: "RCA_CASE_ID_REQUIRED",
      status: null,
      requestId: null,
    });
  }

  return apiGet<RcaCase>(
    `/rca/${encodeURIComponent(
      normalizedCaseId
    )}`
  );
}

export async function getRcaStatistics():
Promise<RcaStatistics> {
  return apiGet<RcaStatistics>(
    "/rca/statistics"
  );
}

export async function getRcaCasesForAsset(
  assetId: string
): Promise<RcaAssetCasesResponse> {
  const normalizedAssetId =
    assetId.trim();

  if (!normalizedAssetId) {
    throw new ApiRequestError({
      message: "Asset ID is required.",
      code: "ASSET_ID_REQUIRED",
      status: null,
      requestId: null,
    });
  }

  return apiGet<RcaAssetCasesResponse>(
    `/rca/asset/${encodeURIComponent(
      normalizedAssetId
    )}`
  );
}

export async function getRcaEvidence(
  caseId: string,
  evidenceId: string
): Promise<RcaEvidenceResponse> {
  const normalizedCaseId =
    caseId.trim();

  const normalizedEvidenceId =
    evidenceId.trim();

  if (!normalizedCaseId) {
    throw new ApiRequestError({
      message: "RCA case ID is required.",
      code: "RCA_CASE_ID_REQUIRED",
      status: null,
      requestId: null,
    });
  }

  if (!normalizedEvidenceId) {
    throw new ApiRequestError({
      message: (
        "RCA evidence ID is required."
      ),
      code: "RCA_EVIDENCE_ID_REQUIRED",
      status: null,
      requestId: null,
    });
  }

  return apiGet<RcaEvidenceResponse>(
    `/rca/${encodeURIComponent(
      normalizedCaseId
    )}/evidence/${encodeURIComponent(
      normalizedEvidenceId
    )}`
  );
}
