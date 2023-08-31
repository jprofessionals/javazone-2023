<script lang="ts">
	import '../app.css'
	import Img from '$lib/images/neko-idle.gif'

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

	<div class="absolute -left-4 -bottom-4" style="transform: rotateY(180deg)">
		<img src={Img} alt="dog" width="200" />
	</div>
	<div class="absolute right-0 bottom-0" style="transform: rotateY(180deg)">
		<img
			src="https://www.icegif.com/wp-content/uploads/2023/02/icegif-519.gif"
			class="h-32"
			alt="Dog"
		/>
	</div>
</AppShell>
