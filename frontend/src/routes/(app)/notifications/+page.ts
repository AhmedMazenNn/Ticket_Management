import { API_BASE } from '$lib/api/index';
import { auth } from '$lib/stores/auth.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
	const access = auth.accessToken;

	const page = Number(url.searchParams.get('page')) || 1;
	const filter = url.searchParams.get('filter') || 'all';

	const params = new URLSearchParams();
	params.set('page', String(page));
	if (filter === 'unread') params.set('is_read', 'false');

	if (!access) {
		return { notifications: [], count: 0, page, filter };
	}

	const headers = {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${access}`
	};

	try {
		const res = await fetch(`${API_BASE}/notifications/?${params}`, { headers });

		if (!res.ok) {
			return { notifications: [], count: 0, page, filter };
		}

		const data = await res.json();

		return {
			notifications: data.results,
			count: data.count,
			page,
			filter
		};
	} catch {
		return { notifications: [], count: 0, page, filter };
	}
};
