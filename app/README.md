# JavaZone 2023 client app

> A Tauri application with a SvelteKit frontend

This application was developed to be run on our client machines on our stand at JavaZone 2023. It is complemented by a BitBot:XL car that is used to drive around a track of our own design, and in order to communicate with this car through a microbit chip, it was decided to try out Tauri in order to tap into a rich Rust ecosystem for interfacing with the computers hardware.

## Getting up and running

In order to start developing this application some pre-requisites need to be installed on the computer.

### Pre-requisites

- Node, I developed with Node 18

Example install with homebrew:

```sh
  brew install node@18
```

Alternative install methods: [Read here](https://nodejs.org/en/download/package-manager)

- pnpm (A faster package manager than npm. It's blazingly fast ⚡)

Ironically, we can use npm to install pnpm

```sh
npm i -g pnpm
```

- Install node modules. (in root of this project)

```sh
pnpm install
```

- RustLang, install with following shell command:

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

After installing Rust, Cargo (the package manager) should also be installed.

- Tauri CLI, installed with cargo

```sh
  cargo install tauri-cli
```

### Developing

Then:

```
cargo tauri dev
```

The application should then appear as a separate window

### The stack

Frontend:

- Svelte
- SvelteKit
- TypeScript
- TailwindCSS
- Skeleton UI
- Prettier+Eslint

"Backend":

- Rust
- Tauri
- Supabase (database for player and score data)
- Serialport-rs (Library for interfacing with the microbit through serial)
