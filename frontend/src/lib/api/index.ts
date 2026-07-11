/**
 * API client layer.
 *
 * All HTTP calls go through this module so that:
 * - The base URL is configured from a single env variable.
 * - Auth headers (JWT) are injected once, not per-call.
 * - Error handling / response normalisation is centralised.
 *
 * Sub-modules (to be created as apps are built):
 *   $lib/api/tickets.ts
 *   $lib/api/auth.ts
 *   $lib/api/users.ts
 *   $lib/api/dashboard.ts
 */

export const API_BASE = import.meta.env.PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';
