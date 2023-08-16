<script lang="ts">
	import WebSocket from 'tauri-plugin-websocket-api'
	import { onDestroy, onMount } from 'svelte'
	import { invoke } from '@tauri-apps/api/tauri'

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let ws: any
	let response = ''
	let message = ''

	onMount(async () => {
		ws = await WebSocket.connect('ws://127.0.0.1:8080')
			.then((r) => {
				_updateResponse('Connected')
				return r
			})
			.catch(_updateResponse)
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		ws.addListener((msg: any) => {
			console.log(msg)
			_updateResponse(msg)
		})
	})

	let devices: string[] = []
	onMount(async () => {
		devices = await invoke('get_available_ports')
	})

	onDestroy(disconnect)

	let resultObj: any

	const send_over_serial = async () => {
		const result: string = await invoke('send_over_serial', { message })
		try {
			resultObj = JSON.parse(result)
			console.log(resultObj)
		} catch (e) {
			console.log('whoops')
		}
	}

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const _updateResponse = (returnValue: string | any) => {
		response +=
			(typeof returnValue === 'string' ? returnValue : JSON.stringify(returnValue)) + '<br>'
	}

	async function send() {
		try {
			await ws.send(message)
			_updateResponse('Message sent')
		} catch (error) {
			_updateResponse(error)
		}
	}

	function disconnect() {
		ws.disconnect()
			.then(() => _updateResponse('Disconnected'))
			.catch(_updateResponse)
	}
	// import Leaderboard from '$lib/Leaderboard.svelte'
</script>

<div>
	<input bind:value={message} />
	<button on:click={send}>Send</button>
	<button on:click={() => send_over_serial()}>Send to bit</button>
</div>
<div>{@html response}</div>
<ul>
	{#each devices as device}
		<li
			on:click={async () =>
				await invoke('connect_to_selected_port', { port: device, message: 'Yeah' })}
		>
			{device}
		</li>
	{/each}
</ul>
<!-- <BluetoothScan /> -->
