// Timeout for all API requests (ms)
export const API_TIMEOUT = 30000

/**
 * Format an ISO datetime string to a date-only string (YYYY-MM-DD).
 * Returns '—' for null/undefined values.
 */
export function formatDate(value) {
  if (!value) return '—'
  return value.slice(0, 10)
}
