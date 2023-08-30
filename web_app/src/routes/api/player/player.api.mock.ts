import type { Player } from '$lib/types'

export const mockPlayers: Player[] = [
	{
		id: '1',
		created_at: '2023-08-28T12:34:56Z',
		name: 'Frodo Baggins',
		username: 'frodo',
		email: 'frodo@example.com',
		score: [
			{ id: '1', created_at: '2023-08-28T12:34:56Z', score: 100, players: { username: 'frodo' } },
		],
	},
	{
		id: '2',
		created_at: '2023-08-28T12:34:56Z',
		name: 'Aragorn',
		username: 'aragorn',
		email: 'aragorn@example.com',
		score: [
			{ id: '2', created_at: '2023-08-28T12:34:56Z', score: 200, players: { username: 'aragorn' } },
		],
	},
	{
		id: '3',
		created_at: '2023-08-28T12:34:56Z',
		name: 'Gandalf',
		username: 'gandalf',
		email: 'gandalf@example.com',
		score: [
			{ id: '3', created_at: '2023-08-28T12:34:56Z', score: 150, players: { username: 'gandalf' } },
		],
	},
	{
		id: '4',
		created_at: '2023-08-28T12:34:56Z',
		name: 'Legolas',
		username: 'legolas',
		email: 'legolas@example.com',
		score: [
			{ id: '4', created_at: '2023-08-28T12:34:56Z', score: 250, players: { username: 'legolas' } },
		],
	},
	{
		id: '5',
		created_at: '2023-08-28T12:34:56Z',
		name: 'Gimli',
		username: 'gimli',
		email: 'gimli@example.com',
		score: [
			{ id: '5', created_at: '2023-08-28T12:34:56Z', score: 300, players: { username: 'gimli' } },
		],
	},
]
