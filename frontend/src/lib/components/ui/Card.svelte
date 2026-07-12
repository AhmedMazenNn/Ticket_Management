<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		className = '',
		children
	}: {
		className?: string;
		children: Snippet;
	} = $props();
</script>

<div class="rounded-2xl border border-slate-200/80 bg-white shadow-sm {className}">
	{@render children()}
</div>
