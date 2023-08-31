<script lang="ts">
	import cn from '$utils/cn'

	//	import { onMount } from 'svelte'
	import type { Score } from './types'
	// import { currentHighScore } from '$lib/stores'
	const sourceData: Score[] = [
		{ score: 10, players: { username: 'MARIO' } },
		{ score: 108, players: { username: 'PEACH' } },
		{ score: 40, players: { username: 'LUIGI' } },
		{ score: 69, players: { username: 'DNKNG' } },
		{ score: 9, players: { username: 'BWSER' } },
	].sort((a, b) => {
		if (a.score > b.score) return -1
		if (a.score < b.score) return 1
		return 0
	})

	let highScoreData: Score[] = sourceData

	// currentHighScore.subscribe((hs) => {
	// 	highScoreData = hs
	// })
	//
</script>

<svelte:head>
	<title>JProZone 2023</title>
</svelte:head>

<div class={'container max-w-full h-full'}>
	<div class={cn('text-4xl flex flex-col gap-12  relative items-center py-10', 'w-full h-full')}>
		<h1
			class={cn(
				'h1 max-w-lg text-white text-center [text-shadow:_4px_4px_0_rgb(100_100_100_/_60%)] pixel-font',
			)}
		>
			Current Leaderboard
		</h1>
		<ol class={cn('text-5xl flex flex-col gap-4 relative')}>
			{#each highScoreData as highscore, index}
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
					<span>{highscore.players.username}</span>
					<!-- Pad the score with 0's -->
					<span>{String(highscore.score).padStart(3, '0')}</span>
				</li>
			{/each}
		</ol>
	</div>
</div>
