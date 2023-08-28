<script>
	import { page } from '$app/stores'
	import { AppRail, AppRailAnchor } from '@skeletonlabs/skeleton'
</script>

<AppRail background="bg-slate-700" class="text-white">
	<svelte:fragment slot="lead" />
	<!-- --- -->
	<AppRailAnchor href="/" selected={$page.url.pathname === '/'}>
		<div class="flex flex-col">
			<span class="text-3xl leading-none">🏠</span>
			<span>Home</span>
		</div>
	</AppRailAnchor>
	<AppRailAnchor href="/leaderboard" selected={$page.url.pathname === '/leaderboard'}>
		<div class="flex flex-col">
			<span class="text-3xl leading-none">🤩</span>
			<span>Leaderboard</span>
		</div>
	</AppRailAnchor>
</AppRail>
