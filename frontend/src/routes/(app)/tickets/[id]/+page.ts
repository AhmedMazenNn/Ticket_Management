import { API_BASE } from '$lib/api/index';
import { auth } from '$lib/stores/auth.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const access = auth.accessToken;

	if (!access) {
		return { ticket: null };
	}

	const headers = {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${access}`
	};

	try {
		const res = await fetch(`${API_BASE}/tickets/${params.id}/`, { headers });

		if (!res.ok) {
			return { ticket: null };
		}

		const ticket = await res.json();
		return { ticket };
	} catch {
		return { ticket: null };
	}
};
