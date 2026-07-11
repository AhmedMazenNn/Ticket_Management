<script lang="ts">
	import { api } from '$lib/api/client';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Card from '$lib/components/ui/Card.svelte';

	let { data } = $props();

	let ticket = $derived(data.ticket);

	function getUserInitials(user: { first_name: string; last_name: string; email: string }): string {
		return `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase() || user.email[0].toUpperCase();
	}

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}
</script>

<AppShell title="Ticket details" subtitle={ticket.id.slice(0, 8)}>
	{#snippet action()}
		<a
			href="/tickets/{ticket.id}/edit"
			class="inline-flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50"
		>
			Edit ticket
		</a>
	{/snippet}

	<a
		href="/tickets"
		class="-mt-2 mb-5 inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-blue-600"
	>
		<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<path d="M19 12H5M12 19l-7-7 7-7" />
		</svg>
		Back to tickets
	</a>

	<div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_330px]">
		<div class="space-y-6">
			<Card className="p-6 sm:p-7">
				<div class="flex flex-wrap items-center gap-2">
					<Badge value={ticket.status} type="status" />
					<span class="text-xs font-semibold text-slate-400">
						{ticket.id.slice(0, 8)}
					</span>
				</div>
				<h2 class="mt-4 text-2xl font-bold tracking-tight text-slate-950">
					{ticket.title}
				</h2>
				{#if ticket.description}
					<div class="mt-6 border-t border-slate-100 pt-6">
						<h3 class="text-sm font-semibold text-slate-900">Description</h3>
						<p class="mt-3 max-w-3xl text-sm leading-7 text-slate-600">
							{ticket.description}
						</p>
					</div>
				{/if}
			</Card>

			<Card>
				<div class="border-b border-slate-100 px-6 py-4">
					<h2 class="text-sm font-semibold text-slate-900">Discussion</h2>
					<p class="mt-0.5 text-xs text-slate-500">Coming soon</p>
				</div>
				<div class="px-6 py-10 text-center text-sm text-slate-400">
					Comments feature coming soon.
				</div>
			</Card>
		</div>

		<aside class="space-y-5">
			<Card>
				<div class="border-b border-slate-100 px-5 py-4">
					<h2 class="text-sm font-semibold">Properties</h2>
				</div>
				<div class="divide-y divide-slate-100">
					<div class="px-5 py-4">
						<p class="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
							<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M20 6L9 17l-5-5" />
							</svg>
							Status
						</p>
						<Badge value={ticket.status} type="status" />
					</div>
					<div class="px-5 py-4">
						<p class="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
							<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z" />
								<line x1="7" y1="7" x2="7.01" y2="7" />
							</svg>
							Priority
						</p>
						<Badge value={ticket.priority} type="priority" />
					</div>
					<div class="px-5 py-4">
						<p class="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
							<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
								<circle cx="12" cy="7" r="4" />
							</svg>
							Assignee
						</p>
						{#if ticket.assigned_to}
							<span class="flex items-center gap-2 text-sm font-medium text-slate-700">
								<Avatar initials={getUserInitials(ticket.assigned_to)} size="sm" />
								{ticket.assigned_to.first_name}
								{ticket.assigned_to.last_name}
							</span>
						{:else}
							<span class="text-sm text-slate-400">Unassigned</span>
						{/if}
					</div>
					<div class="px-5 py-4">
						<p class="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
							<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
								<line x1="16" y1="2" x2="16" y2="6" />
								<line x1="8" y1="2" x2="8" y2="6" />
								<line x1="3" y1="10" x2="21" y2="10" />
							</svg>
							Created
						</p>
						<span class="text-sm text-slate-600">{formatDate(ticket.created_at)}</span>
					</div>
					<div class="px-5 py-4">
						<p class="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
							<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<circle cx="12" cy="12" r="10" />
								<polyline points="12 6 12 12 16 14" />
							</svg>
							Last updated
						</p>
						<span class="text-sm text-slate-600">{formatDate(ticket.updated_at)}</span>
					</div>
				</div>
			</Card>

			<Card>
				<div class="border-b border-slate-100 px-5 py-4">
					<h2 class="text-sm font-semibold">Activity</h2>
					<p class="mt-0.5 text-xs text-slate-500">Coming soon</p>
				</div>
				<div class="px-5 py-10 text-center text-sm text-slate-400">
					Activity log coming soon.
				</div>
			</Card>
		</aside>
	</div>
</AppShell>
