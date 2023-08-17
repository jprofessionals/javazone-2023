<script lang="ts">
	import { onMount } from 'svelte'
	import setScriptLang from '$utils/set_script_lang'

	import Editor from '$lib/Editor.svelte'
	import Documentation from '$lib/Documentation.svelte'

	onMount(() => {
		setScriptLang()
	})
</script>

<div class="grid lg:grid-cols-2 p-8 gap-10">
	<Editor />
	<Documentation />
</div>
