// since there's no dynamic data here, we can prerender
// it so that it gets served as a static asset in production
export const prerender = false

import type { Score } from '$lib/types'
import type { PageLoad } from './$types'

export const load: PageLoad = async ({ url }) => {
	const response = await fetch(`${url.href}api/v2/player_score?top=10`)
	const result = (await response.json()) as { data: Score[]; error: unknown }

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
