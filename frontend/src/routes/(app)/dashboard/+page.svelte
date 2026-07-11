<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import { auth } from '$lib/stores/auth.svelte';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Chart from '$lib/components/ui/Chart.svelte';
	import type { Ticket } from '$lib/types/ticket';

	let loading = $state(true);
	let greeting = $state('');
	let total = $state(0);
	let openCount = $state(0);
	let inProgress = $state(0);
	let closed = $state(0);
	let recentTickets = $state<Ticket[]>([]);
	let priorityLow = $state(0);
	let priorityMedium = $state(0);
	let priorityHigh = $state(0);

	onMount(async () => {
		if (!auth.isAuthenticated) {
			goto('/login');
			return;
		}
		try {
			const user = await api.me();
			const hour = new Date().getHours();
			const name = user.first_name || user.email.split('@')[0];
			greeting =
				hour < 12
					? `Good morning, ${name}`
					: hour < 18
						? `Good afternoon, ${name}`
						: `Good evening, ${name}`;

			const stats = await api.getDashboardStats();
			total = stats.total;
			openCount = stats.open;
			inProgress = stats.in_progress;
			closed = stats.closed;
			recentTickets = stats.recent_tickets;
			priorityLow = stats.priority_breakdown.low;
			priorityMedium = stats.priority_breakdown.medium;
			priorityHigh = stats.priority_breakdown.high;
		} catch {
			auth.clear();
			goto('/login');
		} finally {
			loading = false;
		}
	});

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric'
		});
	}
</script>

{#if loading}
	<div class="flex min-h-screen items-center justify-center bg-slate-50">
		<svg class="h-8 w-8 animate-spin text-blue-600" viewBox="0 0 24 24" fill="none">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
			/>
		</svg>
	</div>
{:else}
	<AppShell title={greeting} subtitle="Here's what needs your attention today.">
		<div class="grid gap-3 sm:gap-4 grid-cols-2 lg:grid-cols-4">
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">Total tickets</p>
				<p class="mt-2 text-2xl sm:text-3xl font-bold text-slate-950">{total}</p>
				<p class="mt-1 text-xs text-slate-400">All time</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">Open tickets</p>
				<p class="mt-2 text-2xl sm:text-3xl font-bold text-blue-600">{openCount}</p>
				<p class="mt-1 text-xs text-slate-400">Awaiting action</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">In progress</p>
				<p class="mt-2 text-2xl sm:text-3xl font-bold text-amber-600">{inProgress}</p>
				<p class="mt-1 text-xs text-slate-400">Being worked on</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">Closed tickets</p>
				<p class="mt-2 text-2xl sm:text-3xl font-bold text-emerald-600">{closed}</p>
				<p class="mt-1 text-xs text-slate-400">Completed</p>
			</div>
		</div>

		<div class="mt-4 grid gap-4 sm:mt-6 sm:gap-6 lg:grid-cols-2">
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
				<h2 class="text-sm font-semibold text-slate-900">Tickets by status</h2>
				<p class="mt-0.5 text-xs text-slate-500">Distribution across workflow stages</p>
				<div class="mt-4">
					{#if total > 0}
						<Chart
							labels={['Open', 'In Progress', 'Closed']}
							data={[openCount, inProgress, closed]}
							colors={['#3b82f6', '#f59e0b', '#10b981']}
							height={220}
						/>
					{:else}
						<div class="flex h-[220px] items-center justify-center text-sm text-slate-400">
							No tickets yet
						</div>
					{/if}
				</div>
			</div>

			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
				<h2 class="text-sm font-semibold text-slate-900">Tickets by priority</h2>
				<p class="mt-0.5 text-xs text-slate-500">Workload breakdown by urgency</p>
				<div class="mt-4">
					{#if total > 0}
						<Chart
							type="bar"
							labels={['Low', 'Medium', 'High']}
							data={[priorityLow, priorityMedium, priorityHigh]}
							colors={['#94a3b8', '#f59e0b', '#ef4444']}
							height={220}
						/>
					{:else}
						<div class="flex h-[220px] items-center justify-center text-sm text-slate-400">
							No tickets yet
						</div>
					{/if}
				</div>
			</div>
		</div>

		<div class="mt-4 sm:mt-6 rounded-xl border border-slate-200 bg-white">
			<div class="flex items-center justify-between border-b border-slate-100 px-4 py-3 sm:px-5 sm:py-4">
				<div>
					<h2 class="text-sm font-semibold text-slate-900">Recent tickets</h2>
					<p class="mt-0.5 text-xs text-slate-500">Latest tickets created across the workspace</p>
				</div>
				<a
					href="/tickets"
					class="rounded-lg px-3 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50"
				>
					View all
				</a>
			</div>
			{#if recentTickets.length === 0}
				<div class="px-6 py-10 text-center text-sm text-slate-400">No tickets yet.</div>
			{:else}
				<div class="divide-y divide-slate-100">
					{#each recentTickets as ticket}
						<a
							href="/tickets/{ticket.id}"
							class="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 sm:px-5"
						>
							<span class="text-xs font-semibold text-blue-600">{ticket.id.slice(0, 8)}</span>
							<span class="min-w-0 flex-1 truncate text-sm font-medium text-slate-700">
								{ticket.title}
							</span>
							<Badge value={ticket.priority} type="priority" />
							<Badge value={ticket.status} type="status" />
							<span class="hidden text-xs text-slate-400 sm:inline">{formatDate(ticket.created_at)}</span>
						</a>
					{/each}
				</div>
			{/if}
		</div>

		{#if auth.user}
			<div class="mt-4 sm:mt-6 rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
				<h2 class="text-sm font-semibold text-slate-900">Your Profile</h2>
				<div class="mt-4 grid gap-4 grid-cols-1 sm:grid-cols-2">
					<div>
						<p class="text-xs font-medium text-slate-500">Name</p>
						<p class="mt-1 text-sm text-slate-700">{auth.user.first_name} {auth.user.last_name}</p>
					</div>
					<div>
						<p class="text-xs font-medium text-slate-500">Email</p>
						<p class="mt-1 text-sm text-slate-700 break-all">{auth.user.email}</p>
					</div>
					<div>
						<p class="text-xs font-medium text-slate-500">Role</p>
						<p class="mt-1 text-sm text-slate-700">{auth.user.role}</p>
					</div>
					<div>
						<p class="text-xs font-medium text-slate-500">Status</p>
						<p class="mt-1 text-sm text-slate-700">{auth.user.is_active ? 'Active' : 'Inactive'}</p>
					</div>
				</div>
			</div>
		{/if}
	</AppShell>
{/if}
