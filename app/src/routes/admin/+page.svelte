<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri'
	import { onMount } from 'svelte'
	import { usbDevice } from '$lib/stores'
	import { isConfigSet } from '$lib/stores'

	let url = ''
	let apikey = ''
	let selectedDevice: string

	usbDevice.subscribe((dev) => {
		selectedDevice = dev
	})

	const validateFields = (): boolean => {
		const validUrl = !!url
		const validApikey = !!apikey
		const validPort = selectedDevice !== 'unset'
		return validUrl && validApikey && validPort
	}

	const handleSubmit = async () => {
		if (validateFields()) {
			// Your custom submission function here
			const resp = (await invoke('set_supabase_config', { url, apikey })) as string
			try {
				const config = await invoke('get_supabase_config')
				setDevice()
				isConfigSet.set(true)
				console.log({ resp, config })
			} catch (e) {
				console.log(e)
			}
		} else {
			console.log('Please fill in all fields correctly')
		}
	}

	onMount(async () => {
		try {
			const [storedUrl, storedApikey] = (await invoke('get_supabase_config')) as [string, string]
			if (storedUrl !== '') url = storedUrl
			if (storedApikey !== '') apikey = storedApikey
		} catch (e) {
			console.log(e)
		}
	})

	let usbDeviceValue: string

	usbDevice.subscribe((val) => {
		usbDeviceValue = val
	})

	let availableDevices: string[] = []

	async function getAvailablePorts() {
		const foundPorts = ((await invoke('get_available_ports')) || []) as string[]
		availableDevices = foundPorts.filter((port: string) => !port.includes('Bluetooth'))
	}

	onMount(async () => {
		await getAvailablePorts()
	})

	const setDevice = async () => {
		if (!selectedDevice) return
		await invoke('set_device', { device: selectedDevice })
		const device = (await invoke('get_device')) as string
		usbDevice.set(device)
	}
</script>

<h1>Admin yo</h1>

<div class="flex justify-center">
	<form on:submit|preventDefault={handleSubmit} class="space-y-8">
		<label class="label">
			<span>Api URL:</span>
			<input type="text" class="input" bind:value={url} />
		</label>
		<label class="label">
			<span>Api Key:</span>
			<input type="text" class="input" bind:value={apikey} />
		</label>

		<label class="label">
			<span>Select device:</span>
			<div class="flex space-x-4">
				<select class="select rounded-full" bind:value={selectedDevice}>
					<option>Unset</option>
					{#each availableDevices as device}
						<option value={device} selected={device === usbDeviceValue}>{device}</option>
					{/each}
				</select>
				<button on:click={() => getAvailablePorts()}>♻️</button>
			</div>
		</label>
		<button type="submit" class="btn variant-filled-surface self-center">Save</button>
	</form>
</div>
