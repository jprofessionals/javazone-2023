import { writable } from 'svelte/store'
import type { Player, Score } from './types'

export const currentPlayer = writable({} as Player)

export const currentHighScore = writable([] as Score[])
