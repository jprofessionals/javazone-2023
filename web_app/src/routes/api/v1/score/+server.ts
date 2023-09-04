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
				.from('scores')
				.select('score, player(name, username, email)')
				.order('score', { ascending: false })
				.limit(Number(top))
			return json(result)
		} else {
			return new Response('Invalid top parameter for highscore, must be a number above 0', {
				status: 500,
			})
		}
	}

	const result = await supabase.from('scores').select('score, player(name, username, email)')

	return json(result)
}

const scoreSchema = z.object({
	score: z.number({
		required_error: 'Really? No score?',
	}),
	player: z
		.string({
			required_error: 'We need a score email to save the score',
		})
		.email(),
})

export const POST: RequestHandler = async ({ request }) => {
	const isValid = validateCUDRequest(request.headers.get('secret'))
	if (!isValid) {
		return new Response('Unauthorized', { status: 401 })
	}
	const newScore = await request.json()
	const scoreData = scoreSchema.safeParse(newScore)
	// If score data is not valid, return an error
	if (!scoreData.success) {
		const errors = scoreData.error.errors.map((err) => err.message)
		return new Response(JSON.stringify({ errors }), { status: 400 })
	}

	const player = (await supabase
		.from('players')
		.select('id')
		.eq('email', newScore.player)
		.limit(1)
		.single()) as { data: { id: string } }

	if ('id' in player.data) {
		const result = await supabase
			.from('scores')
			.insert({ player: player.data.id, score: newScore.score })
		if (result.status !== 201) return new Response('Something went wrong', { status: 500 })

		return new Response('Created successfully', { status: 201 })
	}

	return new Response('Player with email provided does not exist, try with a registered user', {
		status: 400,
	})
}

const getPlayerIdByEmail = async (email: string) => {
	const player = (await supabase
		.from('players')
		.select('id')
		.eq('email', email)
		.limit(1)
		.single()) as { data: { id: string } }
	return player.data.id
}

export const DELETE: RequestHandler = async ({ request }) => {
	const isValid = validateCUDRequest(request.headers.get('secret'))
	if (!isValid) {
		return new Response('Unauthorized', { status: 401 })
	}
	const req = (await request.json()) as { email: string }
	if (!req.email) {
		return new Response('Please provide email to delete', { status: 400 })
	}

	const playerId = await getPlayerIdByEmail(req.email)

	const result = await supabase.from('scores').delete().eq('player', playerId)
	if (result.error) {
		return new Response(result.error.message, { status: 500 })
	}

	console.log(result)

	return new Response(`Score with email ${req.email} was deleted successfully`, { status: 200 })
}
