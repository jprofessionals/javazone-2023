<script lang="ts">
	import Leaderboard from '$lib/Leaderboard.svelte'
	import Video from '$lib/images/jpro-promo.mp4'
	import cn from '$utils/cn'
	import type { PageData } from './$types'
	export let data: PageData

	let video: HTMLVideoElement
	let playing = false
	let refreshScoreFunc: () => Promise<void>
	async function refreshScore() {
		await refreshScoreFunc()
	}

	function startPresentation() {
		playing = true
		video.play()
	}

	function stopPresentation() {
		playing = false
	}

	function onEnd() {
		refreshScore().then(() => {
			stopPresentation()
			setTimeout(() => {
				startPresentation()
			}, 10000)
		})
	}
</script>

<p class="text-white">Playing: {playing}</p>
<button class="btn variant-filled" on:click={() => startPresentation()}>Start</button>
<button class="btn variant-filled" on:click={() => stopPresentation()}>Stop</button>
<Leaderboard {...data} bind:refreshScores={refreshScoreFunc} />
<video
	src={Video}
	on:ended={onEnd}
	controls
	bind:this={video}
	on:click={stopPresentation}
	class={cn(!playing && 'invisible', 'absolute z-50 block top-0 w-dscreen h-dscreen bg-black')}
>
	<track kind="captions" />
</video>
