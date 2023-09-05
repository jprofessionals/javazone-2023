import { json } from '@sveltejs/kit'
import { z } from 'zod'
import type { RequestHandler } from './$types'
import { getSupabaseClient } from '$utils/db_client'
import { validateCUDRequest } from '$utils/validate'

const supabase = getSupabaseClient('service')

export const GET: RequestHandler = async ({ url }) => {
	const top = url.searchParams.get('top')

	if (top) {
		if (Number(top) > 0) {
			const result = await supabase
				.from('player_scores')
				.select('score, player_username, player_email')
				.order('score', { ascending: false })
				.limit(Number(top))
			return json(result)
		} else {
			return new Response('Invalid top parameter for highscore, must be a number above 0', {
				status: 500,
			})
		}
	}

	const result = await supabase.from('player_scores').select('score, player_username, player_email')

	return json(result)
}

const playerScoreSchema = z.object({
	score: z.number({
		required_error: 'Really? No score?',
	}),
	player_username: z
		.string({
			required_error: 'Username is required',
		})
		.trim()
		.toUpperCase()
		.min(3, 'username must be at least 3 character')
		.max(5, 'username must be at most 5 characters'),
	player_email: z.string().trim().email('Must be a proper email').optional(),
})

export const POST: RequestHandler = async ({ request }) => {
	const isValid = validateCUDRequest(request.headers.get('secret'))
	if (!isValid) {
		return new Response('Unauthorized', { status: 401 })
	}
	const newScore = await request.json()
	const scoreData = playerScoreSchema.safeParse(newScore)
	// If score data is not valid, return invalid request
	if (!scoreData.success) {
		const errors = scoreData.error.errors.map((err) => err.message)
		return new Response(JSON.stringify({ errors }), { status: 400 })
	}

	const result = await supabase.from('player_scores').insert(scoreData.data)

	if (result.status !== 201) {
		console.error(result.error)
		return new Response('Something went wrong', { status: 500 })
	}

	return new Response('Created successfully', { status: 201 })
}
