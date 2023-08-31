<script lang="ts">
	import cn from '$utils/cn'
	import { AppBar } from '@skeletonlabs/skeleton'
	import { page } from '$app/stores'
</script>

<AppBar background="bg-transparent">
	<svelte:fragment slot="lead">
		<a href="/">
			<span class="py-4 text-2xl text-white pixel-font">
				<span class="text-orange-500">j</span>Pro
			</span>
		</a>
	</svelte:fragment>
	<svelte:fragment slot="trail">
		<nav class="text-white color-white pixel-font text-xs">
			<a href="/">
				<span class={cn($page.url.pathname === '/' && 'underline underline-offset-4')}>
					High score
				</span>
			</a>
			<a href="/rules">
				<span class={cn($page.url.pathname === '/rules' && 'underline underline-offset-4')}>
					Rules
				</span>
			</a>
		</nav>
	</svelte:fragment>
</AppBar>
