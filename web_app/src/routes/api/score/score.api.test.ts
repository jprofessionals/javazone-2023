import { afterAll, describe, expect, it } from 'vitest'
import fetch from 'node-fetch'
import { LOCAL_BASE_URL, SUPABASE_SERVICE_KEY } from '$env/static/private'

// Trick so vitest knows to re-run the tests below when +server.ts changes:
import './+server'

describe('GET /api/score', () => {
	it('responds with the list of scores', async () => {
		const result = await fetch(`${LOCAL_BASE_URL}/api/score`)

		expect(result.status).toEqual(200)

		const scores = (await result.json()) as { data: unknown[] }

		expect(scores.data).toBeInstanceOf(Array)
		expect(scores.data.length).toBeGreaterThan(0)
	})

	it('responds with top x amount of scores ', async () => {
		const result = await fetch(`${LOCAL_BASE_URL}/api/score?top=3`)

		expect(result.status).toEqual(200)

		const scores = (await result.json()) as { data: unknown[] }

		expect(scores.data).toBeInstanceOf(Array)
		expect(scores.data.length).toBe(3)
	})
	it('responds with error with invalid top param', async () => {
		const result = await fetch(`${LOCAL_BASE_URL}/api/score?top=umptheen-thousand`)
		expect(result.status).toEqual(500)
	})
})

describe('POST /api/players', () => {
	it('expect faulty input to return error', async () => {
		const faultyScore = {
			player: 123,
			score: 'two thousand',
		}

		const response = await fetch(`${LOCAL_BASE_URL}/api/player`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(faultyScore),
		})

		const body = (await response.json()) as { errors: unknown[] }
		expect(body).toHaveProperty('errors')
		expect(body.errors.length).toBe(2)
	})

	it('expect multiple score records to be created', async (context) => {
		if (!SUPABASE_SERVICE_KEY) context.skip()
		const score1 = {
			player: 'ingvild@gatsby.no',
			score: 10,
		}
		const score2 = {
			player: 'ingvild@gatsby.no',
			score: 11,
		}

		console.log('wh')

		console.log('hey')
		const response = await fetch(`${LOCAL_BASE_URL}/api/score`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(score1),
		})

		expect(response.status).toEqual(201)

		const response2 = await fetch(`${LOCAL_BASE_URL}/api/score`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(score2),
		})

		expect(response2.status).toEqual(201)
	})

	afterAll(async () => {
		if (SUPABASE_SERVICE_KEY) {
			await fetch(`${LOCAL_BASE_URL}/api/score`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ email: 'ingvild@gatsby.no' }),
			})
		}
	})
})
