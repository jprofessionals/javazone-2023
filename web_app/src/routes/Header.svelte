<script lang="ts">
	import Logo from '$lib/logo.svelte'
	import { currentPlayer } from '$lib/stores'
	import { AppBar } from '@skeletonlabs/skeleton'
	import { fade, fly } from 'svelte/transition'

	let currentPlayerName: string | undefined
	currentPlayer.subscribe((player) => {
		currentPlayerName = player.name
	})
</script>

<AppBar background="bg-slate-700" padding="pl-2">
	<svelte:fragment slot="lead">
		<Logo />
	</svelte:fragment>
	<div class="flex items-center">
		<span class="text-2xl mt-3 text-white">JavaZone 2023</span>
		{#if currentPlayerName}
			<div in:fly={{ x: 200, duration: 1000 }} out:fade>
				<span class="text-center w-full text-slate-800 mx-20 p-2 parch rounded-lg">
					Player: {currentPlayerName}
				</span>

				<button class="btn parch" on:click={() => currentPlayer.set({})}> Exit </button>
			</div>
		{/if}
	</div>
	<svelte:fragment slot="trail">
		<img
			src="https://www.icegif.com/wp-content/uploads/2023/02/icegif-519.gif"
			class="h-20"
			alt="Dog"
		/>
	</svelte:fragment>
</AppBar>
