<script lang="ts">
	import cn from '$utils/cn'
	import { fade, slide } from 'svelte/transition'

	let input = ''

	type Log = {
		source: 'device' | 'application'
		message: string
	}

	// fill log with 5 examples
	let log: Log[] = [
		{
			source: 'device',
			message: 'Hello world',
		},
		{
			source: 'application',
			message: 'Hello world',
		},
		{
			source: 'device',
			message: 'Hello world',
		},
		{
			source: 'application',
			message: 'Hello world',
		},
		{
			source: 'device',
			message: 'Hello world',
		},
	]

	function send_to_device() {
		log = [...log, { source: 'application', message: input }]
		input = ''
	}
</script>

<div>
	<span>Send to bluetooth:</span>
	<form on:submit|preventDefault={send_to_device}>
		<input type="text" bind:value={input} />
		<input type="submit" class="btn variant-filled btn-sm" value="↩️" />
	</form>
</div>

<h2 class="h4">Log:</h2>
<div class="bg-white m-4 flex flex-col w-1/2 py-4 gap-2">
	{#each log as entry}
		<span
			transition:slide={{ duration: 300 }}
			class={cn(
				entry.source === 'application' && 'self-end bg-slate-300 px-2 py-1 rounded-l-full',
				entry.source === 'device' && 'self-start bg-green-300 px-2 py-1 rounded-r-full',
				'',
			)}
		>
			From: {entry.source}, Message: {entry.message}
		</span>
	{/each}
</div>
