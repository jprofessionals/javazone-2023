<script lang="ts">
	import cn from '$utils/cn'
	import { usbDevice } from './stores'
	import WebSocket from './WebSocket.svelte'

	const valid_instructions = [
		'move_forward()j',
		'move_left()j',
		'move_right()j',
		'u_turn()j',
		'start()j',
	] as const

	type Instruction = (typeof valid_instructions)[number]
	type CodeLine = {
		text: [Instruction, string] | ['start()j']
		error?: boolean
		byte_value?: 'F' | 'L' | 'R' | 'U' | 'S'
	}
	const byte_value: Record<Instruction, 'F' | 'L' | 'R' | 'U' | 'S'> = {
		'move_forward()j': 'F',
		'move_left()j': 'L',
		'move_right()j': 'R',
		'u_turn()j': 'U',
		'start()j': 'S',
	}

	const example = [
		{ text: ['move_forward()j'], byte_value: 'F' },
		{ text: ['move_left()j'], byte_value: 'L' },
		{ text: ['move_forward()j'], byte_value: 'F' },
		{ text: ['start()j'], byte_value: 'S' },
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
			const splitLine = line.split('*')
			// Valid instruction
			if (
				splitLine.length === 1 &&
				valid_instructions.includes(splitLine[0].toLowerCase() as Instruction)
			) {
				const instruction = splitLine[0] as Instruction
				return {
					text: splitLine,
					byte_value: byte_value[instruction],
				} as CodeLine
			} else if (splitLine.length === 1 && splitLine[0].trim() === '') {
				// Allow whitespace/empty lines
				return {
					text: splitLine,
				} as CodeLine
				// Found multiplier, indicating multiple instructions on same line
			}
			return {
				text: splitLine,
				error: true,
			} as CodeLine
		})

	let usbDevicePort: string
	usbDevice.subscribe((val) => {
		usbDevicePort = val
	})

	let websocketChild: {
		send: (msg: string) => Promise<void>
	}
	// Send to websocket server the parsed instructions in byte values
	const sendToBitBot = async () => {
		if (usbDevicePort === 'unset') return // Need to set usbdevice before playing
		if (code.filter(({ error }) => error).length > 0) return
		const msg = code
			.filter((line) => line.byte_value !== undefined)
			.map(({ byte_value }) => byte_value)
			.join('')
		await websocketChild.send(`${usbDevicePort};${msg}`)
	}
</script>

<div class="flex flex-col gap-10 items-center">
	<h2 class="h3">Write your program here:</h2>
	<div class="flex w-2/3 gap-2 p-2 bg-slate-700 rounded-xl">
		<div class="flex flex-col text-slate-300 text-sm leading-6">
			{#each Array(Math.max(1, numOfLines)) as num, index}
				<span class={`leading-6 ${num}`}>
					{index + 1}
				</span>
			{/each}
		</div>
		<textarea
			on:keyup={textareaOnKeyup}
			class="flex leading-6 p-0 bg-slate-700 text-white border-none outline-none w-full"
			value={currentText}
			spellcheck="false"
			rows={15}
		/>
		<div class="flex flex-col text-slate-300 text-sm">
			{#each code as line}
				<span
					class={cn(
						'first:rounded-tr-lg last:rounded-br-lg leading-6 bg-green-300 h-6 w-2',
						line.error && 'bg-red-600',
					)}
				/>
			{/each}
		</div>
	</div>
	<button on:click={sendToBitBot} class="btn variant-filled">Send to bitbot</button>
	<WebSocket bind:this={websocketChild} />
</div>
