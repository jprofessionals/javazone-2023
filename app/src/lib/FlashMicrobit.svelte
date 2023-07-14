<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri'
	import _letters from '../letters.json'

	let greetMsg = ''

	const letters = _letters as { [key: string]: number[][] }

	let alphabet = Object.keys(letters)

	async function flash_microbit(letter: string) {
		// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
		let commands = JSON.stringify({
			age: 130,
			display: letters[letter || 'A'],
		})

		alert(`hey ${letter}`)
		greetMsg = await invoke('flash_display_nrf', { commands })
	}

	let message: string[] = []
</script>

<div class="alphabet">
	{#each alphabet as letter}
		<button
			on:click={() => {
				message = [...message, letter]
			}}
		>
			{letter}
		</button>
	{/each}
	{message.join('')}
</div>

<p>{greetMsg}</p>

<style>
	.alphabet {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
	}
</style>
