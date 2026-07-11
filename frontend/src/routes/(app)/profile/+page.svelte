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
	let user = $derived(auth.user);
	let assignedTotal = $state(0);
	let assignedOpen = $state(0);
	let assignedInProgress = $state(0);
	let assignedClosed = $state(0);
	let createdTotal = $state(0);
	let assignedTickets = $state<Ticket[]>([]);

	const initials = $derived(
		user
			? `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase() ||
					user.email[0].toUpperCase()
			: '?'
	);

	onMount(async () => {
		if (!auth.isAuthenticated) {
			goto('/login');
			return;
		}
		try {
			await api.me();
			const stats = await api.getMyStats();
			assignedTotal = stats.assigned_total;
			assignedOpen = stats.assigned_open;
			assignedInProgress = stats.assigned_in_progress;
			assignedClosed = stats.assigned_closed;
			createdTotal = stats.created_total;
			assignedTickets = stats.assigned_tickets;
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
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

{#if loading || !user}
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
	<AppShell title="Profile" subtitle="Manage your personal details and workload.">
		<div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
			<div class="h-20 bg-slate-900 sm:h-24"></div>
			<div class="relative px-4 pb-5 sm:px-6 sm:pb-6">
				<div class="-mt-10 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
					<div class="flex items-end gap-3 sm:gap-4">
						<span
							class="grid h-16 w-16 shrink-0 place-items-center rounded-full bg-blue-600 text-lg font-bold text-white ring-4 ring-white sm:h-20 sm:w-20 sm:text-xl"
						>
							{initials}
						</span>
						<div class="pb-1">
							<h2 class="text-lg bg-red-50 font-bold text-slate-950 sm:text-xl">
								{user.first_name}
								{user.last_name}
							</h2>
							<p class="text-xs text-slate-500 sm:text-sm">{user.role}</p>
						</div>
					</div>
					<span
						class="mb-1 shrink-0 rounded-full px-3 py-1 text-xs font-semibold self-start sm:self-auto {user.is_active
							? 'bg-emerald-50 text-emerald-700'
							: 'bg-red-50 text-red-700'}"
					>
						{user.is_active ? 'Active' : 'Inactive'}
					</span>
				</div>
				<div
					class="mt-4 flex flex-col gap-1.5 text-sm text-slate-500 sm:mt-6 sm:flex-row sm:flex-wrap sm:gap-x-6 sm:gap-y-2"
				>
					<span class="flex items-center gap-2">
						<svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
							<rect x="2" y="4" width="20" height="16" rx="2" />
							<path d="M22 7l-10 6L2 7" />
						</svg>
						<span class="break-all">{user.email}</span>
					</span>
					<span class="flex items-center gap-2">
						<svg class="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
							<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
							<circle cx="12" cy="7" r="4" />
						</svg>
						{user.role}
					</span>
				</div>
			</div>
		</div>

		<div class="mt-4 grid grid-cols-1 gap-3 sm:mt-6 sm:grid-cols-3 sm:gap-4">
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<div class="flex items-center justify-between">
					<span class="rounded-lg bg-blue-50 p-2 sm:p-2.5 text-blue-600">
						<svg class="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
							<path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" />
							<rect x="9" y="3" width="6" height="4" rx="1" />
						</svg>
					</span>
					<span class="text-xs font-medium text-slate-400">Assigned</span>
				</div>
				<p class="mt-4 text-2xl font-bold tracking-tight text-slate-950 sm:mt-5">{assignedTotal}</p>
				<p class="mt-1 text-sm text-slate-500">Assigned tickets</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<div class="flex items-center justify-between">
					<span class="rounded-lg bg-emerald-50 p-2 sm:p-2.5 text-emerald-600">
						<svg class="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
							<path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
							<path d="M22 4L12 14.01l-3-3" />
						</svg>
					</span>
					<span class="text-xs font-medium text-slate-400">Completed</span>
				</div>
				<p class="mt-4 text-2xl font-bold tracking-tight text-slate-950 sm:mt-5">{assignedClosed}</p>
				<p class="mt-1 text-sm text-slate-500">Closed tickets</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<div class="flex items-center justify-between">
					<span class="rounded-lg bg-amber-50 p-2 sm:p-2.5 text-amber-600">
						<svg class="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
							<path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
						</svg>
					</span>
					<span class="text-xs font-medium text-slate-400">Open</span>
				</div>
				<p class="mt-4 text-2xl font-bold tracking-tight text-slate-950 sm:mt-5">{assignedOpen}</p>
				<p class="mt-1 text-sm text-slate-500">Open tickets</p>
			</div>
		</div>

		<div class="mt-4 grid gap-4 sm:mt-6 sm:gap-6 lg:grid-cols-[minmax(0,1.5fr)_minmax(320px,1fr)]">
			<div class="rounded-xl border border-slate-200 bg-white">
				<div class="flex items-center justify-between border-b border-slate-100 px-4 py-3 sm:px-5 sm:py-4">
					<div>
						<h2 class="text-sm font-semibold text-slate-900">Assigned tickets</h2>
						<p class="mt-0.5 text-xs text-slate-500">Tickets where you're the primary owner</p>
					</div>
					{#if assignedTickets.length > 0}
						<a href="/tickets" class="rounded-lg px-3 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50">
							View all
						</a>
					{/if}
				</div>
				{#if assignedTickets.length === 0}
					<div class="px-4 py-10 text-center text-sm text-slate-400 sm:px-5 sm:py-12">
						No tickets assigned to you yet.
					</div>
				{:else}
					<div class="divide-y divide-slate-100">
						{#each assignedTickets as ticket}
							<a
								href="/tickets/{ticket.id}"
								class="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 sm:px-5"
							>
								<span class="min-w-0 flex-1 truncate text-sm font-medium text-slate-700">
									{ticket.title}
								</span>
								<Badge value={ticket.priority} type="priority" />
								<Badge value={ticket.status} type="status" />
								<span class="hidden text-xs text-slate-400 sm:inline">{formatDate(ticket.updated_at)}</span>
							</a>
						{/each}
					</div>
				{/if}
			</div>

			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-6">
				<div class="border-b border-slate-100 pb-3">
					<h2 class="text-sm font-semibold text-slate-900">Workload breakdown</h2>
					<p class="mt-0.5 text-xs text-slate-500">Your assigned tickets by status</p>
				</div>
				<div class="mt-4">
					{#if assignedTotal > 0}
						<Chart
							labels={['Open', 'In Progress', 'Closed']}
							data={[assignedOpen, assignedInProgress, assignedClosed]}
							colors={['#3b82f6', '#f59e0b', '#10b981']}
							height={200}
						/>
					{:else}
						<div class="flex h-[200px] items-center justify-center text-sm text-slate-400">
							No assigned tickets yet
						</div>
					{/if}
				</div>
				<div class="mt-4 grid grid-cols-3 gap-2 text-center">
					<div class="rounded-lg bg-blue-50 p-2">
						<p class="text-lg font-bold text-blue-600">{assignedOpen}</p>
						<p class="text-xs text-slate-500">Open</p>
					</div>
					<div class="rounded-lg bg-amber-50 p-2">
						<p class="text-lg font-bold text-amber-600">{assignedInProgress}</p>
						<p class="text-xs text-slate-500">In Progress</p>
					</div>
					<div class="rounded-lg bg-emerald-50 p-2">
						<p class="text-lg font-bold text-emerald-600">{assignedClosed}</p>
						<p class="text-xs text-slate-500">Closed</p>
					</div>
				</div>
			</div>
		</div>
	</AppShell>
{/if}
