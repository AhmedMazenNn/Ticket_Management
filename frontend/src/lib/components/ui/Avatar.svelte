<script lang="ts">
	let {
		initials,
		size = 'sm'
	}: {
		initials: string;
		size?: 'sm' | 'md';
	} = $props();

	const sizeClasses = $derived(
		size === 'md' ? 'h-9 w-9 text-xs' : 'h-7 w-7 text-[10px]'
	);
</script>

<span
	class="inline-flex shrink-0 items-center justify-center rounded-full bg-blue-600 font-bold text-white {sizeClasses}"
>
	{initials}
</span>
