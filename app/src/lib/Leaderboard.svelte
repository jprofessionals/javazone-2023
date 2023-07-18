<script lang="ts">
	import cn from '$utils/cn'

	const sourceData = [
		{ name: 'Mario', score: 10, avatar: 'H', username: 'MARIO' },
		{ name: 'Princess Peach', score: 108, avatar: 'B', username: 'PEACH' },
		{ name: 'Luigi', score: 40, avatar: 'He', username: 'LUIGI' },
		{ name: 'Donkey Kong', score: 69, avatar: 'Li', username: 'DNKNG' },
		{ name: 'Bowser', score: 9, avatar: 'Be', username: 'BWSER' },
	].sort((a, b) => {
		if (a.score > b.score) return -1
		if (a.score < b.score) return 1
		return 0
	})

</script>

<svelte:head>
	<title>JProZone 2023</title>
</svelte:head>

<div class="container h-full flex items-center flex-col gap-16 pt-32">
	<h1 class="h1">Current Leaderboard</h1>

	<ol class="text-4xl flex flex-col gap-4 bg-black p-10 starry">
		{#each sourceData as player, index}
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
				<span>{player.username}</span>
				<!-- Pad the score with 0's -->
				<span>{String(player.score).padStart(3, '0')}</span>
			</li>
		{/each}
	</ol>
</div>
