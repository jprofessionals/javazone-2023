<script lang="ts">
	import cn from '$utils/cn'

	type Direction = 'LEFT' | 'FORWARD' | 'RIGHT'
	type CodeLine = {
		text: [Direction, string] | ['START']
		error?: boolean
	}

	const example = [
		{ text: ['FORWARD', '2'] },
		{ text: ['LEFT', '90'] },
		{ text: ['FORWARD', '10'] },
		{ text: ['START'] },
	] as CodeLine[]

	let code: CodeLine[] = example

	let currentText = code.map((line) => line.text.join(' ')).join('\n')

	let numOfLines = code.length

	function textareaOnKeyup(event: KeyboardEvent) {
		const target = event.target as HTMLTextAreaElement
		const text = target.value.split('\n')
		numOfLines = text.length
		code = parseText(text)
	}
	const parseText = (code: string[]): CodeLine[] =>
		code.map((line) => {
			const splitLine = line.split(' ')
			if (splitLine.length === 1 && splitLine[0].toUpperCase() === 'START') {
				return {
					text: splitLine,
				} as CodeLine
			} else if (splitLine.length === 1 && splitLine[0].trim() === '') {
				return {
					text: splitLine,
				} as CodeLine
			} else if (splitLine.length === 2) {
				const [dir, val] = splitLine
				if (['FORWARD', 'LEFT', 'RIGHT'].includes(dir.toUpperCase()) && !isNaN(Number(val))) {
					return {
						text: splitLine,
					} as CodeLine
				}
			}
			return {
				text: splitLine,
				error: true,
			} as CodeLine
		})
</script>

Write your program here:
<div class="flex">
	<div class="m-10 w-fit flex flex-col items-end gap-10">
		<div class="flex gap-2 p-2 bg-slate-700 w-fit rounded-xl">
			<div class="flex flex-col text-slate-300 text-sm">
				{#each Array(Math.max(1, numOfLines)) as _, index}
					<span class="leading-6">
						{index + 1}
					</span>
				{/each}
			</div>
			<textarea
				on:keyup={textareaOnKeyup}
				class="flex leading-6 px-2 bg-slate-700 text-white border-none outline-none w-96"
				value={currentText}
				rows={15}
			/>
			<div class="flex flex-col text-slate-300 text-sm">
				{#each code as line}
					<span class={cn('leading-6 bg-green-300 h-6 w-2', line.error && 'bg-red-600')} />
				{/each}
			</div>
		</div>
		<button class="btn variant-filled">Send to bitbot</button>
	</div>
	<div class="card w-80 p-4 mt-10 bg-amber-100 parch prose">
		<p>Instruction manual</p>
		<p>Forward: X amount of cm's to move forward</p>
		<p>Left: X amount of degrees to move to the left</p>
		<p>Right: X amount of degrees to move to the right</p>
		<p>Start: Kick off the program</p>
	</div>
</div>
