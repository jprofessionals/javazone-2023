<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri'
	import type { Device } from '$lib/types'

	let connected_device = ''

	let devices: Device[] = []
	let scanning_for_bt = false
	async function scan_for_bt() {
		connected_device = ''
		scanning_for_bt = true
		devices = await invoke('get_bt')
		scanning_for_bt = false
	}

	async function connect_to_bt_device(device: string) {
		devices = await invoke('connect_to_bt_device', { device })
		connected_device = device
	}
</script>

<div class="p-4 flex flex-col gap-4 items-center">
	<button on:click={() => scan_for_bt()} class="btn variant-filled"> Scan bluetooth </button>
	{#if connected_device === ''}
		<p>Devices found:</p>
		{#if scanning_for_bt}
			Scanning...
		{/if}
		<ol class="flex flex-col gap-4">
			{#each devices as device}
				<li>
					<span>{device.name} - is connected: {device.connected}</span>
					<button
						class="btn btn-sm variant-filled-surface"
						on:click={() => connect_to_bt_device(device.name)}
					>
						Connect
					</button>
				</li>
			{/each}
		</ol>
	{:else}
		<p>Connected to: {connected_device}</p>
	{/if}
</div>
