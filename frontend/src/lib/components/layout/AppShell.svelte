<script lang="ts">
	import { onMount } from 'svelte';
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';
	import { api } from '$lib/api/client';
	import { auth } from '$lib/stores/auth.svelte';
	import { notifications } from '$lib/stores/notification.svelte';
	import { goto } from '$app/navigation';
	import type { Notification } from '$lib/types/notification';
	import { NOTIFICATION_LABELS } from '$lib/types/notification';

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
	let bellOpen = $state(false);
	let recentNotifications = $state<Notification[]>([]);
	let loadingRecent = $state(false);

	const pathname: string = $derived(page.url.pathname);
	const userInitials = $derived(
		auth.user
			? `${auth.user.first_name?.[0] ?? ''}${auth.user.last_name?.[0] ?? ''}`.toUpperCase() ||
					auth.user.email[0].toUpperCase()
			: '?'
	);

	onMount(() => {
		notifications.startPolling(30000);
		loadRecent();
		return () => notifications.stopPolling();
	});

	function closeMobile() {
		mobileOpen = false;
	}

	function closeBell() {
		bellOpen = false;
	}

	async function loadRecent() {
		loadingRecent = true;
		try {
			const res = await api.listNotifications({ page: 1 });
			recentNotifications = res.results.slice(0, 10);
		} catch {
			// silently ignore
		} finally {
			loadingRecent = false;
		}
	}

	async function toggleBell() {
		bellOpen = !bellOpen;
		if (bellOpen && recentNotifications.length === 0) {
			await loadRecent();
		}
	}

	async function handleMarkAsRead(notification: Notification) {
		if (!notification.is_read) {
			try {
				await api.markAsRead(notification.id);
				notifications.fetchCount();
				recentNotifications = recentNotifications.map((n) =>
					n.id === notification.id ? { ...n, is_read: true } : n
				);
			} catch {
				// silently ignore
			}
		}
		goto(`/tickets/${notification.ticket.id}`);
		closeBell();
	}

	async function handleMarkAllRead() {
		try {
			await api.markAllAsRead();
			recentNotifications = recentNotifications.map((n) => ({ ...n, is_read: true }));
			notifications.fetchCount();
		} catch {
			// silently ignore individual failures
		}
	}

	function timeAgo(dateStr: string): string {
		const now = Date.now();
		const then = new Date(dateStr).getTime();
		const diffMs = now - then;
		const diffMin = Math.floor(diffMs / 60000);
		if (diffMin < 1) return 'Just now';
		if (diffMin < 60) return `${diffMin}m ago`;
		const diffHr = Math.floor(diffMin / 60);
		if (diffHr < 24) return `${diffHr}h ago`;
		const diffDay = Math.floor(diffHr / 24);
		return `${diffDay}d ago`;
	}

	async function handleLogout() {
		notifications.clear();
		await api.logout();
		goto('/login');
	}

	const navItems = $derived([
		{
			href: '/dashboard',
			label: 'Dashboard',
			icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1'
		},
		{
			href: '/tickets',
			label: 'Tickets',
			icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2'
		},
		{
			href: '/notifications',
			label: 'Notifications',
			icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9'
		},
		...(auth.user?.role === 'ADMIN'
			? [
					{
						href: '/admin/users',
						label: 'Users',
						icon: 'M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2M9 11a4 4 0 100-8 4 4 0 000 8zM23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75'
					}
				]
			: []),
		{
			href: '/profile',
			label: 'Profile',
			icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
		},
		{
			href: '/settings',
			label: 'Settings',
			icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z'
		}
	]);
</script>

