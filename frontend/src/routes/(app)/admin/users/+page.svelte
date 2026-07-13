<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import { auth } from '$lib/stores/auth.svelte';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Badge from '$lib/components/ui/Badge.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import type { User, UserRole } from '$lib/types/user';

	let loading = $state(true);
	let users = $state<User[]>([]);
	let error = $state('');
	let editingUser = $state<User | null>(null);
	let editFirstName = $state('');
	let editLastName = $state('');
	let editEmail = $state('');
	let editRole = $state<UserRole>('AGENT');
	let editIsActive = $state(true);
	let saving = $state(false);
	let saveSuccess = $state(false);

	onMount(() => {
		if (!auth.isAuthenticated) {
			goto('/login');
			return;
		}
		if (auth.user?.role !== 'ADMIN') {
			goto('/dashboard');
			return;
		}
		loadUsers();
	});

	async function loadUsers() {
		loading = true;
		error = '';
		try {
			users = await api.adminListUsers();
		} catch (e: any) {
			error = e?.detail || 'Failed to load users.';
		} finally {
			loading = false;
		}
	}

	function openEdit(user: User) {
		editingUser = user;
		editFirstName = user.first_name;
		editLastName = user.last_name;
		editEmail = user.email;
		editRole = user.role;
		editIsActive = user.is_active;
		saveSuccess = false;
	}

	function closeEdit() {
		editingUser = null;
		saveSuccess = false;
	}

	async function saveUser() {
		if (!editingUser) return;
		saving = true;
		saveSuccess = false;
		error = '';
		try {
			const updated = await api.adminUpdateUser(editingUser.id, {
				first_name: editFirstName,
				last_name: editLastName,
				email: editEmail,
				role: editRole,
				is_active: editIsActive
			});
			users = users.map((u) => (u.id === updated.id ? updated : u));
			saveSuccess = true;
			setTimeout(() => {
				closeEdit();
			}, 1200);
		} catch (e: any) {
			error = e?.detail || e?.email?.[0] || e?.role?.[0] || 'Failed to update user.';
		} finally {
			saving = false;
		}
	}

	function formatDate(iso: string): string {
		return new Date(iso).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function roleBadgeClass(role: UserRole): string {
		switch (role) {
			case 'ADMIN':
				return 'bg-purple-50 text-purple-700 ring-purple-200';
			case 'MANAGER':
				return 'bg-blue-50 text-blue-700 ring-blue-200';
			default:
				return 'bg-slate-100 text-slate-600 ring-slate-200';
		}
	}
</script>

<AppShell title="User Management" subtitle="View and manage team members.">
	{#if loading}
		<div class="flex items-center justify-center py-20">
			<svg class="h-8 w-8 animate-spin text-primary-600" viewBox="0 0 24 24" fill="none">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
			</svg>
		</div>
	{:else if error && users.length === 0}
		<div class="rounded-xl border border-rose-200 bg-rose-50 p-6 text-center text-sm text-rose-700">
			{error}
		</div>
	{:else}
		<div class="rounded-xl border border-surface-200 bg-white shadow-sm overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full text-left text-sm">
					<thead>
						<tr class="border-b border-surface-100 bg-surface-50/50">
							<th class="px-4 py-3 font-semibold text-surface-600 sm:px-6">User</th>
							<th class="px-4 py-3 font-semibold text-surface-600 sm:px-6">Role</th>
							<th class="px-4 py-3 font-semibold text-surface-600 sm:px-6 hidden md:table-cell">Status</th>
							<th class="px-4 py-3 font-semibold text-surface-600 sm:px-6 hidden lg:table-cell">Joined</th>
							<th class="px-4 py-3 font-semibold text-surface-600 sm:px-6 text-right">Actions</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-surface-100">
						{#each users as user (user.id)}
							<tr class="hover:bg-surface-50/50 transition-colors">
								<td class="px-4 py-3 sm:px-6">
									<div class="flex items-center gap-3">
										<span class="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-primary-500 to-purple-600 text-xs font-bold text-white">
											{(user.first_name?.[0] ?? '') + (user.last_name?.[0] ?? '') || user.email[0].toUpperCase()}
										</span>
										<div class="min-w-0">
											<p class="font-medium text-surface-900 truncate">{user.first_name} {user.last_name}</p>
											<p class="text-xs text-surface-500 truncate">{user.email}</p>
										</div>
									</div>
								</td>
								<td class="px-4 py-3 sm:px-6">
									<span class="inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ring-1 ring-inset {roleBadgeClass(user.role)}">
										{user.role}
									</span>
								</td>
								<td class="px-4 py-3 sm:px-6 hidden md:table-cell">
									<span class="inline-flex items-center gap-1.5 text-xs font-medium {user.is_active ? 'text-emerald-700' : 'text-surface-400'}">
										<span class="h-1.5 w-1.5 rounded-full {user.is_active ? 'bg-emerald-500' : 'bg-surface-300'}"></span>
										{user.is_active ? 'Active' : 'Inactive'}
									</span>
								</td>
								<td class="px-4 py-3 sm:px-6 hidden lg:table-cell text-xs text-surface-500">
									{formatDate(user.created_at)}
								</td>
								<td class="px-4 py-3 sm:px-6 text-right">
									<button
										type="button"
										onclick={() => openEdit(user)}
										class="rounded-lg px-3 py-1.5 text-xs font-semibold text-primary-600 hover:bg-primary-50 transition-colors"
									>
										Edit
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
			{#if users.length === 0}
				<div class="px-6 py-12 text-center text-sm text-surface-400">No users found.</div>
			{/if}
		</div>
	{/if}
</AppShell>

{#if editingUser}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
		<button type="button" class="fixed inset-0 bg-black/40 backdrop-blur-sm" onclick={closeEdit}></button>
		<div class="relative w-full max-w-lg rounded-2xl border border-surface-200 bg-white p-6 shadow-2xl">
			<div class="flex items-center justify-between">
				<h2 class="text-lg font-bold text-surface-900">Edit User</h2>
				<button
					type="button"
					onclick={closeEdit}
					class="rounded-lg p-1.5 text-surface-400 hover:bg-surface-100 hover:text-surface-600"
				>
					<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M18 6L6 18M6 6l12 12" />
					</svg>
				</button>
			</div>

			{#if error}
				<div class="mt-4 rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700 ring-1 ring-inset ring-rose-200">
					{error}
				</div>
			{/if}
			{#if saveSuccess}
				<div class="mt-4 rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-700 ring-1 ring-inset ring-emerald-200">
					User updated successfully.
				</div>
			{/if}

			<div class="mt-5 space-y-4">
				<div class="grid gap-4 sm:grid-cols-2">
					<label class="block">
						<span class="mb-1.5 block text-sm font-semibold text-surface-700">First name</span>
						<input type="text" class="form-input" bind:value={editFirstName} />
					</label>
					<label class="block">
						<span class="mb-1.5 block text-sm font-semibold text-surface-700">Last name</span>
						<input type="text" class="form-input" bind:value={editLastName} />
					</label>
				</div>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">Email</span>
					<input type="email" class="form-input" bind:value={editEmail} />
				</label>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">Role</span>
					<select class="form-input" bind:value={editRole}>
						<option value="AGENT">Agent</option>
						<option value="MANAGER">Manager</option>
						<option value="ADMIN">Admin</option>
					</select>
				</label>
				<div class="flex items-center gap-3">
					<label class="relative inline-flex cursor-pointer items-center">
						<input
							type="checkbox"
							class="peer sr-only"
							bind:checked={editIsActive}
						/>
						<div class="h-6 w-11 rounded-full bg-surface-200 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:bg-white after:shadow-sm after:transition-all peer-checked:bg-primary-600 peer-checked:after:translate-x-full"></div>
					</label>
					<span class="text-sm font-medium text-surface-700">{editIsActive ? 'Active' : 'Inactive'}</span>
				</div>
			</div>

			<div class="mt-6 flex justify-end gap-3">
				<Button variant="secondary" onclick={closeEdit}>Cancel</Button>
				<Button onclick={saveUser} loading={saving}>
					{#if saveSuccess}
						<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M20 6L9 17l-5-5" />
						</svg>
						Saved
					{:else}
						Save changes
					{/if}
				</Button>
			</div>
		</div>
	</div>
{/if}
