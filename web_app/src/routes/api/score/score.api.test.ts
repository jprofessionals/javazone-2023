import { $fetch, setup } from 'vite-test-utils'
import { describe, expect, test } from 'vitest'

// Trick so vitest knows to re-run the tests below when +server.ts changes:
import './+server'

await setup({
	server: true,
})

describe('GET /api/score', () => {
	test('responds with the list of scores', async () => {
		const todos = await $fetch('/api/score')

		expect(todos).toEqual([
			{
				id: 1,
				text: 'test a sveltekit api endpoint with vitest',
				done: true,
			},
		])
	})
})
