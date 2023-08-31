<script lang="ts">
	import '../app.css'

	import BotImg1 from '$lib/images/bot-2.png'
	import BotImg2 from '$lib/images/bot-3.png'

	import { AppShell } from '@skeletonlabs/skeleton'
	import Header from './Header.svelte'
	import Sidebar from '$lib/Sidebar.svelte'

	import { initializeStores } from '@skeletonlabs/skeleton'
	initializeStores()
</script>

<AppShell slotSidebarLeft="hidden">
	<svelte:fragment slot="header">
		<Header />
	</svelte:fragment>
	<svelte:fragment slot="sidebarLeft">
		<Sidebar />
	</svelte:fragment>

	<slot />

	<!-- <svelte:fragment slot="pageFooter">Footer</svelte:fragment> -->
</AppShell>

<div class="absolute -left-1 md:-left-4 -bottom-1 md:-bottom-4 z-20">
	<img src={BotImg2} alt="dog" class="w-20 md:w-52" />
</div>

<a
	class="absolute left-0 right-0 bottom-0 flex justify-center text-white pixel-font z-0"
	href="https://jpro.no/stillinger"
>
	Ser du etter en ny jobb?
</a>

<div class="absolute -right-1 md:-right-4 -bottom-1 md:-bottom-4 z-20">
	<img src={BotImg1} alt="dog" class="w-20 md:w-60" />
</div>
