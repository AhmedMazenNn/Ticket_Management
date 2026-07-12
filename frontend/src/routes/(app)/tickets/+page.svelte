<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import { api } from '$lib/api/client';
	import { parseApiError } from '$lib/api/errors';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
	import Pagination from '$lib/components/ui/Pagination.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import { TICKET_PRIORITIES, TICKET_STATUSES } from '$lib/constants';
	import type { Ticket } from '$lib/types/ticket';
	import type { User } from '$lib/types/user';

	let { data } = $props();

	let tickets = $derived(data.tickets);
	let count = $derived(data.count);
	let users = $derived(data.users);
	let currentPage = $derived(data.page);
	let search = $derived(data.search);
	let statusFilter = $derived(data.statusFilter);
	let priorityFilter = $derived(data.priorityFilter);
	let assigneeFilter = $derived(data.assigneeFilter);

	let deleteTicket = $state<Ticket | null>(null);
	let deleteError = $state('');

	function getUserInitials(user: { first_name: string; last_name: string; email: string }): string {
		return (
			`${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase() ||
			user.email[0].toUpperCase()
		);
	}

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function updateParam(key: string, value: string) {
		const url = new URL(page.url);
		if (value && value !== '' && value !== 'all') {
			url.searchParams.set(key, value);
		} else {
			url.searchParams.delete(key);
		}
		url.searchParams.delete('page');
		goto(url.toString(), { invalidateAll: true, replaceState: true });
	}

	function handleSearch(e: Event) {
		const target = e.target as HTMLInputElement;
		const url = new URL(page.url);
		if (target.value) {
			url.searchParams.set('search', target.value);
		} else {
			url.searchParams.delete('search');
		}
		url.searchParams.delete('page');
		goto(url.toString(), { invalidateAll: true, replaceState: true });
	}

	function handlePageChange(p: number) {
		const url = new URL(page.url);
		url.searchParams.set('page', String(p));
		goto(url.toString(), { invalidateAll: true, replaceState: true });
	}

	async function confirmDelete() {
		if (!deleteTicket) return;
		deleteError = '';
		try {
			await api.deleteTicket(deleteTicket.id);
			deleteTicket = null;
			invalidateAll();
		} catch (err) {
			const parsed = parseApiError(err);
			deleteError = parsed.message;
		}
	}

	const statusOptions = [
		{ value: 'all', label: 'All statuses' },
		...TICKET_STATUSES.map((s) => ({ value: s.value, label: s.label }))
	];

	const priorityOptions = [
		{ value: 'all', label: 'All priorities' },
		...TICKET_PRIORITIES.map((p) => ({ value: p.value, label: p.label }))
	];

	const assigneeOptions = [
		{ value: 'all', label: 'All assignees' },
		...users.map((u: User) => ({
			value: u.id,
			label: u.first_name ? `${u.first_name} ${u.last_name}` : u.email
		}))
	];
</script>

<AppShell title="Tickets" subtitle="Track, prioritize, and resolve work across your organization.">
	<Card className="overflow-hidden">
		<div
			class="flex flex-col gap-3 border-b border-slate-200 p-4 lg:flex-row lg:items-center lg:justify-between"
		>
			<div class="relative min-w-0 flex-1 lg:max-w-sm">
				<svg
					class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<circle cx="11" cy="11" r="8" />
					<path d="M21 21l-4.35-4.35" />
				</svg>
				<input
					value={search}
					oninput={handleSearch}
					class="h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm outline-none placeholder:text-slate-400 focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100"
					placeholder="Search by title..."
				/>
			</div>
			<div class="flex flex-wrap gap-2">
				<Select
					label="Status"
					value={statusFilter}
					options={statusOptions}
					onchange={(v) => updateParam('status', v)}
				/>
				<Select
					label="Priority"
					value={priorityFilter}
					options={priorityOptions}
					onchange={(v) => updateParam('priority', v)}
				/>
				<Select
					label="Assignee"
					value={assigneeFilter}
					options={assigneeOptions}
					onchange={(v) => updateParam('assigned_to', v)}
				/>
				<a href="/tickets/new">
					<Button>
						<svg
							class="h-4 w-4"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M12 5v14M5 12h14" />
						</svg>
						Create ticket
					</Button>
				</a>
			</div>
		</div>

		{#if deleteError}
			<div class="mx-4 mt-4 rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700">
				{deleteError}
			</div>
		{/if}

		{#if tickets.length === 0}
			<div class="px-6 py-16 text-center text-sm text-slate-400">No tickets found.</div>
		{:else}
			<div class="overflow-x-auto">
				<table class="min-w-[800px] w-full text-left">
					<thead class="bg-slate-50 text-xs font-semibold text-slate-500">
						<tr>
							<th class="whitespace-nowrap px-5 py-3.5">ID</th>
							<th class="whitespace-nowrap px-5 py-3.5">Title</th>
							<th class="whitespace-nowrap px-5 py-3.5">Priority</th>
							<th class="whitespace-nowrap px-5 py-3.5">Status</th>
							<th class="whitespace-nowrap px-5 py-3.5">Assignee</th>
							<th class="whitespace-nowrap px-5 py-3.5">Created</th>
							<th class="whitespace-nowrap px-5 py-3.5">Updated</th>
							<th class="px-5 py-3.5"></th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-100">
						{#each tickets as ticket (ticket.id)}
							<tr class="group hover:bg-slate-50">
								<td class="px-5 py-4 text-xs font-semibold text-blue-600">
									{ticket.id.slice(0, 8)}
								</td>
								<td class="max-w-[300px] px-5 py-4">
									<a
										href="/tickets/{ticket.id}"
										class="block max-w-full truncate text-sm font-semibold text-slate-700 hover:text-blue-600"
									>
										{ticket.title}
									</a>
								</td>
								<td class="px-5 py-4">
									<Badge value={ticket.priority} type="priority" />
								</td>
								<td class="px-5 py-4">
									<Badge value={ticket.status} type="status" />
								</td>
								<td class="px-5 py-4">
									{#if ticket.assigned_to}
										<span class="flex items-center gap-2 whitespace-nowrap text-sm text-slate-600">
											<Avatar initials={getUserInitials(ticket.assigned_to)} size="sm" />
											{ticket.assigned_to.first_name}
											{ticket.assigned_to.last_name}
										</span>
									{:else}
										<span class="text-xs text-slate-400">Unassigned</span>
									{/if}
								</td>
								<td class="whitespace-nowrap px-5 py-4 text-sm text-slate-500">
									{formatDate(ticket.created_at)}
								</td>
								<td class="whitespace-nowrap px-5 py-4 text-sm text-slate-500">
									{formatDate(ticket.updated_at)}
								</td>
								<td class="px-5 py-4">
									<div class="flex items-center gap-1">
										<a
											href="/tickets/{ticket.id}"
											class="rounded-lg px-2.5 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100"
										>
											View
										</a>
										<a
											href="/tickets/{ticket.id}/edit"
											class="rounded-lg px-2.5 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50"
										>
											Edit
										</a>
										<button
											type="button"
											onclick={() => {
												deleteTicket = ticket;
												deleteError = '';
											}}
											class="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600"
											aria-label="Delete ticket"
										>
											<svg
												class="h-4 w-4"
												viewBox="0 0 24 24"
												fill="none"
												stroke="currentColor"
												stroke-width="1.5"
											>
												<path
													d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
												/>
												<line x1="10" y1="11" x2="10" y2="17" />
												<line x1="14" y1="11" x2="14" y2="17" />
											</svg>
										</button>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}

		<div
			class="flex flex-col gap-3 border-t border-slate-200 px-5 py-4 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between"
		>
			<span>
				Showing <b class="text-slate-700">{tickets.length}</b> of {count}
				tickets
			</span>
			<Pagination current={currentPage} total={count} onchange={handlePageChange} />
		</div>
	</Card>
</AppShell>

<ConfirmDialog
	open={deleteTicket !== null}
	title={`Delete ${deleteTicket?.id.slice(0, 8) ?? 'ticket'}?`}
	description="This will permanently remove the ticket. This action cannot be undone."
	onclose={() => (deleteTicket = null)}
	onconfirm={confirmDelete}
/>
