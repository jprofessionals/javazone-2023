// Moved this into a separate file, as my editor went haywire on the el.innerHTML line.
export default function setScriptLang() {
	const el = document.querySelector('.codeblock-language')
	if (el) {
		el.innerHTML = 'JProScript'
	}
}
