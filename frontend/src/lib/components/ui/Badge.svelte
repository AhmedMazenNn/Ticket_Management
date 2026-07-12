<script lang="ts">
	import { PRIORITY_COLORS, STATUS_COLORS } from '$lib/constants';

	let {
		value,
		type
	}: {
		value: string;
		type: 'status' | 'priority';
	} = $props();

	const labels: Record<string, string> = {
		OPEN: 'Open',
		IN_PROGRESS: 'In Progress',
		CLOSED: 'Closed',
		LOW: 'Low',
		MEDIUM: 'Medium',
		HIGH: 'High'
	};

	const colorMap = $derived<Record<string, string>>(
		type === 'status' ? STATUS_COLORS : PRIORITY_COLORS
	);

	const display = $derived(labels[value] ?? value);
	const colorClass = $derived(colorMap[value] ?? 'bg-slate-100 text-slate-700');
</script>

<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold {colorClass}">
	{display}
</span>
