export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[]

export interface Database {
	public: {
		Tables: {
			players: {
				Row: {
					created_at: string | null
					email: string | null
					id: string
					name: string | null
					username: string | null
				}
				Insert: {
					created_at?: string | null
					email?: string | null
					id?: string
					name?: string | null
					username?: string | null
				}
				Update: {
					created_at?: string | null
					email?: string | null
					id?: string
					name?: string | null
					username?: string | null
				}
				Relationships: []
			}
			profiles: {
				Row: {
					avatar_url: string | null
					full_name: string | null
					id: string
					updated_at: string | null
					username: string | null
					website: string | null
				}
				Insert: {
					avatar_url?: string | null
					full_name?: string | null
					id: string
					updated_at?: string | null
					username?: string | null
					website?: string | null
				}
				Update: {
					avatar_url?: string | null
					full_name?: string | null
					id?: string
					updated_at?: string | null
					username?: string | null
					website?: string | null
				}
				Relationships: [
					{
						foreignKeyName: 'profiles_id_fkey'
						columns: ['id']
						referencedRelation: 'users'
						referencedColumns: ['id']
					},
				]
			}
			scores: {
				Row: {
					created_at: string | null
					id: string
					player: string
					score: number
				}
				Insert: {
					created_at?: string | null
					id?: string
					player: string
					score?: number
				}
				Update: {
					created_at?: string | null
					id?: string
					player?: string
					score?: number
				}
				Relationships: [
					{
						foreignKeyName: 'scores_player_fkey'
						columns: ['player']
						referencedRelation: 'players'
						referencedColumns: ['id']
					},
				]
			}
		}
		Views: {
			[_ in never]: never
		}
		Functions: {
			[_ in never]: never
		}
		Enums: {
			[_ in never]: never
		}
		CompositeTypes: {
			[_ in never]: never
		}
	}
}
