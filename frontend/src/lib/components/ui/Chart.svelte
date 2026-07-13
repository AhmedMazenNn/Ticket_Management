<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import {
		Chart,
		DoughnutController,
		ArcElement,
		Tooltip,
		Legend,
		BarController,
		BarElement,
		CategoryScale,
		LinearScale
	} from 'chart.js';

	Chart.register(
		DoughnutController,
		ArcElement,
		Tooltip,
		Legend,
		BarController,
		BarElement,
		CategoryScale,
		LinearScale
	);

	let {
		type = 'doughnut',
		labels = [],
		data = [],
		colors = [],
		height = 200
	}: {
		type?: 'doughnut' | 'bar';
		labels: string[];
		data: number[];
		colors?: string[];
		height?: number;
	} = $props();

	let canvas: HTMLCanvasElement;
	let chart: Chart | null = null;

	onMount(() => {
		const ctx = canvas.getContext('2d');
		if (!ctx) return;

		const defaultColors = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4'];
		const bgColors = colors.length ? colors : defaultColors;

		if (type === 'doughnut') {
			chart = new Chart(ctx, {
				type: 'doughnut',
				data: {
					labels,
					datasets: [
						{
							data,
							backgroundColor: bgColors.slice(0, data.length),
							borderWidth: 0,
							hoverOffset: 4
						}
					]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					cutout: '70%',
					plugins: {
						legend: {
							position: 'bottom',
							labels: {
								padding: 16,
								usePointStyle: true,
								pointStyleWidth: 10,
								font: { size: 12, family: 'inherit' }
							}
						}
					}
				}
			});
		} else {
			chart = new Chart(ctx, {
				type: 'bar',
				data: {
					labels,
					datasets: [
						{
							data,
							backgroundColor: bgColors.slice(0, data.length),
							borderWidth: 0,
							borderRadius: 6,
							barThickness: 32
						}
					]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					plugins: {
						legend: { display: false }
					},
					scales: {
						y: {
							beginAtZero: true,
							ticks: {
								stepSize: 1,
								font: { size: 12, family: 'inherit' }
							},
							grid: { color: '#f1f5f9' }
						},
						x: {
							ticks: { font: { size: 12, family: 'inherit' } },
							grid: { display: false }
						}
					}
				}
			});
		}
	});

	onDestroy(() => {
		chart?.destroy();
	});

	$effect(() => {
		if (chart) {
			chart.data.labels = labels;
			chart.data.datasets[0].data = data;
			if (colors.length) {
				chart.data.datasets[0].backgroundColor = colors.slice(0, data.length);
			}
			chart.update();
		}
	});
</script>

<div style="height: {height}px;">
	<canvas bind:this={canvas}></canvas>
</div>
