<script lang="ts">
	import '../app.css'

	import BotImg1 from '$lib/images/bot-2.png'
	import BotImg2 from '$lib/images/bot-3.png'

	import { AppShell } from '@skeletonlabs/skeleton'
	import Header from './Header.svelte'

	import { initializeStores } from '@skeletonlabs/skeleton'
	initializeStores()
</script>

<AppShell slotSidebarLeft="hidden">
	<svelte:fragment slot="header">
		<Header />
	</svelte:fragment>
	<slot />
</AppShell>

<div class="absolute bottom-0 w-full flex justify-between items-end gap-2">
	<img src={BotImg2} alt="" class="w-20 md:w-52 z-20" />

	<a
		class="relative text-white pixel-font bg-black px-4 pt-2 pb-4 text-center z-0 rounded-t-lg"
		href="https://jpro.no/stillinger"
	>
		Looking for a new job?
	</a>

	<img src={BotImg1} alt="" class="w-20 md:w-60 z-20" />
</div>
