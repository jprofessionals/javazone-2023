use postgrest::Postgrest;
use serde::{Deserialize, Serialize};

pub struct SupabaseConfig {
    pub apikey: String,
    pub url: String,
}

fn get_client(config: SupabaseConfig) -> Postgrest {
    Postgrest::new(config.url).insert_header("apikey", config.apikey)
}

pub async fn db_read_players(config: SupabaseConfig) -> String {
    let client = get_client(config);
    let resp = client
        .from("players")
        .select("*,scores(score)")
        .execute()
        .await
        .unwrap();
    resp.text().await.unwrap()
}

pub async fn db_get_highscores(config: SupabaseConfig) -> String {
    let client = get_client(config);
    let resp = client
        .from("scores")
        .select("score, players(username)")
        .order("score.desc")
        .limit(5)
        .execute()
        .await
        .unwrap();
    resp.text().await.unwrap()
}

#[derive(Serialize, Deserialize, Debug)]
struct Player {
    name: String,
    username: String,
    email: Option<String>,
}

pub async fn db_register_player(
    name: String,
    username: String,
    email: Option<String>,
    config: SupabaseConfig,
) -> String {
    let client = get_client(config);

    // let player = format!(
    //     r#"{{"name": {}, "username": {}, "email": {}}}"#,
    //     name, username, email
    // );

    let player = Player {
        name,
        username,
        email,
    };

    println!("player: {:?}", player);

    let json = serde_json::to_string(&player).unwrap();

    let resp = client.from("players").insert(json).execute().await.unwrap();
    let response_text = resp.text().await.unwrap();
    println!("{}", response_text);
    response_text
}
