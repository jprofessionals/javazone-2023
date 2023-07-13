#![no_main]
#![no_std]

use src_microbit as _; // global logger + panicking-behavior + memory layout
                       //
use src_microbit::utilities::parse::parse;

use microbit::{display::blocking::Display, hal::Timer};

use cortex_m_rt::entry;

const CONFIG_DATA: &'static str = include_str!(concat!(env!("OUT_DIR"), "/config_data.rs"));

#[entry]
fn main() -> ! {
    defmt::println!("Hello, world!");
    defmt::println!("{:?}", CONFIG_DATA.trim_end());

    let vec_numbers = parse(CONFIG_DATA).unwrap(); //.expect("It to happen");

    defmt::println!("{}", vec_numbers);

    let board = microbit::Board::take().unwrap();

    let mut display = Display::new(board.display_pins);
    let mut timer = Timer::new(board.TIMER0);
    loop {
        display.show(&mut timer, vec_numbers.display, 30);
    }
}
