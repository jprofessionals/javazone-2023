<script lang="ts">
	import cn from '$utils/cn'
	import { onDestroy, onMount } from 'svelte'

	import type { Player_Score } from './types'
	import { scale } from 'svelte/transition'

	export let scores: Player_Score[] = []

	let loading = false

	const refreshScores = async () => {
		const response = await fetch('/api/v2/player_score?top=10')
		const { data, error } = await response.json()
		if (error) console.error(error)
		else {
			await new Promise((resolve) =>
				setTimeout(() => {
					scores = data
					resolve(0)
				}, 600),
			)
		}
	}

	let intervalId: ReturnType<typeof setInterval>

	onMount(async () => {
		intervalId = setInterval(async () => {
			await refreshScores()
		}, 7000) // refresh every 5 seconds
	})

	onDestroy(() => {
		clearInterval(intervalId)
	})

	const onRefresh = async () => {
		loading = true
		await refreshScores()
		loading = false
	}
</script>

<svelte:head>
	<title>JProZone 2023</title>
</svelte:head>

<div class="container max-w-full h-full relative pb-20">
	<div class="text-4xl flex flex-col gap-12 relative items-center py-10 w-full h-full">
		<button
			class="h1 max-w-lg text-white text-center [text-shadow:_4px_4px_0_rgb(100_100_100_/_60%)] pixel-font"
			on:click={onRefresh}
		>
			Current Leaderboard
		</button>
		<ol class={cn('md:text-5xl text-3xl flex flex-col gap-4 relative')}>
			{#if loading}
				<p class="pixel-font text-white animate-pulse">Loading...</p>
			{:else}
				{#each scores as highscore, index (highscore.id)}
					<li
						in:scale
						class={cn(
							'text-white',
							index === 0 && 'text-[#FFD700]',
							index === 1 && 'text-[#d0d0d0]',
							index === 2 && 'text-[#cd7f32]',
							'[text-shadow:_4px_4px_0_rgb(100_100_100_/_60%)]',
							'flex gap-10 justify-between pixel-font',
						)}
					>
						<span title={highscore.player_email}>{highscore.player_username}</span>
						<!-- Pad the score with 0's -->
						<span>{String(highscore.score).padStart(2, '0')}</span>
					</li>
				{/each}
			{/if}
		</ol>
	</div>
</div>
