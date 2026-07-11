<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		variant = 'primary',
		loading = false,
		type = 'button',
		onclick,
		children
	}: {
		variant?: 'primary' | 'secondary';
		loading?: boolean;
		type?: 'button' | 'submit' | 'reset';
		onclick?: () => void;
		children: Snippet;
	} = $props();
</script>

<button
	{type}
	{onclick}
	disabled={loading}
	class="inline-flex h-10 items-center gap-2 rounded-xl px-4 text-sm font-semibold shadow-sm transition-colors disabled:cursor-not-allowed disabled:opacity-60
		{variant === 'primary'
		? 'bg-blue-600 text-white shadow-blue-200 hover:bg-blue-700'
		: 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}"
>
	{#if loading}
		<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
			<path
				class="opacity-75"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
				fill="currentColor"
			/>
		</svg>
	{/if}
	{@render children()}
</button>
