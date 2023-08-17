<script lang="ts">
	import { invoke } from '@tauri-apps/api/tauri'
	import { onMount } from 'svelte'

	let url = ''
	let apikey = ''

	const validateFields = (): boolean => {
		const validUrl = !!url
		const validApikey = !!apikey
		return validUrl && validApikey
	}

	const handleSubmit = async () => {
		if (validateFields()) {
			// Your custom submission function here
			const resp = (await invoke('set_supabase_config', { url, apikey })) as string
			try {
				const config = await invoke('get_supabase_config')
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
		<button type="submit" class="btn variant-filled-surface self-center">Save</button>
	</form>
</div>
