<script lang="ts">
	import { currentPlayer } from '$lib/stores'
	import { AppBar } from '@skeletonlabs/skeleton'
	import { fade, fly } from 'svelte/transition'

	let currentPlayerName: string | undefined
	currentPlayer.subscribe((player) => {
		currentPlayerName = player.name
	})
</script>

<AppBar background="bg-black starry">
	<svelte:fragment slot="lead">
		<span class="py-4 text-2xl text-white pixel-font">
			<span class="text-orange-500">j</span>Pro
		</span>
	</svelte:fragment>
	<div class="flex items-center">
		{#if currentPlayerName}
			<div in:fly={{ x: 200, duration: 1000 }} out:fade>
				<span class="text-center w-full text-slate-800 mx-20 p-2 parch rounded-lg">
					Player: {currentPlayerName}
				</span>

				<button class="btn parch" on:click={() => currentPlayer.set({})}> Exit </button>
			</div>
		{/if}
	</div>
	<svelte:fragment slot="trail" />
</AppBar>
