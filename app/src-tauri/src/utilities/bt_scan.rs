use serde::{Deserialize, Serialize};
use std::error::Error;
use std::time::Duration;
use tokio::time;

use btleplug::api::{Central, Manager as _, Peripheral, ScanFilter};
use btleplug::platform::Manager;

pub async fn bt_scan() -> Vec<u8> {
    time::sleep(Duration::from_secs(3)).await;
    vec![0, 1, 23]
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Device {
    pub name: String,
    pub connected: bool,
}

pub async fn bt_scanner() -> Result<Vec<Device>, Box<dyn Error>> {
    println!("Got here");

    let manager = Manager::new().await?;
    let adapter_list = manager.adapters().await?;
    if adapter_list.is_empty() {
        eprintln!("No Bluetooth adapters found");
        return Ok(vec![]);
    }

    let mut devices = vec![];

    for adapter in adapter_list.iter() {
        println!("Starting scan on {}...", adapter.adapter_info().await?);
        adapter
            .start_scan(ScanFilter::default())
            .await
            .expect("Can't scan BLE adapter for connected devices...");
        time::sleep(Duration::from_secs(3)).await;
        let peripherals = adapter.peripherals().await?;
        // println!("{:?}", peripherals);
        if peripherals.is_empty() {
            eprintln!("->>> BLE peripheral devices were not found, sorry. Exiting...");
        } else {
            // All peripheral devices in range
            for peripheral in peripherals.iter() {
                let properties = peripheral.properties().await?;
                let is_connected = peripheral.is_connected().await?;
                let local_name = properties
                    .clone()
                    .unwrap()
                    .local_name
                    .unwrap_or(String::from("unknown"));
                if local_name != "unknown" {
                    devices.push(Device {
                        name: local_name,
                        connected: is_connected,
                    });
                }
                //}
            }
        }
        println!("Finished scan on {}...", adapter.adapter_info().await?)
    }
    Ok(devices)
}
