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

	<div class="absolute -right-4 -bottom-4">
		<img src={Img} alt="dog" width="200" />
	</div>
</AppShell>
