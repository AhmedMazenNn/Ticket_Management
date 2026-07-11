<script lang="ts">
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';
	import { api } from '$lib/api/client';
	import { auth } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';

	let {
		title,
		subtitle = '',
		action,
		children
	}: {
		title: string;
		subtitle?: string;
		action?: Snippet;
		children: Snippet;
	} = $props();

	let sidebarOpen = $state(false);
	let mobileOpen = $state(false);

	const pathname: string = $derived(page.url.pathname);
	const userInitials = $derived(
		auth.user
			? `${auth.user.first_name?.[0] ?? ''}${auth.user.last_name?.[0] ?? ''}`.toUpperCase() ||
					auth.user.email[0].toUpperCase()
			: '?'
	);

	function closeMobile() {
		mobileOpen = false;
	}

	async function handleLogout() {
		await api.logout();
		goto('/login');
	}
</script>

<div class="flex min-h-screen bg-slate-50">
	<!-- Mobile backdrop -->
	{#if mobileOpen}
		<button
			type="button"
			class="fixed inset-0 z-40 bg-black/40 lg:hidden"
			onclick={closeMobile}
			aria-label="Close sidebar"
		></button>
	{/if}

	<!-- Sidebar -->
	<aside
		class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-slate-200 bg-white transition-transform duration-200
			lg:sticky lg:z-auto lg:translate-x-0
			{mobileOpen ? 'translate-x-0' : '-translate-x-full'}
			{sidebarOpen ? 'lg:w-60' : 'lg:w-16'} w-60"
	>
		<div class="flex h-14 items-center gap-2.5 border-b border-slate-200 px-4">
			<span
				class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-blue-600 text-sm font-black text-white"
			>
				T
			</span>
			{#if sidebarOpen || mobileOpen}
				<span class="text-base font-bold tracking-tight text-slate-900"> TicketFlow </span>
			{/if}
		</div>

		<nav class="flex-1 space-y-1 overflow-y-auto px-2 py-3">
			<a
				href="/dashboard"
				onclick={closeMobile}
				class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
					{pathname === '/dashboard'
					? 'bg-blue-50 text-blue-700'
					: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
			>
				<svg
					class="h-5 w-5 shrink-0"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<rect x="3" y="3" width="7" height="7" rx="1.5" />
					<rect x="14" y="3" width="7" height="7" rx="1.5" />
					<rect x="3" y="14" width="7" height="7" rx="1.5" />
					<rect x="14" y="14" width="7" height="7" rx="1.5" />
				</svg>
				{#if sidebarOpen || mobileOpen}
					Dashboard
				{/if}
			</a>
			<a
				href="/tickets"
				onclick={closeMobile}
				class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
					{pathname === '/tickets'
					? 'bg-blue-50 text-blue-700'
					: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
			>
				<svg
					class="h-5 w-5 shrink-0"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" />
					<rect x="9" y="3" width="6" height="4" rx="1" />
				</svg>
				{#if sidebarOpen || mobileOpen}
					Tickets
				{/if}
			</a>
			<a
				href="/settings"
				onclick={closeMobile}
				class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
					{pathname === '/settings'
					? 'bg-blue-50 text-blue-700'
					: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
			>
				<svg
					class="h-5 w-5 shrink-0"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<path
						d="M12.22 2h-.44a2 2 0 00-2 2v.18a2 2 0 01-1 1.73l-.43.25a2 2 0 01-2 0l-.15-.08a2 2 0 00-2.73.73l-.22.38a2 2 0 00.73 2.73l.15.1a2 2 0 011 1.72v.51a2 2 0 01-1 1.74l-.15.09a2 2 0 00-.73 2.73l.22.38a2 2 0 002.73.73l.15-.08a2 2 0 012 0l.43.25a2 2 0 011 1.73V20a2 2 0 002 2h.44a2 2 0 002-2v-.18a2 2 0 011-1.73l.43-.25a2 2 0 012 0l.15.08a2 2 0 002.73-.73l.22-.39a2 2 0 00-.73-2.73l-.15-.08a2 2 0 01-1-1.74v-.5a2 2 0 011-1.74l.15-.09a2 2 0 00.73-2.73l-.22-.38a2 2 0 00-2.73-.73l-.15.08a2 2 0 01-2 0l-.43-.25a2 2 0 01-1-1.73V4a2 2 0 00-2-2z"
					/>
					<circle cx="12" cy="12" r="3" />
				</svg>
				{#if sidebarOpen || mobileOpen}
					Settings
				{/if}
			</a>
			<a
				href="/profile"
				onclick={closeMobile}
				class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
					{pathname === '/profile'
					? 'bg-blue-50 text-blue-700'
					: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
			>
				<svg
					class="h-5 w-5 shrink-0"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
				>
					<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
					<circle cx="12" cy="7" r="4" />
				</svg>
				{#if sidebarOpen || mobileOpen}
					Profile
				{/if}
			</a>
		</nav>

		{#if auth.user}
			<div class="shrink-0 border-t border-slate-200 px-3 py-3">
				<div class="flex items-center gap-3">
					<span
						class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-blue-600 text-xs font-bold text-white"
					>
						{userInitials}
					</span>
					{#if sidebarOpen || mobileOpen}
						<div class="min-w-0 flex-1 rounded-lg bg-slate-100 px-3 py-1.5">
							<p class="truncate text-sm font-semibold text-slate-900">
								{auth.user.first_name}
								{auth.user.last_name}
							</p>
							<p class="truncate text-xs text-slate-500">{auth.user.email}</p>
						</div>
						<button
							type="button"
							onclick={handleLogout}
							class="shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600"
							aria-label="Sign out"
						>
							<svg
								class="h-4 w-4"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="1.5"
							>
								<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
								<polyline points="16 17 21 12 16 7" />
								<line x1="21" y1="12" x2="9" y2="12" />
							</svg>
						</button>
					{/if}
				</div>
			</div>
		{/if}

		<button
			type="button"
			onclick={() => (sidebarOpen = !sidebarOpen)}
			class="hidden lg:flex h-10 items-center justify-center border-t border-slate-200 text-slate-400 hover:text-slate-600"
			aria-label="Toggle sidebar"
		>
			<svg
				class="h-4 w-4 transition-transform {sidebarOpen ? '' : 'rotate-180'}"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
			>
				<path d="M15 18l-6-6 6-6" />
			</svg>
		</button>
	</aside>

	<div class="flex flex-1 flex-col min-w-0">
		<header class="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 sm:px-6">
			<button
				type="button"
				onclick={() => (mobileOpen = !mobileOpen)}
				class="lg:hidden shrink-0 rounded-lg p-2 text-slate-500 hover:bg-slate-100"
				aria-label="Open menu"
			>
				<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M3 12h18M3 6h18M3 18h18" />
				</svg>
			</button>
			<div class="min-w-0 flex-1">
				<h1 class="truncate text-lg font-bold tracking-tight text-slate-950 sm:text-xl">{title}</h1>
				{#if subtitle}
					<p class="mt-0.5 hidden text-sm text-slate-500 sm:block">{subtitle}</p>
				{/if}
			</div>
			{#if action}
				<div class="shrink-0">
					{@render action()}
				</div>
			{/if}
		</header>

		<main class="flex-1 p-4 sm:p-6">
			{@render children()}
		</main>
	</div>
</div>
