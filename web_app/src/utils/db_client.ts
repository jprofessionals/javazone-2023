import { createClient } from '@supabase/supabase-js'
import type { Database } from '$lib/database.types'
import { SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY } from '$env/static/private'

export const getSupabaseClient = (role: 'anon' | 'service') =>
	createClient<Database>(
		SUPABASE_URL,
		// Only use service key if role is 'service' and sevrice key is defined in env vars
		role === 'service' && SUPABASE_SERVICE_KEY ? SUPABASE_SERVICE_KEY : SUPABASE_ANON_KEY,
		{
			auth: { persistSession: false },
		},
	)
