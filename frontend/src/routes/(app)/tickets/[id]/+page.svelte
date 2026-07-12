<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import { parseApiError } from '$lib/api/errors';
	import { auth } from '$lib/stores/auth.svelte';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Avatar from '$lib/components/ui/Avatar.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import type { Comment } from '$lib/types/comment';
	import type { TicketHistoryEntry } from '$lib/types/history';

	let { data } = $props();

	let ticket = $derived(data.ticket);
	let comments = $state<Comment[]>([]);
	let commentBody = $state('');
	let submitting = $state(false);
	let editingId = $state<string | null>(null);
	let editBody = $state('');
	let loadingComments = $state(true);
	let historyItems = $state<TicketHistoryEntry[]>([]);
	let loadingHistory = $state(true);
	let commentError = $state('');
	let editError = $state('');

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

	function formatDateTime(iso: string): string {
		return new Date(iso).toLocaleString('en-US', {
			month: 'short',
			day: 'numeric',
			hour: 'numeric',
			minute: '2-digit'
		});
	}

	function timeAgo(iso: string): string {
		const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
		if (seconds < 60) return 'just now';
		const minutes = Math.floor(seconds / 60);
		if (minutes < 60) return `${minutes}m ago`;
		const hours = Math.floor(minutes / 60);
		if (hours < 24) return `${hours}h ago`;
		const days = Math.floor(hours / 24);
		if (days < 7) return `${days}d ago`;
		return formatDate(iso);
	}

	const FIELD_LABELS: Record<string, string> = {
		created: 'Ticket created',
		title: 'Title',
		description: 'Description',
		priority: 'Priority',
		status: 'Status',
		assigned_to: 'Assignee'
	};

	const FIELD_ICONS: Record<string, string> = {
		created: 'M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6',
		title:
			'M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z',
		description:
			'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8',
		priority:
			'M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z M7 7h.01',
		status: 'M20 6L9 17l-5-5',
		assigned_to: 'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2 M12 11a4 4 0 100-8 4 4 0 000 8z'
	};

	async function loadComments() {
		try {
			comments = await api.listComments(ticket.id);
		} catch {
			// silently fail
		} finally {
			loadingComments = false;
		}
	}

	async function loadHistory() {
		try {
			historyItems = await api.listHistory(ticket.id);
		} catch {
			// silently fail
		} finally {
			loadingHistory = false;
		}
	}

	async function submitComment() {
		if (!commentBody.trim() || submitting) return;
		commentError = '';
		submitting = true;
		try {
			const newComment = await api.createComment(ticket.id, { body: commentBody.trim() });
			comments = [newComment, ...comments];
			commentBody = '';
		} catch (err) {
			const parsed = parseApiError(err);
			commentError = parsed.message;
		} finally {
			submitting = false;
		}
	}

	function startEdit(comment: Comment) {
		editingId = comment.id;
		editBody = comment.body;
	}

	function cancelEdit() {
		editingId = null;
		editBody = '';
	}

	async function saveEdit(commentId: string) {
		if (!editBody.trim()) return;
		editError = '';
		try {
			const updated = await api.updateComment(commentId, { body: editBody.trim() });
			comments = comments.map((c) => (c.id === commentId ? updated : c));
			cancelEdit();
		} catch (err) {
			const parsed = parseApiError(err);
			editError = parsed.message;
		}
	}

	async function deleteComment(commentId: string) {
		try {
			await api.deleteComment(commentId);
			comments = comments.filter((c) => c.id !== commentId);
		} catch (err) {
			const parsed = parseApiError(err);
			commentError = parsed.message;
		}
	}

	onMount(() => {
		loadComments();
		loadHistory();
	});
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

			<Card className="overflow-hidden">
				<div class="border-b border-slate-100 px-6 py-4">
					<div class="flex items-center justify-between">
						<div>
							<h2 class="text-sm font-semibold text-slate-900">Discussion</h2>
							<p class="mt-0.5 text-xs text-slate-500">
								{comments.length}
								{comments.length === 1 ? 'comment' : 'comments'}
							</p>
						</div>
					</div>
				</div>

				<div class="p-6">
					{#if auth.user}
						<div class="mb-6 flex gap-3">
							<div class="flex-shrink-0 pt-0.5">
								<Avatar initials={getUserInitials(auth.user)} size="sm" />
							</div>
							<div class="min-w-0 flex-1">
								<textarea
									bind:value={commentBody}
									placeholder="Add a comment..."
									rows="3"
									class="block w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
								></textarea>
								{#if commentError}
									<p class="mt-2 text-xs text-rose-600">{commentError}</p>
								{/if}
								<div class="mt-2 flex justify-end">
									<button
										onclick={submitComment}
										disabled={!commentBody.trim() || submitting}
										class="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
									>
										{#if submitting}
											<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
												<circle
													class="opacity-25"
													cx="12"
													cy="12"
													r="10"
													stroke="currentColor"
													stroke-width="4"
												/>
												<path
													class="opacity-75"
													fill="currentColor"
													d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
												/>
											</svg>
											Sending...
										{:else}
											Comment
										{/if}
									</button>
								</div>
							</div>
						</div>
					{/if}

					{#if loadingComments}
						<div class="py-10 text-center text-sm text-slate-400">
							<svg
								class="mx-auto h-6 w-6 animate-spin text-slate-300"
								viewBox="0 0 24 24"
								fill="none"
							>
								<circle
									class="opacity-25"
									cx="12"
									cy="12"
									r="10"
									stroke="currentColor"
									stroke-width="4"
								/>
								<path
									class="opacity-75"
									fill="currentColor"
									d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
								/>
							</svg>
							<p class="mt-2">Loading comments...</p>
						</div>
					{:else if comments.length === 0}
						<div class="py-10 text-center">
							<svg
								class="mx-auto h-10 w-10 text-slate-300"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="1.5"
							>
								<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
							</svg>
							<p class="mt-2 text-sm font-medium text-slate-500">No comments yet</p>
							<p class="mt-1 text-xs text-slate-400">Be the first to start the discussion.</p>
						</div>
					{:else}
						<div class="space-y-5">
							{#each comments as comment (comment.id)}
								<div class="group flex gap-3">
									<div class="flex-shrink-0 pt-0.5">
										<Avatar initials={getUserInitials(comment.author)} size="sm" />
									</div>
									<div class="min-w-0 flex-1">
										<div class="flex items-center gap-2">
											<span class="text-sm font-semibold text-slate-900">
												{comment.author.first_name || comment.author.email}
												{comment.author.last_name || ''}
											</span>
											<span
												class="text-xs text-slate-400"
												title={formatDateTime(comment.created_at)}
											>
												{timeAgo(comment.created_at)}
											</span>
											{#if comment.updated_at !== comment.created_at}
												<span class="text-xs text-slate-400">(edited)</span>
											{/if}
										</div>
										{#if editingId === comment.id}
											<div class="mt-2">
												<textarea
													bind:value={editBody}
													rows="3"
													class="block w-full resize-none rounded-xl border border-blue-300 bg-white px-4 py-3 text-sm text-slate-900 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
												></textarea>
												{#if editError}
													<p class="mt-2 text-xs text-rose-600">{editError}</p>
												{/if}
												<div class="mt-2 flex gap-2">
													<button
														onclick={() => saveEdit(comment.id)}
														class="inline-flex items-center rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700"
													>
														Save
													</button>
													<button
														onclick={cancelEdit}
														class="inline-flex items-center rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50"
													>
														Cancel
													</button>
												</div>
											</div>
										{:else}
											<p class="mt-1 text-sm leading-6 text-slate-600">{comment.body}</p>
										{/if}
										{#if auth.user && (auth.user.id === comment.author.id || auth.user.role === 'ADMIN') && editingId !== comment.id}
											<div
												class="mt-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity"
											>
												<button
													onclick={() => startEdit(comment)}
													class="inline-flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-blue-600"
												>
													<svg
														class="h-3.5 w-3.5"
														viewBox="0 0 24 24"
														fill="none"
														stroke="currentColor"
														stroke-width="2"
													>
														<path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
														<path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
													</svg>
													Edit
												</button>
												<button
													onclick={() => deleteComment(comment.id)}
													class="inline-flex items-center gap-1 text-xs font-medium text-slate-400 hover:text-rose-600"
												>
													<svg
														class="h-3.5 w-3.5"
														viewBox="0 0 24 24"
														fill="none"
														stroke="currentColor"
														stroke-width="2"
													>
														<polyline points="3 6 5 6 21 6" />
														<path
															d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
														/>
													</svg>
													Delete
												</button>
											</div>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					{/if}
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
							<svg
								class="h-3.5 w-3.5"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M20 6L9 17l-5-5" />
							</svg>
							Status
						</p>
						<Badge value={ticket.status} type="status" />
					</div>
					<div class="px-5 py-4">
						<p class="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
							<svg
								class="h-3.5 w-3.5"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path
									d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"
								/>
								<line x1="7" y1="7" x2="7.01" y2="7" />
							</svg>
							Priority
						</p>
						<Badge value={ticket.priority} type="priority" />
					</div>
					<div class="px-5 py-4">
						<p class="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
							<svg
								class="h-3.5 w-3.5"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
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
							<svg
								class="h-3.5 w-3.5"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
								<circle cx="12" cy="7" r="4" />
							</svg>
							Created by
						</p>
						<span class="flex items-center gap-2 text-sm font-medium text-slate-700">
							<Avatar initials={getUserInitials(ticket.created_by)} size="sm" />
							{ticket.created_by.first_name || ticket.created_by.email}
							{ticket.created_by.last_name || ''}
						</span>
					</div>
					<div class="px-5 py-4">
						<p class="mb-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
							<svg
								class="h-3.5 w-3.5"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
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
							<svg
								class="h-3.5 w-3.5"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
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
					<p class="mt-0.5 text-xs text-slate-500">
						{historyItems.length}
						{historyItems.length === 1 ? 'event' : 'events'}
					</p>
				</div>
				<div class="p-5">
					{#if loadingHistory}
						<div class="py-8 text-center text-sm text-slate-400">
							<svg
								class="mx-auto h-5 w-5 animate-spin text-slate-300"
								viewBox="0 0 24 24"
								fill="none"
							>
								<circle
									class="opacity-25"
									cx="12"
									cy="12"
									r="10"
									stroke="currentColor"
									stroke-width="4"
								/>
								<path
									class="opacity-75"
									fill="currentColor"
									d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
								/>
							</svg>
							<p class="mt-2">Loading activity...</p>
						</div>
					{:else if historyItems.length === 0}
						<div class="py-8 text-center">
							<svg
								class="mx-auto h-8 w-8 text-slate-300"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="1.5"
							>
								<path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
							</svg>
							<p class="mt-2 text-sm font-medium text-slate-500">No activity yet</p>
							<p class="mt-1 text-xs text-slate-400">Changes will appear here.</p>
						</div>
					{:else}
						<div class="relative">
							<div class="absolute left-4 top-0 bottom-0 w-px bg-slate-100"></div>
							<div class="space-y-4">
								{#each historyItems as entry (entry.id)}
									<div class="relative flex gap-3">
										<div
											class="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white ring-2 ring-slate-100"
										>
											<svg
												class="h-3.5 w-3.5 text-slate-500"
												viewBox="0 0 24 24"
												fill="none"
												stroke="currentColor"
												stroke-width="2"
												stroke-linecap="round"
												stroke-linejoin="round"
											>
												<path d={FIELD_ICONS[entry.field_name] ?? FIELD_ICONS.created} />
											</svg>
										</div>
										<div class="min-w-0 flex-1 pt-1">
											<div class="flex items-center gap-2">
												<span class="text-sm font-medium text-slate-700">
													{entry.changed_by.first_name || entry.changed_by.email}
													{entry.changed_by.last_name || ''}
												</span>
												<span
													class="text-xs text-slate-400"
													title={formatDateTime(entry.created_at)}
												>
													{timeAgo(entry.created_at)}
												</span>
											</div>
											{#if entry.field_name === 'created'}
												<p class="mt-1 text-sm text-slate-500">Created this ticket</p>
											{:else}
												<p class="mt-1 text-sm text-slate-500">
													Changed <span class="font-medium text-slate-600"
														>{FIELD_LABELS[entry.field_name] ?? entry.field_name}</span
													>
													{#if entry.old_value && entry.new_value}
														from <span class="font-medium text-slate-600">{entry.old_value}</span>
														to <span class="font-medium text-slate-600">{entry.new_value}</span>
													{:else if entry.new_value}
														to <span class="font-medium text-slate-600">{entry.new_value}</span>
													{:else}
														<span class="font-medium text-slate-600">cleared</span>
													{/if}
												</p>
											{/if}
										</div>
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			</Card>
		</aside>
	</div>
</AppShell>
