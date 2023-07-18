<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri'
	import _letters from '../letters.json'

	let greetMsg = ''

	const alphabet = _letters as { [key: string]: number[][] }

	let padding = [
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],
	]

	let message: string[] = []

	async function flash_microbit() {
		let displayList = message.map((l) => alphabet[l || 'A'])

		if (message.length > 5) {
			displayList = displayList.slice(0, 5)
		} else if (message.length < 5) {
			// pad the remaining with padding array
			for (let i = 0; i < 5 - message.length; i++) {
				displayList.push(padding)
			}
		}

		if (message.length === 3) {
			displayList = [displayList[0], padding, displayList[1], padding, displayList[2]]
		}

		greetMsg = await invoke('flash_display_nrf', {
			display: {
				display: displayList,
			},
		})
	}

	function append_letter(letter: string) {
		if (message.length < 5) {
			message = [...message, letter]
		}
	}

	function delete_last() {
		if (message.length > 0) message = message.slice(0, -1)
	}

	function reset() {
		message = []
	}
</script>

<div class="flex flex-col gap-10 items-center mt-20">
	<div class="grid grid-cols-8 gap-3">
		{#each Object.keys(alphabet) as letter}
			<button
				class="btn variant-filled"
				on:click={() => {
					append_letter(letter)
				}}
			>
				{letter}
			</button>
		{/each}
		<button class="btn variant-soft-error col-start-7" on:click={delete_last}>⬅️</button>
		<button class="btn variant-soft-error col-start-8" on:click={reset}>❌</button>
		<button
			class="btn variant-soft-success outline outline-black col-start-8"
			title="Flash message"
			on:click={flash_microbit}>↗️</button
		>
	</div>

	<div class="card min-w-[200px] flex flex-col p-2">
		<p>Text to output:</p>
		<p class="text-xl p-2 gap-2 h-10 bg-white m-2 rounded-md grid grid-cols-5">
			{#each message as letter}
				<span class="flex justify-center items-center">{letter}</span>
			{/each}
		</p>
	</div>

	<p>{greetMsg}</p>
</div>
