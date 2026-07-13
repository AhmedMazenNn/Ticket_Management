<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import { auth } from '$lib/stores/auth.svelte';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Card from '$lib/components/ui/Card.svelte';

	let firstName = $state('');
	let lastName = $state('');
	let email = $state('');
	let profileSaved = $state(false);
	let profileError = $state('');
	let profileLoading = $state(false);

	let currentPassword = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let passwordSaved = $state(false);
	let passwordError = $state('');
	let passwordLoading = $state(false);

	onMount(() => {
		if (!auth.isAuthenticated) {
			goto('/login');
			return;
		}
		if (auth.user) {
			firstName = auth.user.first_name;
			lastName = auth.user.last_name;
			email = auth.user.email;
		}
	});

	async function saveProfile() {
		profileError = '';
		profileLoading = true;
		try {
			await api.updateProfile({
				first_name: firstName,
				last_name: lastName,
				email: email
			});
			profileSaved = true;
			setTimeout(() => (profileSaved = false), 2000);
		} catch (e: any) {
			profileError =
				e?.detail ||
				e?.first_name?.[0] ||
				e?.last_name?.[0] ||
				e?.email?.[0] ||
				'Failed to update profile.';
		} finally {
			profileLoading = false;
		}
	}

	async function changePassword() {
		passwordError = '';
		passwordSaved = false;
		if (newPassword !== confirmPassword) {
			passwordError = 'New passwords do not match.';
			return;
		}
		if (newPassword.length < 8) {
			passwordError = 'Password must be at least 8 characters.';
			return;
		}
		passwordLoading = true;
		try {
			await api.changePassword(currentPassword, newPassword);
			passwordSaved = true;
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
			setTimeout(() => (passwordSaved = false), 2000);
		} catch (e: any) {
			passwordError =
				e?.detail ||
				e?.current_password?.[0] ||
				e?.new_password?.[0] ||
				'Failed to change password.';
		} finally {
			passwordLoading = false;
		}
	}
</script>

<AppShell title="Settings" subtitle="Manage your account settings.">
	<div class="mx-auto max-w-2xl space-y-6">
		<Card className="p-6 sm:p-7 shadow-sm">
			<div class="flex gap-3">
				<span class="rounded-lg bg-primary-50 p-2.5 text-primary-600">
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
					>
						<path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
					</svg>
				</span>
				<div>
					<h2 class="text-base font-semibold text-surface-900">Profile</h2>
					<p class="mt-1 text-sm text-surface-500">Update your personal information.</p>
				</div>
			</div>
			{#if profileError}
				<div
					class="mt-4 rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700 ring-1 ring-inset ring-rose-200"
				>
					{profileError}
				</div>
			{/if}
			{#if profileSaved}
				<div
					class="mt-4 rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-700 ring-1 ring-inset ring-emerald-200"
				>
					Profile updated successfully.
				</div>
			{/if}
			<div class="mt-6 grid gap-5 sm:grid-cols-2">
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">First name</span>
					<input type="text" class="form-input" bind:value={firstName} placeholder="First name" />
				</label>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">Last name</span>
					<input type="text" class="form-input" bind:value={lastName} placeholder="Last name" />
				</label>
			</div>
			<div class="mt-5">
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">Email</span>
					<input type="email" class="form-input" bind:value={email} placeholder="Email address" />
				</label>
			</div>
			<div class="mt-6 flex justify-end">
				<Button onclick={saveProfile} loading={profileLoading}>
					{#if profileSaved}
						<svg
							class="h-4 w-4"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M20 6L9 17l-5-5" />
						</svg>
						Saved
					{:else}
						Save profile
					{/if}
				</Button>
			</div>
		</Card>

		<Card className="p-6 sm:p-7 shadow-sm">
			<div class="flex gap-3">
				<span class="rounded-lg bg-amber-50 p-2.5 text-amber-600">
					<svg
						class="h-5 w-5"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1.5"
					>
						<path
							d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
						/>
					</svg>
				</span>
				<div>
					<h2 class="text-base font-semibold text-surface-900">Change password</h2>
					<p class="mt-1 text-sm text-surface-500">Ensure your account stays secure.</p>
				</div>
			</div>
			{#if passwordError}
				<div
					class="mt-4 rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700 ring-1 ring-inset ring-rose-200"
				>
					{passwordError}
				</div>
			{/if}
			{#if passwordSaved}
				<div
					class="mt-4 rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-700 ring-1 ring-inset ring-emerald-200"
				>
					Password changed successfully.
				</div>
			{/if}
			<div class="mt-6 space-y-5">
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">Current password</span>
					<input
						type="password"
						class="form-input"
						bind:value={currentPassword}
						placeholder="Enter current password"
					/>
				</label>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700">New password</span>
					<input
						type="password"
						class="form-input"
						bind:value={newPassword}
						placeholder="Enter new password"
					/>
				</label>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-surface-700"
						>Confirm new password</span
					>
					<input
						type="password"
						class="form-input"
						bind:value={confirmPassword}
						placeholder="Confirm new password"
					/>
				</label>
			</div>
			<div class="mt-6 flex justify-end">
				<Button onclick={changePassword} loading={passwordLoading}>
					{#if passwordSaved}
						<svg
							class="h-4 w-4"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
						>
							<path d="M20 6L9 17l-5-5" />
						</svg>
						Changed
					{:else}
						Change password
					{/if}
				</Button>
			</div>
		</Card>
	</div>
</AppShell>
