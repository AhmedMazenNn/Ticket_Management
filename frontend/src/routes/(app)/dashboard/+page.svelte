<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import { auth } from '$lib/stores/auth.svelte';
	import AppShell from '$lib/components/layout/AppShell.svelte';

	let loading = $state(true);
	let greeting = $state('');

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
		} catch {
			auth.clear();
			goto('/login');
		} finally {
			loading = false;
		}
	});
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
				<p class="mt-2 text-2xl sm:text-3xl font-bold text-slate-950">—</p>
				<p class="mt-1 text-xs text-slate-400">No data yet</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">Open tickets</p>
				<p class="mt-2 text-2xl sm:text-3xl font-bold text-slate-950">—</p>
				<p class="mt-1 text-xs text-slate-400">No data yet</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">In progress</p>
				<p class="mt-2 text-2xl sm:text-3xl font-bold text-slate-950">—</p>
				<p class="mt-1 text-xs text-slate-400">No data yet</p>
			</div>
			<div class="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
				<p class="text-xs sm:text-sm font-medium text-slate-500">Closed tickets</p>
				<p class="mt-2 text-2xl sm:text-3xl font-bold text-slate-950">—</p>
				<p class="mt-1 text-xs text-slate-400">No data yet</p>
			</div>
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
