"use client";

import {
  useEffect,
} from "react";

import {
  ErrorState,
} from "@/components/system";

type GlobalErrorProps = {
  error: Error & {
    digest?: string;
  };
  reset: () => void;
};

export default function GlobalError({
  error,
  reset,
}: GlobalErrorProps) {
  useEffect(
    () => {
      console.error(
        "PlantMind route error",
        error
      );
    },
    [
      error,
    ]
  );

  return (
    <main className="min-h-[calc(100vh-8rem)] min-w-0 bg-slate-950 px-4 py-8 text-slate-100 sm:px-6">
      <div className="mx-auto w-full max-w-7xl">
        <ErrorState
          title="PlantMind could not display this page"
          message="The page encountered an unexpected error. Retry the operation or return to another workspace."
          requestId={
            error.digest
              ? error.digest
              : null
          }
          retryLabel="Retry page"
          onRetry={reset}
        />
      </div>
    </main>
  );
}
