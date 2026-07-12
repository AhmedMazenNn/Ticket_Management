<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { auth } from '$lib/stores/auth.svelte';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();

	onMount(async () => {
		if (auth.isAuthenticated && !auth.user) {
			try {
				await import('$lib/api/client').then((m) => m.api.me());
			} catch {
				auth.clear();
			}
		}
		auth.setLoaded();
	});

	$effect(() => {
		if (!auth.loading && !auth.isAuthenticated) {
			const publicPaths = ['/login'];
			if (!publicPaths.includes(page.url.pathname)) {
				goto('/login');
			}
		}
	});
</script>

{#if auth.loading}
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
{:else if auth.isAuthenticated}
	{@render children()}
{/if}
