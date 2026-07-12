<script lang="ts">
	let {
		label,
		value = '',
		options,
		onchange
	}: {
		label: string;
		value?: string;
		options: { value: string; label: string }[];
		onchange?: (value: string) => void;
	} = $props();

	function handleChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		onchange?.(target.value);
	}
</script>

<label class="relative">
	<span class="sr-only">{label}</span>
	<svg
		class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-surface-400"
		viewBox="0 0 24 24"
		fill="none"
		stroke="currentColor"
		stroke-width="2"
	>
		<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
	</svg>
	<select
		{value}
		onchange={handleChange}
		class="h-10 appearance-none rounded-lg border border-surface-200 bg-white pl-7 pr-7 text-xs font-medium text-surface-600 outline-none hover:bg-surface-50 focus:border-primary-400 focus:ring-2 focus:ring-primary-100 transition-colors"
	>
		{#each options as option (option.value)}
			<option value={option.value}>{option.label}</option>
		{/each}
	</select>
</label>
