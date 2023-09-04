<script lang="ts">
	import '../app.css'

	import BotImg1 from '$lib/images/bot-2.png'
	import BotImg2 from '$lib/images/bot-3.png'
	import Neko from '$lib/images/neko-idle.gif'

	import { Confetti } from 'svelte-confetti'

	import { AppShell } from '@skeletonlabs/skeleton'
	import Header from './Header.svelte'

	import { initializeStores } from '@skeletonlabs/skeleton'
	initializeStores()

	let bot1clicked = false
	let bot2clicked = false

	function toggleBot(which: 1 | 2) {
		if (which === 1) {
			bot1clicked = !bot1clicked
		} else {
			bot2clicked = !bot2clicked
		}
	}
</script>

<AppShell slotSidebarLeft="hidden">
	<svelte:fragment slot="header">
		<Header />
	</svelte:fragment>
	<slot />
</AppShell>

<div class="absolute bottom-0 w-full flex justify-between items-end gap-2">
	<button on:click={() => toggleBot(2)} class="z-20">
		{#if bot2clicked}
			<Confetti />
		{/if}
		{#if bot2clicked}
			<img
				src={Neko}
				alt=""
				class="w-20 md:w-52 z-20"
				style={bot2clicked ? 'transform:rotateY(180deg)' : ''}
			/>
		{:else}
			<img
				src={BotImg2}
				alt=""
				class="w-20 md:w-52 z-20"
				style={bot2clicked ? 'transform:rotateY(180deg)' : ''}
			/>
		{/if}
	</button>

	<a
		class="relative text-white pixel-font bg-black px-4 pt-2 pb-4 text-center z-0 rounded-t-lg"
		href="https://jpro.no/stillinger"
	>
		Looking for a new job?
	</a>

	<button on:click={() => toggleBot(1)} class="z-20">
		<img src={bot1clicked ? Neko : BotImg1} alt="" class="w-20 md:w-60 z-20" />
		{#if bot1clicked}
			<Confetti />
		{/if}
	</button>
</div>
