<script lang="ts">
	let { error = '' }: { error?: string } = $props();
</script>

{#if error}
	<p class="mt-1.5 text-xs text-rose-600">{error}</p>
{/if}
