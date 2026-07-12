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
	let assignedTotal = $state(0);
	let assignedOpen = $state(0);
	let assignedInProgress = $state(0);
	let assignedClosed = $state(0);
	let createdTotal = $state(0);
	let assignedTickets = $state<Ticket[]>([]);

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

			const [stats, myStats] = await Promise.all([api.getDashboardStats(), api.getMyStats()]);
			total = stats.total;
			openCount = stats.open;
			inProgress = stats.in_progress;
			closed = stats.closed;
			recentTickets = stats.recent_tickets;
			priorityLow = stats.priority_breakdown.low;
			priorityMedium = stats.priority_breakdown.medium;
			priorityHigh = stats.priority_breakdown.high;
			assignedTotal = myStats.assigned_total;
			assignedOpen = myStats.assigned_open;
			assignedInProgress = myStats.assigned_in_progress;
			assignedClosed = myStats.assigned_closed;
			createdTotal = myStats.created_total;
			assignedTickets = myStats.assigned_tickets;
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

	function completionRate(): number {
		if (total === 0) return 0;
		return Math.round((closed / total) * 100);
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
				<div class="flex items-center justify-between">
					<p class="text-xs sm:text-sm font-medium text-slate-500">Total tickets</p>
					<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100">
						<svg
							class="h-4 w-4 text-slate-600"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
							<polyline points="14 2 14 8 20 8" />
							<line x1="16" y1="13" x2="8" y2="13" />
							<line x1="16" y1="17" x2="8" y2="17" />
							<polyline points="10 9 9 9 8 9" />
						</svg>
					</div>
				</div>
				<p class="mt-3 text-2xl sm:text-3xl font-bold text-slate-950">{total}</p>
				<p class="mt-1 text-xs text-slate-400">All time</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<div class="flex items-center justify-between">
					<p class="text-xs sm:text-sm font-medium text-slate-500">Open</p>
					<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
						<svg
							class="h-4 w-4 text-blue-600"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<circle cx="12" cy="12" r="10" />
							<line x1="12" y1="8" x2="12" y2="16" />
							<line x1="8" y1="12" x2="16" y2="12" />
						</svg>
					</div>
				</div>
				<p class="mt-3 text-2xl sm:text-3xl font-bold text-blue-600">{openCount}</p>
				<p class="mt-1 text-xs text-slate-400">Awaiting action</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<div class="flex items-center justify-between">
					<p class="text-xs sm:text-sm font-medium text-slate-500">In progress</p>
					<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50">
						<svg
							class="h-4 w-4 text-amber-600"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path
								d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"
							/>
						</svg>
					</div>
				</div>
				<p class="mt-3 text-2xl sm:text-3xl font-bold text-amber-600">{inProgress}</p>
				<p class="mt-1 text-xs text-slate-400">Being worked on</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<div class="flex items-center justify-between">
					<p class="text-xs sm:text-sm font-medium text-slate-500">Closed</p>
					<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50">
						<svg
							class="h-4 w-4 text-emerald-600"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
							<polyline points="22 4 12 14.01 9 11.01" />
						</svg>
					</div>
				</div>
				<p class="mt-3 text-2xl sm:text-3xl font-bold text-emerald-600">{closed}</p>
				<p class="mt-1 text-xs text-slate-400">Completed</p>
			</div>
		</div>

		<div class="mt-3 grid gap-3 sm:mt-4 sm:gap-4 sm:grid-cols-3">
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">My assigned</p>
				<p class="mt-2 text-2xl font-bold text-slate-950">{assignedTotal}</p>
				<div class="mt-2 flex gap-2 text-xs">
					<span class="text-blue-600">{assignedOpen} open</span>
					<span class="text-slate-300">|</span>
					<span class="text-amber-600">{assignedInProgress} active</span>
					<span class="text-slate-300">|</span>
					<span class="text-emerald-600">{assignedClosed} done</span>
				</div>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">Created by me</p>
				<p class="mt-2 text-2xl font-bold text-slate-950">{createdTotal}</p>
				<p class="mt-2 text-xs text-slate-400">Tickets you created</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">Completion rate</p>
				<div class="mt-2 flex items-baseline gap-2">
					<p class="text-2xl font-bold text-slate-950">{completionRate()}%</p>
				</div>
				<div class="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
					<div
						class="h-full rounded-full bg-emerald-500 transition-all duration-500"
						style="width: {completionRate()}%"
					></div>
				</div>
			</div>
		</div>

		<div class="mt-3 grid gap-3 sm:mt-4 sm:gap-6 lg:grid-cols-3">
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
				<h2 class="text-sm font-semibold text-slate-900">Status distribution</h2>
				<p class="mt-0.5 text-xs text-slate-500">Workflow stage breakdown</p>
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
				<h2 class="text-sm font-semibold text-slate-900">Priority breakdown</h2>
				<p class="mt-0.5 text-xs text-slate-500">Workload by urgency level</p>
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

			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
				<h2 class="text-sm font-semibold text-slate-900">My workload</h2>
				<p class="mt-0.5 text-xs text-slate-500">Your assigned tickets by status</p>
				<div class="mt-4">
					{#if assignedTotal > 0}
						<Chart
							labels={['Open', 'In Progress', 'Closed']}
							data={[assignedOpen, assignedInProgress, assignedClosed]}
							colors={['#3b82f6', '#f59e0b', '#10b981']}
							height={220}
						/>
					{:else}
						<div class="flex h-[220px] items-center justify-center text-sm text-slate-400">
							No assigned tickets
						</div>
					{/if}
				</div>
			</div>
		</div>

		<div class="mt-3 grid gap-3 sm:mt-4 sm:gap-6 lg:grid-cols-2">
			<div class="rounded-xl border border-slate-200 bg-white">
				<div
					class="flex items-center justify-between border-b border-slate-100 px-4 py-3 sm:px-5 sm:py-4"
				>
					<div>
						<h2 class="text-sm font-semibold text-slate-900">Recent tickets</h2>
						<p class="mt-0.5 text-xs text-slate-500">Latest across the workspace</p>
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
						{#each recentTickets as ticket (ticket.id)}
							<a
								href="/tickets/{ticket.id}"
								class="block px-4 py-3 hover:bg-slate-50 sm:flex sm:items-center sm:gap-3 sm:px-5"
							>
								<div class="flex items-center gap-2 sm:gap-3 sm:min-w-0 sm:flex-1">
									<span class="hidden text-xs font-semibold text-blue-600 sm:inline"
										>{ticket.id.slice(0, 8)}</span
									>
									<span class="min-w-0 flex-1 truncate text-sm font-medium text-slate-700"
										>{ticket.title}</span
									>
								</div>
								<div class="mt-2 flex items-center gap-2 sm:mt-0 sm:flex-shrink-0">
									<Badge value={ticket.priority} type="priority" />
									<Badge value={ticket.status} type="status" />
									<span class="hidden text-xs text-slate-400 md:inline"
										>{formatDate(ticket.created_at)}</span
									>
								</div>
							</a>
						{/each}
					</div>
				{/if}
			</div>

			<div class="rounded-xl border border-slate-200 bg-white">
				<div
					class="flex items-center justify-between border-b border-slate-100 px-4 py-3 sm:px-5 sm:py-4"
				>
					<div>
						<h2 class="text-sm font-semibold text-slate-900">My assigned tickets</h2>
						<p class="mt-0.5 text-xs text-slate-500">Tickets you need to work on</p>
					</div>
					<a
						href="/tickets"
						class="rounded-lg px-3 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50"
					>
						View all
					</a>
				</div>
				{#if assignedTickets.length === 0}
					<div class="px-6 py-10 text-center text-sm text-slate-400">No assigned tickets.</div>
				{:else}
					<div class="divide-y divide-slate-100">
						{#each assignedTickets as ticket (ticket.id)}
							<a
								href="/tickets/{ticket.id}"
								class="block px-4 py-3 hover:bg-slate-50 sm:flex sm:items-center sm:gap-3 sm:px-5"
							>
								<div class="flex items-center gap-2 sm:gap-3 sm:min-w-0 sm:flex-1">
									<span class="hidden text-xs font-semibold text-blue-600 sm:inline"
										>{ticket.id.slice(0, 8)}</span
									>
									<span class="min-w-0 flex-1 truncate text-sm font-medium text-slate-700"
										>{ticket.title}</span
									>
								</div>
								<div class="mt-2 flex items-center gap-2 sm:mt-0 sm:flex-shrink-0">
									<Badge value={ticket.priority} type="priority" />
									<Badge value={ticket.status} type="status" />
								</div>
							</a>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</AppShell>
{/if}
