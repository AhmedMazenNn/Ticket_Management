<script lang="ts">
	let {
		label,
		description,
		checked = false,
		onchange
	}: {
		label: string;
		description: string;
		checked?: boolean;
		onchange?: (value: boolean) => void;
	} = $props();

	let enabled = $state(checked);

	function toggle() {
		enabled = !enabled;
		onchange?.(enabled);
	}
</script>

<div class="flex items-center justify-between gap-6 py-4">
	<div>
		<p class="text-sm font-semibold text-slate-700">{label}</p>
		<p class="mt-1 text-sm text-slate-500">{description}</p>
	</div>
	<button
		type="button"
		onclick={toggle}
		aria-pressed={enabled}
		aria-label={label}
		class="relative h-6 w-11 shrink-0 rounded-full transition-colors {enabled
			? 'bg-blue-600'
			: 'bg-slate-200'}"
	>
		<span
			class="absolute top-1 h-4 w-4 rounded-full bg-white shadow-sm transition-transform {enabled
				? 'translate-x-6'
				: 'translate-x-1'}"
		></span>
	</button>
</div>
