import { join } from 'path'
import type { Config } from 'tailwindcss'

import { skeleton } from '@skeletonlabs/tw-plugin'
import forms from '@tailwindcss/forms'
import typography from '@tailwindcss/typography'

const config = {
	darkMode: 'class',
	content: [
		'./src/**/*.{html,js,svelte,ts}',
		join(require.resolve('@skeletonlabs/skeleton'), '../**/*.{html,js,svelte,ts}'),
	],
	theme: {
		extend: {
			fontFamily: {
				fancy: ['Poppins'],
			},
			screens: {
				'3xl': '2560px',
			},
			width: {
				dscreen: '100dvw',
			},
			height: {
				dscreen: '100dvh',
			},
		},
	},
	plugins: [forms, typography, skeleton({ themes: { preset: ['skeleton', 'wintry'] } })],
} satisfies Config

export default config
