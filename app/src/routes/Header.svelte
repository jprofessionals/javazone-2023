<script>
	import Logo from '$lib/logo.svelte'
	import { AppBar } from '@skeletonlabs/skeleton'
</script>

<AppBar background="bg-slate-700" padding="pl-2">
	<svelte:fragment slot="lead">
		<Logo />
	</svelte:fragment>
	<span class="text-2xl mt-6 text-white">JavaZone 2023</span>
	<svelte:fragment slot="trail">
		<img
			src="https://www.icegif.com/wp-content/uploads/2023/02/icegif-519.gif"
			class="h-20"
			alt="Dog"
		/>
	</svelte:fragment>
</AppBar>
