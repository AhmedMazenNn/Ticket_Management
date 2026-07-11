<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth.svelte';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();

	onMount(() => {
		if (auth.isAuthenticated) {
			goto('/dashboard');
		}
	});
</script>

{#if auth.isAuthenticated}
	<!-- Redirecting to dashboard... -->
{:else}
	{@render children()}
{/if}
