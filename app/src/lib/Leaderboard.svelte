<script lang="ts">
	import cn from '$utils/cn'
	import { onMount } from 'svelte'
	import type { Score } from './types'
	import { currentHighScore } from '$lib/stores'
	import { invoke } from '@tauri-apps/api/tauri'

	const sourceData: Score[] = [
		{ score: 10, player: { username: 'MARIO' } },
		{ score: 108, player: { username: 'PEACH' } },
		{ score: 40, player: { username: 'LUIGI' } },
		{ score: 69, player: { username: 'DNKNG' } },
		{ score: 9, player: { username: 'BWSER' } },
	].sort((a, b) => {
		if (a.score > b.score) return -1
		if (a.score < b.score) return 1
		return 0
	})

	let highScoreData: Score[]

	currentHighScore.subscribe((hs) => {
		highScoreData = hs
	})

	onMount(async () => {
		const scores = (await invoke('get_highscore')) as string
		try {
			currentHighScore.set(JSON.parse(scores))
			console.log(currentHighScore)
		} catch (e) {
			console.log(e)
			currentHighScore.set(sourceData)
		}
		console.log(scores)
	})
</script>

<svelte:head>
	<title>JProZone 2023</title>
</svelte:head>

<div class="container h-full flex items-center flex-col gap-16 pt-32">
	<h1 class="h1">Current Leaderboard</h1>

	<ol class="text-4xl flex flex-col gap-4 bg-black p-10 starry">
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
