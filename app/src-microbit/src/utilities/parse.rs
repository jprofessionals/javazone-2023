extern crate serde;
extern crate serde_json_core;

// use core::fmt::Write;
// use heapless::String;
use defmt::Format;
use serde::{Deserialize, Serialize};

#[derive(Deserialize, Serialize, Format)]
pub struct MyJson {
    pub display: [[[u8; 5]; 5]; 5],
}

pub fn parse(json: &'static str) -> Option<MyJson> {
    // This is the JSON string we will use.
    match serde_json_core::de::from_str::<MyJson>(json) {
        Ok(result) => {
            defmt::println!("Successfully deserialized.\n");
            // print 1 element (u32)
            let display = { result.0 }; // result=(MyJson, usize) ; result.0=MyJson
            defmt::println!("display: {:?}", display);

            return Some(display);
        }
        err => {
            if err.is_err() {
                defmt::println!("shit went down");
                // display error message:
            }
        }
    }
    None
}
