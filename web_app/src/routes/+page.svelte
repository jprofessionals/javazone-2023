<script lang="ts">
	import Leaderboard from '$lib/Leaderboard.svelte'
	import RegisterPlayer from '$lib/RegisterPlayer.svelte'
	import { currentPlayer } from '$lib/stores'

	let wantToPlay = false
	let currPlayer: string | undefined
	currentPlayer.subscribe((plr) => {
		currPlayer = plr.username
	})
</script>

{#if currPlayer}
	<Leaderboard />
{:else}
	<div>
		<h2 class="h2 text-center mt-10">Want to play?</h2>
		{#if wantToPlay}
			<RegisterPlayer />
		{:else}
			<div class="flex justify-center mt-8 gap-6">
				<div>
					<button
						on:click={() => {
							wantToPlay = true
						}}
						class="btn variant-filled">Click here to register</button
					>
				</div>
			</div>
		{/if}
	</div>
{/if}
