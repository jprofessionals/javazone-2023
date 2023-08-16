<script lang="ts">
	import { onDestroy, onMount } from 'svelte'
	import WebSocket from 'tauri-plugin-websocket-api'
	import type { Message } from 'tauri-plugin-websocket-api'

	export let onListen: (message: Message) => void = updateLog
	export let shouldDisplayLog: boolean = true

	let log: Array<string | Message> = []
	let ws: WebSocket | void
	onMount(async () => {
		ws = await WebSocket.connect('ws://127.0.0.1:8080')
			.then((r) => {
				updateLog('connected')
				return r
			})
			.catch(console.log)
		if (!ws) return
		ws.addListener(onListen)
	})

	onDestroy(() => {
		if (ws)
			ws.disconnect()
				.then(() => updateLog('disconnected'))
				.catch(console.log)
	})

	export async function send(message: Message | string) {
		if (ws) {
			try {
				await ws.send(message)
				updateLog('Message sent')
				updateLog(message)
			} catch (error: unknown) {
				updateLog(error as string)
			}
		}
	}
	function updateLog(entry: Message | string) {
		if (!shouldDisplayLog) return

		log = [...log, entry]
	}
</script>

{#if shouldDisplayLog}
	<h1>Websocket log:</h1>

	<ul>
		{#each log as item}
			<li>{JSON.stringify(item)}</li>
		{/each}
	</ul>
{/if}
