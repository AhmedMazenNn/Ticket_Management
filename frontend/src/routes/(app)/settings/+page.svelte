<script lang="ts">
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Toggle from '$lib/components/ui/Toggle.svelte';

	let saved = $state(false);

	function save() {
		saved = true;
		setTimeout(() => (saved = false), 1800);
	}
</script>

<AppShell title="Settings" subtitle="Configure workspace preferences and notification defaults.">
	<div class="mx-auto max-w-4xl space-y-6">
		<Card className="p-6 sm:p-7">
			<div class="flex gap-3">
				<span class="rounded-lg bg-blue-50 p-2.5 text-blue-600">
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
					>
						<path
							d="M3 21h18M9 8h1M9 12h1M9 16h1M14 8h1M14 12h1M14 16h1M5 21V5a2 2 0 012-2h10a2 2 0 012 2v16"
						/>
					</svg>
				</span>
				<div>
					<h2 class="text-base font-semibold text-slate-900">Workspace</h2>
					<p class="mt-1 text-sm text-slate-500">Manage information shared across your team.</p>
				</div>
			</div>
			<div class="mt-6 grid gap-5 sm:grid-cols-2">
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-slate-700">Workspace name</span>
					<input class="form-input" value="Northstar Workspace" />
				</label>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-slate-700">Workspace URL</span>
					<div class="flex">
						<span
							class="inline-flex h-10 items-center rounded-l-xl border border-r-0 border-slate-200 bg-slate-50 px-3 text-sm text-slate-400"
						>
							ticketflow.io/
						</span>
						<input class="form-input rounded-l-none" value="northstar" />
					</div>
				</label>
			</div>
		</Card>

		<Card className="p-6 sm:p-7">
			<div class="flex gap-3">
				<span class="rounded-lg bg-amber-50 p-2.5 text-amber-600">
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
					>
						<path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0" />
					</svg>
				</span>
				<div>
					<h2 class="text-base font-semibold text-slate-900">Notifications</h2>
					<p class="mt-1 text-sm text-slate-500">Control how you receive ticket updates.</p>
				</div>
			</div>
			<div class="mt-5 divide-y divide-slate-100">
				<Toggle
					label="Ticket assignments"
					description="Receive a notification when a ticket is assigned to you."
					checked={true}
				/>
				<Toggle
					label="Mentions and replies"
					description="Receive notifications when someone mentions or replies to you."
					checked={true}
				/>
				<Toggle
					label="Daily summary"
					description="Get a daily email with unresolved and overdue tickets."
				/>
			</div>
		</Card>

		<Card className="p-6 sm:p-7">
			<div class="flex gap-3">
				<span class="rounded-lg bg-emerald-50 p-2.5 text-emerald-600">
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
					>
						<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
						<path d="M9 12l2 2 4-4" />
					</svg>
				</span>
				<div>
					<h2 class="text-base font-semibold text-slate-900">Access & permissions</h2>
					<p class="mt-1 text-sm text-slate-500">Your current workspace access level.</p>
				</div>
			</div>
			<div
				class="mt-5 flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4"
			>
				<div class="flex items-center gap-3">
					<span class="rounded-lg bg-white p-2 text-slate-500 shadow-sm">
						<svg
							class="h-4 w-4"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.5"
						>
							<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
							<circle cx="9" cy="7" r="4" />
							<path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
						</svg>
					</span>
					<div>
						<p class="text-sm font-semibold text-slate-700">Workspace administrator</p>
						<p class="mt-0.5 text-xs text-slate-500">
							You can manage members, settings, and tickets.
						</p>
					</div>
				</div>
				<span class="rounded-md bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-700">
					Admin
				</span>
			</div>
		</Card>

		<div class="flex justify-end">
			<Button onclick={save}>
				{#if saved}
					<svg
						class="h-4 w-4"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M20 6L9 17l-5-5" />
					</svg>
					Changes saved
				{:else}
					Save changes
				{/if}
			</Button>
		</div>
	</div>
</AppShell>
