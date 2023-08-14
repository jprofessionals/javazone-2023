// use serde::{Deserialize, Serialize};
use std::error::Error;
use std::time::Duration;
use tokio::time;

use btleplug::api::{Central, CharPropFlags, Manager as _, Peripheral, ScanFilter};
use btleplug::platform::Manager;
use futures::stream::StreamExt;

use super::bt_scan::Device;

pub async fn connect(device: String) -> Result<Vec<Device>, Box<dyn Error>> {
    println!("Got here");

    let manager = Manager::new().await?;
    let adapters = manager.adapters().await?;
    let adapter = adapters.get(0).expect("No adapters found");
    adapter.start_scan(ScanFilter::default()).await?;
    time::sleep(Duration::from_secs(3)).await;
    let peripherals = adapter.peripherals().await?;

    let mut devices: Vec<Device> = vec![];

    for peripheral in peripherals.iter() {
        let properties = peripheral.properties().await?;
        let is_connected = peripheral.is_connected().await?;
        let local_name = properties
            .clone()
            .unwrap()
            .local_name
            .unwrap_or(String::from("unknown"));
        println!("Hey {}", local_name);
        if local_name == device {
            if !is_connected {
                println!("Connecting to peripheral {:?}...", &local_name);
                if let Err(err) = peripheral.connect().await {
                    eprintln!("Error connecting to peripheral, skipping: {}", err);
                    continue;
                }
            }
            println!("Connected to peripheral {:?}!", &local_name);
            let is_connected = peripheral.is_connected().await?;

            if is_connected {
                println!("Discover peripheral {:?} services...", &local_name);
                peripheral.discover_services().await?;
                for char in peripheral.characteristics() {
                    println!("Checking char {:?}", char);
                    // Subscribe to notifications from the char with the selected
                    // UUID.
                    if char.properties.contains(CharPropFlags::NOTIFY) {
                        println!("Subscribing to char {:?}", char.uuid);
                        peripheral.subscribe(&char).await?;
                        // Print the first 4 notifications received.
                        let mut notification_stream = peripheral.notifications().await?.take(4);
                        // // Process while the BLE connection is not broken or stopped.
                        while let Some(data) = notification_stream.next().await {
                            println!(
                                "Received data from {:?} [{:?}]: {:?}",
                                local_name, data.uuid, data.value
                            );
                        }
                    }
                    println!("Disconnecting from peripheral {:?}...", local_name);
                    peripheral.disconnect().await?;
                }
            }
            println!("{:?}", properties);
            devices.push(Device {
                name: local_name,
                connected: is_connected,
            })
        }
    }

    Ok(devices)
}
