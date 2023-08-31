<script lang="ts">
	import Leaderboard from '$lib/Leaderboard.svelte'
	import type { PageData } from './$types'

	export let data: PageData
</script>

<Leaderboard {...data} />
