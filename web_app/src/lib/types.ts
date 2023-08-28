export type Score = {
	id?: string
	created_at?: string
	score: number
	players: Pick<Player, 'username'>
}

export type Player = {
	id?: string
	created_at?: string
	name?: string
	username?: string
	email?: string
	score?: Score[]
}
