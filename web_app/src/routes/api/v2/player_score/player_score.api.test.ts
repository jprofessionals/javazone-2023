import { describe, expect, it } from 'vitest'
import fetch from 'node-fetch'
import { LOCAL_BASE_URL, SECRET_KEY, SUPABASE_SERVICE_KEY } from '$env/static/private'

// Trick so vitest knows to re-run the tests below when +server.ts changes:
import './+server'

const mock_scores = [
	{
		score: 10,
		player_email: 'mario@ninteno.no',
		player_username: 'MARIO',
	},
	{
		score: 11,
		player_email: 'peach@nintendo.no',
		player_username: 'PEACH',
	},
	{
		score: 43,
		player_email: 'donkey@nintendo.no',
		player_username: 'DNKNG',
	},
	{
		score: 20,
		player_email: 'geralt@rivia.no',
		player_username: 'GERLT',
	},
	{
		score: 19,
		player_email: 'yennefer@vengerberg.no',
		player_username: 'YNNFR',
	},
]

describe('POST /api/v2/player_score', () => {
	it('expect faulty input to return error', async () => {
		const faultyScore = {
			player_email: 123,
			score: 'two thousand',
		}

		const response = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				secret: SECRET_KEY,
			},
			body: JSON.stringify(faultyScore),
		})

		const body = (await response.json()) as { errors: unknown[] }
		expect(body).toHaveProperty('errors')
		expect(body.errors.length).toBe(3)
	})

	it('expect multiple score records to be created', async (context) => {
		if (!SUPABASE_SERVICE_KEY) context.skip()

		const response = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				secret: SECRET_KEY,
			},
			body: JSON.stringify(mock_scores[0]),
		})

		expect(response.status).toEqual(201)

		const response2 = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				secret: SECRET_KEY,
			},
			body: JSON.stringify(mock_scores[1]),
		})

		expect(response2.status).toEqual(201)
		const response3 = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				secret: SECRET_KEY,
			},
			body: JSON.stringify(mock_scores[2]),
		})

		expect(response3.status).toEqual(201)
		const response4 = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				secret: SECRET_KEY,
			},
			body: JSON.stringify(mock_scores[3]),
		})

		expect(response4.status).toEqual(201)
		const response5 = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				secret: SECRET_KEY,
			},
			body: JSON.stringify(mock_scores[4]),
		})

		expect(response5.status).toEqual(201)
	})
})

describe('GET /api/v2/player_score', () => {
	it('responds with the list of scores', async () => {
		const result = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score`)

		expect(result.status).toEqual(200)

		const scores = (await result.json()) as { data: unknown[] }

		expect(scores.data).toBeInstanceOf(Array)
		expect(scores.data.length).toBeGreaterThan(0)
	})

	it('responds with top x amount of scores ', async () => {
		const result = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score?top=3`)

		expect(result.status).toEqual(200)

		const scores = (await result.json()) as { data: unknown[] }

		expect(scores.data).toBeInstanceOf(Array)
		expect(scores.data.length).toBe(3)
	})
	it('responds with error with invalid top param', async () => {
		const result = await fetch(`${LOCAL_BASE_URL}/api/v2/player_score?top=umptheen-thousand`)
		expect(result.status).toEqual(500)
	})
})
