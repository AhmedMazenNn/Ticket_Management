<script lang="ts">
	import { goto } from '$app/navigation';
	import { api } from '$lib/api/client';
	import { parseApiError } from '$lib/api/errors';
	import FieldError from '$lib/components/ui/FieldError.svelte';

	let firstName = $state('');
	let lastName = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let showPassword = $state(false);
	let loading = $state(false);
	let error = $state('');
	let fieldErrors = $state<Record<string, string>>({});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';
		fieldErrors = {};

		if (!email.trim()) fieldErrors.email = 'Email is required.';
		if (!password) fieldErrors.password = 'Password is required.';
		else if (password.length < 8) fieldErrors.password = 'Password must be at least 8 characters.';
		if (password !== confirmPassword)
			fieldErrors.confirmPassword = 'Passwords do not match.';
		if (Object.keys(fieldErrors).length > 0) return;

		loading = true;
		try {
			await api.register({ email, password, first_name: firstName, last_name: lastName });
			goto('/dashboard');
		} catch (err) {
			const parsed = parseApiError(err);
			error = parsed.message;
			fieldErrors = parsed.fields;
		} finally {
			loading = false;
		}
	}
</script>

<main class="min-h-screen w-full bg-white lg:grid lg:grid-cols-2">
	<section class="flex min-h-screen items-center justify-center px-6 py-12 sm:px-12">
		<div class="w-full max-w-md">
			<div class="mb-12 flex items-center gap-3">
				<span
					class="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-base font-black text-white shadow-lg shadow-indigo-500/25"
				>
					T
				</span>
				<span class="text-xl font-bold tracking-tight text-slate-900">TicketFlow</span>
			</div>
			<div>
				<p class="text-sm font-semibold text-indigo-600">Create an account</p>
				<h1 class="mt-2 text-3xl font-bold tracking-tight text-slate-950">Join your workspace</h1>
				<p class="mt-3 text-sm leading-6 text-slate-500">Get started with TicketFlow in seconds.</p>
			</div>

			{#if error}
				<div
					class="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700"
				>
					{error}
				</div>
			{/if}

			<form onsubmit={handleSubmit} class="mt-8 space-y-5">
				<div class="grid gap-4 sm:grid-cols-2">
					<label class="block">
						<span class="mb-1.5 block text-sm font-semibold text-slate-700">First name</span>
						<div class="relative">
							<svg
								class="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="1.5"
							>
								<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
								<circle cx="12" cy="7" r="4" />
							</svg>
							<input
								type="text"
								bind:value={firstName}
								placeholder="Alex"
								class="h-11 w-full rounded-xl border border-slate-200 pl-10 pr-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-3 focus:ring-indigo-100"
							/>
						</div>
					</label>
					<label class="block">
						<span class="mb-1.5 block text-sm font-semibold text-slate-700">Last name</span>
						<div class="relative">
							<svg
								class="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="1.5"
							>
								<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
								<circle cx="12" cy="7" r="4" />
							</svg>
							<input
								type="text"
								bind:value={lastName}
								placeholder="Stone"
								class="h-11 w-full rounded-xl border border-slate-200 pl-10 pr-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-3 focus:ring-indigo-100"
							/>
						</div>
					</label>
				</div>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-slate-700">Work email</span>
					<div class="relative">
						<svg
							class="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.5"
						>
							<rect x="2" y="4" width="20" height="16" rx="2" />
							<path d="M22 7l-10 6L2 7" />
						</svg>
						<input
							required
							type="email"
							bind:value={email}
							placeholder="you@company.com"
							class="h-11 w-full rounded-xl border border-slate-200 pl-10 pr-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-3 focus:ring-indigo-100 {fieldErrors.email
								? 'border-rose-300'
								: ''}"
						/>
					</div>
					<FieldError error={fieldErrors.email} />
				</label>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-slate-700">Password</span>
					<div class="relative">
						<svg
							class="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.5"
						>
							<rect x="3" y="11" width="18" height="11" rx="2" />
							<path d="M7 11V7a5 5 0 0110 0v4" />
						</svg>
						<input
							required
							type={showPassword ? 'text' : 'password'}
							bind:value={password}
							minlength="8"
							placeholder="At least 8 characters"
							class="h-11 w-full rounded-xl border border-slate-200 pl-10 pr-11 text-sm outline-none transition focus:border-indigo-500 focus:ring-3 focus:ring-indigo-100 {fieldErrors.password
								? 'border-rose-300'
								: ''}"
						/>
						<button
							type="button"
							onclick={() => (showPassword = !showPassword)}
							class="absolute right-3 top-3 text-slate-400 hover:text-slate-600"
							aria-label={showPassword ? 'Hide password' : 'Show password'}
						>
							{#if showPassword}
								<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
									<path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94" />
									<path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19" />
									<path d="M1 1l22 22" />
									<path d="M14.12 14.12A3 3 0 019.88 9.88" />
								</svg>
							{:else}
								<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
									<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
									<circle cx="12" cy="12" r="3" />
								</svg>
							{/if}
						</button>
					</div>
					<FieldError error={fieldErrors.password} />
				</label>
				<label class="block">
					<span class="mb-1.5 block text-sm font-semibold text-slate-700">Confirm password</span>
					<div class="relative">
						<svg
							class="pointer-events-none absolute left-3 top-3 h-4 w-4 text-slate-400"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.5"
						>
							<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
						</svg>
						<input
							required
							type={showPassword ? 'text' : 'password'}
							bind:value={confirmPassword}
							minlength="8"
							placeholder="Repeat your password"
							class="h-11 w-full rounded-xl border border-slate-200 pl-10 pr-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-3 focus:ring-indigo-100 {fieldErrors.confirmPassword
								? 'border-rose-300'
								: ''}"
						/>
					</div>
					<FieldError error={fieldErrors.confirmPassword} />
				</label>
				<button
					type="submit"
					disabled={loading}
					class="inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-4 text-sm font-semibold text-white shadow-lg shadow-indigo-200 transition-all hover:from-indigo-700 hover:to-purple-700 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50"
				>
					{#if loading}
						<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
						</svg>
					{:else}
						Create account
						<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M5 12h14M12 5l7 7-7 7" />
						</svg>
					{/if}
				</button>
			</form>
			<p class="mt-8 text-center text-sm text-slate-500">
				Already have an account?
				<a href="/login" class="font-semibold text-indigo-600 hover:text-indigo-700">Sign in</a>
			</p>
		</div>
	</section>

	<section
		class="relative hidden overflow-hidden bg-slate-950 p-12 lg:flex lg:flex-col lg:justify-between"
	>
		<div class="gradient-mesh absolute inset-0"></div>
		<div class="relative z-10 flex items-center gap-2 text-sm font-medium text-slate-300">
			<span class="h-2 w-2 rounded-full bg-emerald-400"></span>
			All systems operational
		</div>
		<div
			class="relative z-10 mx-auto w-full max-w-lg rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-sm"
		>
			<div class="mb-5 flex items-center justify-between">
				<div>
					<p class="text-xs font-medium text-slate-400">Support operations</p>
					<h2 class="mt-1 text-lg font-semibold text-white">Everything in flow</h2>
				</div>
				<span class="rounded-lg bg-indigo-500/15 px-2.5 py-1 text-xs font-semibold text-indigo-300"
					>This week</span
				>
			</div>
			<div class="grid grid-cols-3 gap-3">
				<div class="rounded-lg bg-white/[0.06] p-3">
					<p class="text-[11px] text-slate-400">Resolved</p>
					<p class="mt-1 text-xl font-semibold text-white">184</p>
				</div>
				<div class="rounded-lg bg-white/[0.06] p-3">
					<p class="text-[11px] text-slate-400">Response time</p>
					<p class="mt-1 text-xl font-semibold text-white">24m</p>
				</div>
				<div class="rounded-lg bg-white/[0.06] p-3">
					<p class="text-[11px] text-slate-400">CSAT score</p>
					<p class="mt-1 text-xl font-semibold text-white">98%</p>
				</div>
			</div>
			<div class="mt-5 rounded-xl border border-white/10 bg-white/[0.04] p-4">
				<div class="flex items-center justify-between border-b border-white/10 pb-3">
					<div class="flex items-center gap-2">
						<span
							class="grid h-7 w-7 place-items-center rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 text-[10px] font-bold text-white"
							>MC</span
						>
						<span class="text-sm font-medium text-white">Maya Chen</span>
					</div>
					<span class="text-xs text-slate-400">just now</span>
				</div>
				<p class="pt-3 text-sm leading-6 text-slate-300">
					I've identified the session issue and shared a fix for review.
				</p>
			</div>
		</div>
		<div class="relative z-10">
			<h2 class="max-w-md text-3xl font-semibold leading-tight tracking-tight text-white">
				The calm command center for customer work.
			</h2>
			<p class="mt-4 max-w-md text-sm leading-6 text-slate-400">
				TicketFlow gives high-performing teams the context to resolve what matters—without losing
				momentum.
			</p>
			<div class="mt-6 flex gap-5 text-sm text-slate-300">
				<span class="flex items-center gap-1.5">
					<svg class="h-4 w-4 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5" /></svg>
					Unified context
				</span>
				<span class="flex items-center gap-1.5">
					<svg class="h-4 w-4 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5" /></svg>
					Clear ownership
				</span>
				<span class="flex items-center gap-1.5">
					<svg class="h-4 w-4 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5" /></svg>
					Faster resolution
				</span>
			</div>
		</div>
	</section>
</main>
