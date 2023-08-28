<script lang="ts">
	import cn from '$utils/cn'
	import { currentPlayer } from './stores'

	let name = 'marius'
	let email = ''
	let username = 'KNGMA'
	let usernameError = false

	const validateFields = (): boolean => {
		const validName = !!name
		const validUsername = /^[A-Z]{5}$/.test(username)
		if (!validUsername) {
			usernameError = true
		} else {
			usernameError = false
		}
		return validName && validUsername
	}

	const handleSubmit = async () => {
		if (validateFields()) {
			// Your custom submission function here
			//			const resp = (await invoke('register_player', { name, email, username })) as string
			const resp = '{}'
			try {
				currentPlayer.set(JSON.parse(resp)[0])
				console.log(resp)
			} catch (e) {
				console.log(e)
			}
		} else {
			console.log('Please fill in all fields correctly')
		}
	}
</script>

<div class="flex flex-col justify-center items-center mt-16 gap-6 h-80">
	<form on:submit|preventDefault={handleSubmit} class="flex flex-col justify-center gap-8">
		<label class="label">
			<span>Name:</span>
			<input type="text" class="input" bind:value={name} />
		</label>
		<label class="label">
			<span>Email:</span>
			<input type="email" class="input" bind:value={email} />
			<p class="text-sm">Optional, but required to enter contest</p>
		</label>
		<label class="label">
			<span>Username (5 uppercase letters):</span>
			<div class="input-group input-group-divider grid-cols-[1fr_auto]">
				<input
					type="text"
					bind:value={username}
					placeholder="Enter Username..."
					maxlength="5"
					class="uppercase"
				/>
			</div>
			<p class={cn(usernameError && 'text-error-800', !usernameError && 'invisible', 'text-sm ')}>
				Username must contain exactly 5 uppercase letters
			</p>
		</label>
		<button type="submit" class="btn variant-filled-surface self-center">PLAY</button>
	</form>
</div>
