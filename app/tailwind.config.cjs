/** @type {import('tailwindcss').Config} */
module.exports = {
	// 1. Apply the dark mode class setting:
	darkMode: 'class',
	content: [
		'./src/**/*.{html,js,svelte,ts}',
		// 2. Append the path for the Skeleton NPM package and files:
		require('path').join(require.resolve('@skeletonlabs/skeleton'), '../**/*.{html,js,svelte,ts}'),
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
	plugins: [
		require('@tailwindcss/forms'),
		...require('@skeletonlabs/skeleton/tailwind/skeleton.cjs')(),
	],
}
