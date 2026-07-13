<script lang="ts">
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import { parseApiError } from '$lib/api/errors';
	import { auth } from '$lib/stores/auth.svelte';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import FieldError from '$lib/components/ui/FieldError.svelte';
	import { TICKET_PRIORITIES, TICKET_STATUSES } from '$lib/constants';
	import type { User } from '$lib/types/user';

	let { data } = $props();

	let users = $derived(data.users);
	let loading = $state(false);
	let error = $state('');
	let fieldErrors = $state<Record<string, string>>({});

	let title = $state('');
	let description = $state('');
	let priority = $state('MEDIUM');
	let status = $state('OPEN');
	let assignedTo = $state('');

	let assignableUsers = $derived(
		users.filter((u: User) => {
			if (u.role === 'AGENT') return true;
			if (auth.user && u.id === auth.user.id) return true;
			return false;
		})
	);

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		fieldErrors = {};

		if (!title.trim()) fieldErrors.title = 'Title is required.';
		if (Object.keys(fieldErrors).length > 0) return;

		loading = true;
		try {
			const ticket = await api.createTicket({
				title: title.trim(),
				description: description.trim(),
				priority: priority as any,
				status: status as any,
				assigned_to: assignedTo || null
			});
			goto(`/tickets/${ticket.id}`);
		} catch (err) {
			const parsed = parseApiError(err);
			error = parsed.message;
			fieldErrors = parsed.fields;
		} finally {
			loading = false;
		}
	}
</script>

<AppShell title="Create ticket" subtitle="Capture the right context so your team can move quickly.">
	{#snippet action()}
		<a
			href="/tickets"
			class="inline-flex h-10 items-center gap-2 rounded-xl border border-surface-200 bg-white px-4 text-sm font-semibold text-surface-700 shadow-sm hover:bg-surface-50 transition-colors"
		>
			Cancel
		</a>
	{/snippet}

	<div class="mx-auto max-w-3xl">
		<a
			href="/tickets"
			class="-mt-4 mb-5 inline-flex items-center gap-1.5 text-sm font-medium text-surface-500 hover:text-primary-600 transition-colors"
		>
			<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M19 12H5M12 19l-7-7 7-7" />
			</svg>
			Back
		</a>

		<Card className="p-6 sm:p-8 shadow-sm">
			<form onsubmit={handleSubmit} class="space-y-6">
				{#if error}
					<div class="rounded-lg bg-rose-50 border border-rose-200 p-3 text-sm text-rose-700">
						{error}
					</div>
				{/if}

				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">
						Title <span class="ml-1 text-rose-500">*</span>
					</span>
					<input
						bind:value={title}
						required
						placeholder="Briefly describe the issue or request"
						class="block w-full rounded-xl border border-surface-200 bg-white px-4 py-2.5 text-sm outline-none placeholder:text-surface-400 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 transition-colors {fieldErrors.title
							? 'border-rose-300'
							: ''}"
					/>
					<FieldError error={fieldErrors.title} />
				</label>

				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">Description</span>
					<span class="mt-1.5 mb-1.5 block text-xs leading-5 text-surface-400">
						Include relevant context, expected outcome, and any useful links.
					</span>
					<textarea
						bind:value={description}
						placeholder="Describe the work that needs to be done..."
						rows="5"
						class="block w-full resize-y rounded-xl border border-surface-200 bg-white px-4 py-2.5 text-sm outline-none placeholder:text-surface-400 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 transition-colors"
					></textarea>
				</label>

				<div class="grid gap-5 sm:grid-cols-3">
					<label class="block">
						<span class="mb-1.5 block text-sm font-semibold text-surface-700">Priority</span>
						<select
							bind:value={priority}
							class="block w-full rounded-xl border border-surface-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 transition-colors"
						>
							{#each TICKET_PRIORITIES as p (p.value)}
								<option value={p.value}>{p.label}</option>
							{/each}
						</select>
					</label>

					<label class="block">
						<span class="mb-1.5 block text-sm font-semibold text-surface-700">Status</span>
						<select
							bind:value={status}
							class="block w-full rounded-xl border border-surface-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 transition-colors"
						>
							{#each TICKET_STATUSES as s (s.value)}
								<option value={s.value}>{s.label}</option>
							{/each}
						</select>
					</label>

					<label class="block">
						<span class="mb-1.5 block text-sm font-semibold text-surface-700">Assign user</span>
						<select
							bind:value={assignedTo}
							class="block w-full rounded-xl border border-surface-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 transition-colors"
						>
							<option value="">Unassigned</option>
							{#each assignableUsers as user (user.id)}
								<option value={user.id}>
									{user.first_name ? `${user.first_name} ${user.last_name}` : user.email}
								</option>
							{/each}
						</select>
					</label>
				</div>

				<div class="flex items-center justify-end gap-3 border-t border-surface-100 pt-6">
					<a
						href="/tickets"
						class="inline-flex h-10 items-center gap-2 rounded-xl border border-surface-200 bg-white px-4 text-sm font-semibold text-surface-700 shadow-sm hover:bg-surface-50 transition-colors"
					>
						Cancel
					</a>
					<Button type="submit" {loading}>
						{#if !loading}
							<svg
								class="h-4 w-4"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M20 6L9 17l-5-5" />
							</svg>
						{/if}
						Create ticket
					</Button>
				</div>
			</form>
		</Card>
	</div>
</AppShell>
