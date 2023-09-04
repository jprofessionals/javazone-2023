import { describe, expect, it, test } from 'vitest'
import fetch from 'node-fetch'
import { pick } from 'radash'
import { SUPABASE_SERVICE_KEY } from '$env/static/private'

//
// Trick so vitest knows to re-run the tests below when +server.ts changes:
import './+server'
import { mockPlayers } from './player.api.mock'

const mockPlayer = pick(mockPlayers[0], ['name', 'username', 'email'])

describe('GET /api/players', () => {
	test('expect list of players', async () => {
		const response = await fetch('http://localhost:5173/api/player')
		expect(response.status).toBe(200)
	})
})

describe('POST /api/players', () => {
	test('expect faulty input to return error', async () => {
		const faultyPlayer = {
			name: false,
			email: 123,
			username: 2,
		}

		const response = await fetch('http://localhost:5173/api/player', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(faultyPlayer),
		})

		const body = (await response.json()) as { errors: unknown[] }
		expect(body).toHaveProperty('errors')
		expect(body.errors.length).toBe(3)
	})

	test('expect wrong length on username to return error', async () => {
		const faultyPlayer = {
			name: 'Frodo',
			email: 'Frodo@baggins.com',
			username: 'FRODOaaaaaa',
		}

		const response = await fetch('http://localhost:5173/api/player', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(faultyPlayer),
		})

		const body = (await response.json()) as { errors: unknown[] }
		expect(body).toHaveProperty('errors')
		expect(body.errors.length).toBe(1)
	})
	test('expect faulty email to return error', async () => {
		const faultyPlayer = {
			name: 'Frodo',
			email: 'Frodo',
			username: 'FRODO',
		}

		const response = await fetch('http://localhost:5173/api/player', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(faultyPlayer),
		})

		const body = (await response.json()) as { errors: unknown[] }
		expect(body).toHaveProperty('errors')
		expect(body.errors.length).toBe(1)
	})

	it('should return 201 when valid data has been sent', async (context) => {
		if (!SUPABASE_SERVICE_KEY) context.skip()
		const response = await fetch('http://localhost:5173/api/player', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(mockPlayer),
		})

		expect(response.status).toBe(201)
	})
})

describe('DELETE /api/players', () => {
	it('should return 200 when deleted', async (context) => {
		if (!SUPABASE_SERVICE_KEY) context.skip()
		const response = await fetch('http://localhost:5173/api/player', {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(mockPlayer),
		})

		expect(response.status).toBe(200)
	})
})
