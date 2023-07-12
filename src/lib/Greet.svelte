<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri'
	import letters from '../letters.json'

	let greetMsg = ''

	let alphabet = Object.keys(letters)

	async function greet(letter: string) {
		// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
		let commands = JSON.stringify({
			age: 130,
			display: letters[letter || 'A'],
		})
		alert(`hey ${letter}`)
		greetMsg = await invoke('flash_display_nrf', { commands })
	}
</script>

<div>
	<div class="alphabet">
		{#each alphabet as letter}
			<button on:click={() => greet(letter)}>
				{letter}
			</button>
		{/each}
	</div>

	<p>{greetMsg}</p>
</div>

<style>
	.alphabet {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
	}
</style>
