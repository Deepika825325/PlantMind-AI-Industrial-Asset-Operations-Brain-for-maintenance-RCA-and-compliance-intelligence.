import {
  getApiErrorMessage,
  getApiErrorRequestId,
  isBackendUnavailableError,
} from "@/lib/api";

export type FrontendErrorState = {
  message: string;
  requestId: string | null;
  backendUnavailable: boolean;
};

export function createFrontendErrorState(
  error: unknown
): FrontendErrorState {
  return {
    message: getApiErrorMessage(error),
    requestId: getApiErrorRequestId(error),
    backendUnavailable:
      isBackendUnavailableError(error),
  };
}
