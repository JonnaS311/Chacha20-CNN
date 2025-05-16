mod cka;
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    // El primer argumento es la url del main.exe
    println!("Número de argumentos: {}", args.len());
    for (i, arg) in args.iter().enumerate() {
        println!("Argumento {}: {}", i, arg);
    }
    //cka::write_encryp_file("music.mp3", "music_encriptada")?;
    //Ok(())
}
