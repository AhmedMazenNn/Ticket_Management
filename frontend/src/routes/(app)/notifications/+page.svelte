<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import { api } from '$lib/api/client';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Pagination from '$lib/components/ui/Pagination.svelte';
	import { notifications } from '$lib/stores/notification.svelte';
	import { NOTIFICATION_LABELS } from '$lib/types/notification';
	import type { Notification, NotificationType } from '$lib/types/notification';

	let { data } = $props();

	let items = $derived(data.notifications);
	let count = $derived(data.count);
	let currentPage = $derived(data.page);
	let filter = $derived(data.filter);

	let markingAll = $state(false);
	let deletingId = $state<string | null>(null);

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

	function handlePageChange(p: number) {
		const url = new URL(page.url);
		url.searchParams.set('page', String(p));
		goto(url.toString(), { invalidateAll: true, replaceState: true });
	}

	async function markAsRead(n: Notification) {
		if (!n.is_read) {
			try {
				await api.markAsRead(n.id);
				notifications.fetchCount();
				invalidateAll();
			} catch {
				// silently ignore
			}
		}
		goto(`/tickets/${n.ticket.id}`);
	}

	async function markAllAsRead() {
		markingAll = true;
		try {
			await api.markAllAsRead();
			notifications.fetchCount();
			invalidateAll();
		} catch {
			// silently ignore
		} finally {
			markingAll = false;
		}
	}

	async function deleteNotification(n: Notification, e: MouseEvent) {
		e.stopPropagation();
		deletingId = n.id;
		try {
			await api.deleteNotification(n.id);
			notifications.fetchCount();
			invalidateAll();
		} catch {
			// silently ignore
		} finally {
			deletingId = null;
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

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: 'numeric',
			minute: '2-digit'
		});
	}
</script>

<AppShell title="Notifications" subtitle="Stay updated on ticket activity across your team.">
	<Card className="overflow-hidden shadow-sm">
		<div class="flex flex-col gap-3 border-b border-surface-200 p-4 sm:flex-row sm:items-center sm:justify-between">
			<div class="flex gap-2">
				<button
					type="button"
					onclick={() => updateParam('filter', 'all')}
					class="rounded-lg px-3 py-1.5 text-sm font-medium transition-colors
						{filter === 'all' ? 'bg-primary-50 text-primary-700' : 'text-surface-500 hover:bg-surface-100'}"
				>
					All
				</button>
				<button
					type="button"
					onclick={() => updateParam('filter', 'unread')}
					class="rounded-lg px-3 py-1.5 text-sm font-medium transition-colors
						{filter === 'unread' ? 'bg-primary-50 text-primary-700' : 'text-surface-500 hover:bg-surface-100'}"
				>
					Unread
					{#if notifications.unreadCount > 0}
						<span class="ml-1 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold text-white">
							{notifications.unreadCount > 99 ? '99+' : notifications.unreadCount}
						</span>
					{/if}
				</button>
			</div>
			{#if notifications.unreadCount > 0}
				<Button variant="secondary" onclick={markAllAsRead} loading={markingAll}>
					<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M20 6L9 17l-5-5" />
					</svg>
					Mark all as read
				</Button>
			{/if}
		</div>

		{#if items.length === 0}
			<div class="px-6 py-16 text-center text-sm text-surface-400">
				{filter === 'unread' ? 'No unread notifications.' : 'No notifications yet.'}
			</div>
		{:else}
			<div class="divide-y divide-surface-100">
				{#each items as notification (notification.id)}
					<div class="group flex items-start gap-4 px-5 py-4 transition-colors hover:bg-surface-50
						{notification.is_read ? '' : 'bg-primary-50/40'}">
						<button
							type="button"
							onclick={() => markAsRead(notification)}
							class="flex min-w-0 flex-1 items-start gap-4 text-left"
						>
							<span class="mt-1 h-2.5 w-2.5 shrink-0 rounded-full {notification.is_read ? 'bg-transparent' : 'bg-primary-500'}"></span>
							<div class="min-w-0 flex-1">
								<div class="flex items-center gap-2">
									<span class="text-sm font-semibold text-surface-900">
										{NOTIFICATION_LABELS[notification.type as NotificationType]}
									</span>
									<Badge value={notification.ticket.priority} type="priority" />
								</div>
								<p class="mt-1 text-sm text-surface-600">
									<span class="font-medium text-surface-800">{notification.ticket.title}</span>
								</p>
								<p class="mt-1 text-xs text-surface-400">
									{formatDate(notification.created_at)} &middot; {timeAgo(notification.created_at)}
								</p>
							</div>
							<svg class="mt-1 h-4 w-4 shrink-0 text-surface-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M9 18l6-6-6-6" />
							</svg>
						</button>
						<button
							type="button"
							onclick={(e) => deleteNotification(notification, e)}
							disabled={deletingId === notification.id}
							class="mt-1 shrink-0 rounded-lg p-1.5 text-surface-300 opacity-0 transition-all hover:bg-rose-50 hover:text-rose-500 group-hover:opacity-100 disabled:opacity-50"
							aria-label="Delete notification"
						>
							{#if deletingId === notification.id}
								<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
								</svg>
							{:else}
								<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M18 6L6 18M6 6l12 12" />
								</svg>
							{/if}
						</button>
					</div>
				{/each}
			</div>
		{/if}

		<div class="flex flex-col gap-3 border-t border-surface-200 px-5 py-4 text-sm text-surface-500 sm:flex-row sm:items-center sm:justify-between">
			<span>
				Showing <b class="text-surface-700">{items.length}</b> of {count} notifications
			</span>
			<Pagination current={currentPage} total={count} onchange={handlePageChange} />
		</div>
	</Card>
</AppShell>
