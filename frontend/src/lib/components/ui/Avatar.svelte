<script lang="ts">
	let {
		initials,
		size = 'sm'
	}: {
		initials: string;
		size?: 'sm' | 'md';
	} = $props();

	const sizeClasses = $derived(size === 'md' ? 'h-9 w-9 text-xs' : 'h-7 w-7 text-[10px]');
</script>

<span
	class="inline-flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 font-bold text-white shadow-sm {sizeClasses}"
>
	{initials}
</span>
