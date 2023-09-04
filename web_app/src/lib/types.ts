export type Score = {
	id?: string
	created_at?: string
	score: number
	player: Player
}

export type Player = {
	id?: string
	created_at?: string
	name?: string
	username?: string
	email?: string
}

export type Player_Score = {
	id?: number
	created_at?: string
	player_username: string
	score: number
	player_email?: string
}
