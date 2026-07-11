import { API_BASE } from '$lib/api/index';
import { auth } from '$lib/stores/auth.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const access = auth.accessToken;

	if (!access) {
		return { ticket: null, users: [] };
	}

	const headers = {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${access}`
	};

	try {
		const [ticketRes, usersRes] = await Promise.all([
			fetch(`${API_BASE}/tickets/${params.id}/`, { headers }),
			fetch(`${API_BASE}/auth/users/`, { headers })
		]);

		if (!ticketRes.ok) {
			return { ticket: null, users: [] };
		}

		const ticket = await ticketRes.json();
		const users = usersRes.ok ? await usersRes.json() : [];
		return { ticket, users };
	} catch {
		return { ticket: null, users: [] };
	}
};