<div class="flex min-h-screen bg-slate-50/80">
	{#if mobileOpen}
		<button
			type="button"
			class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
			onclick={closeMobile}
			aria-label="Close sidebar"
		></button>
	{/if}

	<aside
		class="fixed inset-y-0 left-0 z-50 flex flex-col sidebar-gradient transition-all duration-300
			lg:sticky lg:z-auto lg:translate-x-0
			{mobileOpen ? 'translate-x-0' : '-translate-x-full'}
			{sidebarOpen ? 'lg:w-60' : 'lg:w-[68px]'} w-60"
	>
		<div class="flex h-16 items-center gap-3 border-b border-white/10 px-4">
			<span
				class="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-sm font-black text-white shadow-lg shadow-indigo-500/25"
			>
				T
			</span>
			{#if sidebarOpen || mobileOpen}
				<span class="text-lg font-bold tracking-tight text-white"> TicketFlow </span>
			{/if}
		</div>

		<nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4">
			{#each navItems as item}
				<a
					href={item.href}
					onclick={closeMobile}
					class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150
						{pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href))
						? 'bg-white/10 text-white shadow-sm'
						: 'text-slate-400 hover:bg-white/5 hover:text-white'}"
				>
					<svg
						class="h-5 w-5 shrink-0"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<path d={item.icon} />
					</svg>
					{#if sidebarOpen || mobileOpen}
						{item.label}
						{#if item.href === '/notifications' && notifications.unreadCount > 0}
							<span class="ml-auto inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 px-1.5 text-[10px] font-bold text-white shadow-sm">
								{notifications.unreadCount > 99 ? '99+' : notifications.unreadCount}
							</span>
						{/if}
					{/if}
				</a>
			{/each}
		</nav>

		{#if auth.user}
			<div class="shrink-0 border-t border-white/10 px-3 py-3">
				<div class="flex items-center gap-3">
					<span
						class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 text-[10px] font-bold text-white"
					>
						{userInitials}
					</span>
					{#if sidebarOpen || mobileOpen}
						<div class="min-w-0 flex-1">
							<p class="truncate text-sm font-semibold text-white">
								{auth.user.first_name}
								{auth.user.last_name}
							</p>
							<p class="truncate text-xs text-slate-400">{auth.user.email}</p>
						</div>
						<button
							type="button"
							onclick={handleLogout}
							class="shrink-0 rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-white/10 hover:text-white"
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
			class="hidden lg:flex h-10 items-center justify-center border-t border-white/10 text-slate-400 transition-colors hover:text-white"
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
		<header class="glass sticky top-0 z-30 flex items-center gap-4 border-b border-slate-200/60 px-4 py-3 sm:px-6">
			<button
				type="button"
				onclick={() => (mobileOpen = !mobileOpen)}
				class="lg:hidden shrink-0 rounded-xl p-2 text-slate-500 transition-colors hover:bg-slate-100"
				aria-label="Open menu"
			>
				<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M3 12h18M3 6h18M3 18h18" />
				</svg>
			</button>
			<div class="min-w-0 flex-1">
				<h1 class="truncate text-lg font-bold tracking-tight text-slate-900 sm:text-xl">{title}</h1>
				{#if subtitle}
					<p class="mt-0.5 hidden text-sm text-slate-500 sm:block">{subtitle}</p>
				{/if}
			</div>
			<div class="relative shrink-0">
				<button
					type="button"
					onclick={toggleBell}
					class="relative rounded-xl p-2.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
					aria-label="Notifications"
				>
					<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
						<path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
						<path d="M13.73 21a2 2 0 01-3.46 0" />
					</svg>
					{#if notifications.unreadCount > 0}
						<span class="absolute -top-0.5 -right-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold text-white shadow-sm">
							{notifications.unreadCount > 99 ? '99+' : notifications.unreadCount}
						</span>
					{/if}
				</button>
				{#if bellOpen}
					<button
						type="button"
						class="fixed inset-0 z-40"
						onclick={closeBell}
						aria-label="Close notifications"
					></button>
					<div class="absolute right-0 top-full z-50 mt-2 w-80 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
						<div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
							<h3 class="text-sm font-semibold text-slate-900">Notifications</h3>
							{#if recentNotifications.some((n) => !n.is_read)}
								<button
									type="button"
									onclick={handleMarkAllRead}
									class="text-xs font-medium text-indigo-600 hover:text-indigo-800"
								>
									Mark all read
								</button>
							{/if}
						</div>
						<div class="max-h-80 overflow-y-auto">
							{#if loadingRecent}
								<div class="flex items-center justify-center py-8">
									<svg class="h-5 w-5 animate-spin text-slate-400" viewBox="0 0 24 24" fill="none">
										<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
										<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
									</svg>
								</div>
							{:else if recentNotifications.length === 0}
								<p class="py-8 text-center text-sm text-slate-500">No notifications yet</p>
							{:else}
								{#each recentNotifications as notification}
									<button
										type="button"
										onclick={() => handleMarkAsRead(notification)}
										class="flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-slate-50
											{notification.is_read ? '' : 'bg-indigo-50/40'}"
									>
										<span class="mt-0.5 h-2 w-2 shrink-0 rounded-full {notification.is_read ? 'bg-transparent' : 'bg-indigo-500'}"></span>
										<div class="min-w-0 flex-1">
											<p class="text-sm font-medium text-slate-900">{NOTIFICATION_LABELS[notification.type]}</p>
											<p class="mt-0.5 truncate text-xs text-slate-500">{notification.ticket.title}</p>
											<p class="mt-1 text-xs text-slate-400">{timeAgo(notification.created_at)}</p>
										</div>
									</button>
								{/each}
							{/if}
						</div>
						<div class="border-t border-slate-100 px-4 py-2.5">
							<a
								href="/notifications"
								onclick={closeBell}
								class="block text-center text-xs font-medium text-indigo-600 hover:text-indigo-800"
							>
								View all notifications
							</a>
						</div>
					</div>
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
