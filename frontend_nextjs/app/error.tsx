'use client';

import { ErrorBoundaryFallback } from './not-found';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <ErrorBoundaryFallback error={error} resetErrorBoundary={reset} />;
}

