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
		video.webkitRequestFullScreen()
		video.play()
	}

	function stopPresentation() {
		video.webkitExitFullScreen()
		playing = false
	}

	function onEnd() {
		refreshScore().then(() => {
			stopPresentation()
			setTimeout(() => {
				startPresentation()
			}, 45000)
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
	width="100%"
	height="100%"
	controls
	bind:this={video}
	class={cn(!playing && 'invisible', 'absolute')}
>
	<track kind="captions" />
</video>
