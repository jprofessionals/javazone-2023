<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri'
	import type { Device } from '$lib/types'

	let devices: Device[] = []
	async function scan_for_bt() {
		devices = await invoke('get_bt_devices_command')
	}
</script>

<div>
	<p>{devices}</p>
	<div>
		<label for="input" style="display: block;">Message: {devices}</label>
		<button on:click={() => scan_for_bt()}> Scan bluetooth </button>
	</div>
	<p>Devices found:</p>
	<ol>
		{#each devices as device}
			<li>{device.name} - is connected: {device.connected}</li>
		{/each}
	</ol>
</div>
