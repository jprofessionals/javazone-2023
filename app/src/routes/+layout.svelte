<script lang="ts">
	// Your selected Skeleton theme:
	import '@skeletonlabs/skeleton/themes/theme-skeleton.css'

	// This contains the bulk of Skeletons required styles:
	import '@skeletonlabs/skeleton/styles/skeleton.css'

	// Finally, your application's global stylesheet (sometimes labeled 'app.css')
	import '../app.css'
	import Img from '$lib/images/neko-idle.gif'

	import { AppShell } from '@skeletonlabs/skeleton'
	import Header from './Header.svelte'
	import Sidebar from '$lib/Sidebar.svelte'

	import { usbDevice } from '$lib/stores'
	import { onMount } from 'svelte'
	import { invoke } from '@tauri-apps/api/tauri'

	let usbDeviceValue: string

	usbDevice.subscribe((val) => {
		usbDeviceValue = val
	})

	let availableDevices: string[] = []

	onMount(async () => {
		const foundPorts = ((await invoke('get_available_ports')) || []) as string[]
		availableDevices = foundPorts.filter((port: string) => !port.includes('Bluetooth'))
	})

	let selectedDevice: string

	const setDevice = async () => {
		if (!selectedDevice) return
		await invoke('set_device', { device: selectedDevice })
		const device = (await invoke('get_device')) as string
		usbDevice.set(device)
	}
</script>

<AppShell>
	<svelte:fragment slot="header">
		<Header />
	</svelte:fragment>
	<svelte:fragment slot="sidebarLeft">
		<Sidebar />
	</svelte:fragment>

	<slot />

	<!-- <svelte:fragment slot="pageFooter">Footer</svelte:fragment> -->

	<div class="absolute left-2 bottom-0 bg-orange-200 p-2 rounded-t-lg flex items-end gap-4">
		<label class="label">
			<span>Select device:</span>
			<select class="select" bind:value={selectedDevice}>
				<option>Unset</option>
				{#each availableDevices as device}
					<option value={device} selected={device === usbDeviceValue}>{device}</option>
				{/each}
			</select>
		</label>
		<button class="btn variant-filled" on:click={setDevice}>Connect</button>
	</div>
	<div class="absolute -right-4 -bottom-4">
		<img src={Img} alt="dog" width="200" />
	</div>
</AppShell>
