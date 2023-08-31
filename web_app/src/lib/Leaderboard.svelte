<script lang="ts">
	import cn from '$utils/cn'

	import { onMount } from 'svelte'
	import type { Score } from './types'

	let scores: Score[] = []

	onMount(async () => {
		await refreshScores()
	})

	const refreshScores = async () => {
		scores = []
		const response = await fetch('/api/score?top=10')
		const { data, error } = await response.json()
		if (error) console.error(error)
		else {
			setTimeout(() => {
				scores = data
			}, 300)
		}
	}
</script>

<svelte:head>
	<title>JProZone 2023</title>
</svelte:head>

<div class="container max-w-full h-full z-10 relative">
	<div class="text-4xl flex flex-col gap-12 relative items-center py-10 w-full h-full">
		<button
			class="h1 max-w-lg text-white text-center [text-shadow:_4px_4px_0_rgb(100_100_100_/_60%)] pixel-font"
			on:click={refreshScores}
		>
			Current Leaderboard
		</button>
		<ol class={cn('md:text-5xl text-3xl flex flex-col gap-4 relative')}>
			{#if scores.length === 0}
				<p class="pixel-font text-white animate-pulse">Loading...</p>
			{:else}
				{#each scores as highscore, index}
					<li
						class={cn(
							'text-white',
							index === 0 && 'text-[#FFD700]',
							index === 1 && 'text-[#d0d0d0]',
							index === 2 && 'text-[#cd7f32]',
							'[text-shadow:_4px_4px_0_rgb(100_100_100_/_60%)]',
							'flex gap-10 justify-between pixel-font',
						)}
					>
						<span title={highscore.player.email}>{highscore.player.username}</span>
						<!-- Pad the score with 0's -->
						<span>{String(highscore.score).padStart(3, '0')}</span>
					</li>
				{/each}
			{/if}
		</ol>
	</div>
</div>
