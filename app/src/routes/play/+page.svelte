<script>
	import Editor from '$lib/Editor.svelte'
	import { CodeBlock, storeHighlightJs } from '@skeletonlabs/skeleton'
	import hljs from 'highlight.js'
	import 'highlight.js/styles/github-dark.css'
	import { onMount } from 'svelte'
	storeHighlightJs.set(hljs)
	import setScriptLang from '$utils/set_script_lang'

	onMount(() => {
		setScriptLang()
	})
</script>

<div class="grid lg:grid-cols-2 p-8 justify-center gap-10">
	<Editor />
	<div class="flex flex-col gap-4">
		<h2 class="h3">"JProScript" documentation</h2>
		<CodeBlock
			language="ts"
			code={`// move forward to next intersection
move_forward()j 

// move left in intersection
move_left()j 

// move right in intersection
move_right()j 

// attempt to turn 180 degrees
u_turn()j 

// Kick off the program
start()j 
      `}
		/>
	</div>
</div>
