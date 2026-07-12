import { API_BASE } from '$lib/api/index';
import { auth } from '$lib/stores/auth.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const access = auth.accessToken;

	if (!access) {
		return { users: [] };
	}

	const headers = {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${access}`
	};

	try {
		const res = await fetch(`${API_BASE}/auth/users/`, { headers });

		if (!res.ok) {
			return { users: [] };
		}

		const users = await res.json();
		return { users };
	} catch {
		return { users: [] };
	}
};
