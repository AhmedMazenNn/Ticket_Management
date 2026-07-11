<script lang="ts">
	import Button from './Button.svelte';

	let {
		open = false,
		title,
		description,
		onclose,
		onconfirm
	}: {
		open?: boolean;
		title: string;
		description: string;
		onclose: () => void;
		onconfirm: () => void;
	} = $props();
</script>

{#if open}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
		onclick={onclose}
	>
		<div
			class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl"
			onclick={(e) => e.stopPropagation()}
			role="dialog"
			tabindex="-1"
			aria-label={title}
		>
			<h2 class="text-lg font-bold text-slate-950">{title}</h2>
			<p class="mt-2 text-sm text-slate-500">{description}</p>
			<div class="mt-6 flex justify-end gap-3">
				<Button variant="secondary" onclick={onclose}>Cancel</Button>
				<button
					type="button"
					onclick={onconfirm}
					class="inline-flex h-10 items-center gap-2 rounded-xl bg-rose-600 px-4 text-sm font-semibold text-white shadow-sm hover:bg-rose-700"
				>
					Delete
				</button>
			</div>
		</div>
	</div>
{/if}
