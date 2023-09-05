// since there's no dynamic data here, we can prerender
// it so that it gets served as a static asset in production
export const prerender = false

import type { Player_Score } from '$lib/types'
import type { PageLoad } from './$types'

export const load: PageLoad = async ({ url }) => {
	console.log(url)
	const response = await fetch(`${url.origin}/api/v2/player_score?top=10`)
	const result = (await response.json()) as { data: Player_Score[]; error: unknown }

	if (result.error) {
		return {
			error: result.error,
		}
	} else {
		return {
			scores: result.data,
		}
	}
}
