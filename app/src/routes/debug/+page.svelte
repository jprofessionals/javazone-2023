<script>
	import BluetoothDebugger from '$lib/BluetoothDebugger.svelte'
	import BluetoothScan from '$lib/BluetoothScan.svelte'
	// Bluetooth page for debugging bluetooth, when that was a thing
</script>

<div class="p-10 flex flex-col gap-4">
	<div class="card p-4">
		<h2>Bluetooth scanner</h2>
		<BluetoothScan />
	</div>
	<div class="card p-4">
		<h2>Send message to bluetooth device</h2>
		<BluetoothDebugger />
	</div>
</div>
