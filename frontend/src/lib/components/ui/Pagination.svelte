<script lang="ts">
	let {
		current = 1,
		total = 0,
		perPage = 20,
		onchange
	}: {
		current?: number;
		total?: number;
		perPage?: number;
		onchange?: (page: number) => void;
	} = $props();

	const totalPages = $derived(Math.max(1, Math.ceil(total / perPage)));
	const pages = $derived(() => {
		const result: (number | string)[] = [];
		const tp = totalPages;
		if (tp <= 7) {
			for (let i = 1; i <= tp; i++) result.push(i);
		} else {
			result.push(1);
			if (current > 3) result.push('...');
			const start = Math.max(2, current - 1);
			const end = Math.min(tp - 1, current + 1);
			for (let i = start; i <= end; i++) result.push(i);
			if (current < tp - 2) result.push('...');
			result.push(tp);
		}
		return result;
	});

	function goToPage(p: number) {
		if (p >= 1 && p <= totalPages && p !== current) {
			onchange?.(p);
		}
	}
</script>

{#if totalPages > 1}
	<div class="flex items-center gap-1">
		<button
			type="button"
			onclick={() => goToPage(current - 1)}
			disabled={current <= 1}
			class="rounded-lg border border-surface-200 p-2 hover:bg-surface-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
			aria-label="Previous page"
		>
			<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M15 18l-6-6 6-6" />
			</svg>
		</button>
		{#each pages() as p}
			{#if p === '...'}
				<span class="px-1 text-xs text-surface-400">...</span>
			{:else}
				<button
					type="button"
					onclick={() => goToPage(p as number)}
					class="rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors
						{p === current ? 'bg-primary-50 text-primary-700' : 'text-surface-500 hover:bg-surface-100'}"
				>
					{p}
				</button>
			{/if}
		{/each}
		<button
			type="button"
			onclick={() => goToPage(current + 1)}
			disabled={current >= totalPages}
			class="rounded-lg border border-surface-200 p-2 hover:bg-surface-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
			aria-label="Next page"
		>
			<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M9 18l6-6-6-6" />
			</svg>
		</button>
	</div>
{/if}
