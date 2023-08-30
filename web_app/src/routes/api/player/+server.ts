import { json } from '@sveltejs/kit'
import { z } from 'zod'
import type { RequestHandler } from './$types'
import { getSupabaseClient } from '$utils/db_client'

const supabase = getSupabaseClient('service')

const playerSchema = z.object({
	name: z
		.string({
			required_error: 'Name is required',
		})
		.trim()
		.min(1),
	username: z
		.string({
			required_error: 'Username is required',
		})
		.trim()
		.toUpperCase()
		.min(1, 'username must be at least 1 character')
		.max(5, 'username must be at most 5 characters'),
	email: z.string().trim().email('Must be a proper email').optional(),
})

export const GET: RequestHandler = async () => {
	const result = await supabase.from('players').select()

	return json(result)
}

export const POST: RequestHandler = async ({ request }) => {
	const newPlayer = await request.json()
	const playerData = playerSchema.safeParse(newPlayer)
	// If player data is not valid, return an error
	if (!playerData.success) {
		const errors = playerData.error.errors.map((err) => err.message)
		return new Response(JSON.stringify({ errors }), { status: 400 })
	}

	const existingPlayer = (await supabase
		.from('players')
		.select('email')
		.eq('email', newPlayer.email)) as { data: unknown[] }

	if (existingPlayer?.data?.length > 0) {
		return new Response('Player with that email already exists', { status: 400 })
	}

	const result = await supabase.from('players').insert(newPlayer)
	if (result.status !== 201) return new Response('Something went wrong', { status: 500 })

	return new Response('Created successfully', { status: 201 })
}

export const DELETE: RequestHandler = async ({ request }) => {
	const req = (await request.json()) as { email: string }
	if (!req.email) {
		return new Response('Please provide email to delete', { status: 400 })
	}

	const result = await supabase.from('players').delete().eq('email', req.email)
	if (result.error) {
		return new Response(result.error.message, { status: 500 })
	}

	return new Response(`Player with email ${req.email} was deleted successfully`, { status: 200 })
}
