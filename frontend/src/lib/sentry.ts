import { browser } from '$app/environment';
import * as Sentry from '@sentry/sveltekit';

export function initSentry() {
	if (!browser) return;

	const dsn = import.meta.env.PUBLIC_SENTRY_DSN;
	if (!dsn) return;

	Sentry.init({
		dsn,
		environment: import.meta.env.PUBLIC_SENTRY_ENVIRONMENT || 'development',
		tracesSampleRate: 1.0
	});
}
