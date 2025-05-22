mod cka;
use std::env;
use std::error::Error;

fn main()-> Result<(), Box<dyn Error>>  {
    let args: Vec<String> = env::args().collect();
    /*
    println!("Número de argumentos: {}", args.len());
    for (i, arg) in args.iter().enumerate() {
        println!("Argumento {}: {}", i, arg);
    }
    */

    if args.len() > 4 && &args[1]=="0"{
        cka::write_encryp_file(&args[2], &args[3], &args[4])?; 
    }else if  args.len() > 5 && &args[1]=="1" {
        cka::write_desencryp_file(&args[2], &args[3], &args[4], &args[5])?; 
    }else {
        println!("Uso: <modo> <programa> <nombre> <key> <formato>");
    }
    
    Ok(())
}
