import { API_BASE } from '$lib/api/index';
import { auth } from '$lib/stores/auth.svelte';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url, fetch }) => {
	const access = auth.accessToken;

	const page = Number(url.searchParams.get('page')) || 1;
	const search = url.searchParams.get('search') || '';
	const statusFilter = url.searchParams.get('status') || 'all';
	const priorityFilter = url.searchParams.get('priority') || 'all';
	const assigneeFilter = url.searchParams.get('assigned_to') || 'all';

	const params = new URLSearchParams();
	params.set('page', String(page));
	if (search) params.set('search', search);
	if (statusFilter !== 'all') params.set('status', statusFilter);
	if (priorityFilter !== 'all') params.set('priority', priorityFilter);
	if (assigneeFilter !== 'all') params.set('assigned_to', assigneeFilter);

	if (!access) {
		return { tickets: [], count: 0, users: [], page, search, statusFilter, priorityFilter, assigneeFilter };
	}

	const headers = {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${access}`
	};

	try {
		const [ticketsRes, usersRes] = await Promise.all([
			fetch(`${API_BASE}/tickets/?${params}`, { headers }),
			fetch(`${API_BASE}/auth/users/`, { headers })
		]);

		if (!ticketsRes.ok || !usersRes.ok) {
			return { tickets: [], count: 0, users: [], page, search, statusFilter, priorityFilter, assigneeFilter };
		}

		const ticketResponse = await ticketsRes.json();
		const users = await usersRes.json();

		return {
			tickets: ticketResponse.results,
			count: ticketResponse.count,
			users,
			page,
			search,
			statusFilter,
			priorityFilter,
			assigneeFilter
		};
	} catch {
		return { tickets: [], count: 0, users: [], page, search, statusFilter, priorityFilter, assigneeFilter };
	}
};
