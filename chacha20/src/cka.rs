use std::convert::TryInto;
use std::convert::TryInto;
use std::fs;
use std::io::{Read, Write};

use chacha20poly1305::aead::{Aead, KeyInit};
use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce};
use rand::RngCore;
use sha2::{Digest, Sha256};

/// Cifra el archivo en `path` y lo escribe como `./{name}.cka`.
/// Formato: HEADER(10) || NONCE(12) || CT||TAG
use std::io::{Read, Write};

use chacha20poly1305::aead::{Aead, KeyInit};
use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce};
use rand::RngCore;
use sha2::{Digest, Sha256};

/// Cifra el archivo en `path` y lo escribe como `./{name}.cka`.
/// Formato: HEADER(10) || NONCE(12) || CT||TAG
pub fn write_encryp_file(path: &str, name: &str, password: &str) -> Result<(), std::io::Error> {
    // Leer datos
    let data = fs::read(path)?;

    // Derivar clave de 32 bytes con SHA-256
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    let key_bytes = hasher.finalize();
    let key = Key::from_slice(&key_bytes);
    let cipher = ChaCha20Poly1305::new(key);

    // Generar nonce aleatorio de 12 bytes
    let mut nonce_bytes = [0u8; 12];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);
    // Leer datos
    let data = fs::read(path)?;

    // Derivar clave de 32 bytes con SHA-256
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    let key_bytes = hasher.finalize();
    let key = Key::from_slice(&key_bytes);
    let cipher = ChaCha20Poly1305::new(key);

    // Generar nonce aleatorio de 12 bytes
    let mut nonce_bytes = [0u8; 12];
    rand::thread_rng().fill_bytes(&mut nonce_bytes);
    let nonce = Nonce::from_slice(&nonce_bytes);

    // Cifrar datos
    let ciphertext = cipher
        .encrypt(nonce, data.as_ref())
        .map_err(|_| std::io::Error::new(std::io::ErrorKind::Other, "Error de cifrado"))?;

    // Construir header: 0x00, 'c','h','a', 0x00 + ext (4 bytes) + padding hasta 10
    let mut header = vec![0x00, b'c', b'h', b'a', 0x00];
    let ext = path.split('.').last().unwrap_or("");
    header.extend(ext.bytes().take(4));
    header.resize(10, 0);

    // Escribir archivo final
    let mut out = Vec::new();
    out.extend(&header);
    out.extend(&nonce_bytes);
    out.extend(&ciphertext);
    // Cifrar datos
    let ciphertext = cipher
        .encrypt(nonce, data.as_ref())
        .map_err(|_| std::io::Error::new(std::io::ErrorKind::Other, "Error de cifrado"))?;

    // Construir header: 0x00, 'c','h','a', 0x00 + ext (4 bytes) + padding hasta 10
    let mut header = vec![0x00, b'c', b'h', b'a', 0x00];
    let ext = path.split('.').last().unwrap_or("");
    header.extend(ext.bytes().take(4));
    header.resize(10, 0);

    // Escribir archivo final
    let mut out = Vec::new();
    out.extend(&header);
    out.extend(&nonce_bytes);
    out.extend(&ciphertext);

    fs::write(format!("./{}.cka", name), out)?;
    fs::write(format!("./{}.cka", name), out)?;
    Ok(())
}

/// Descifra el archivo `path` (.cka) y lo escribe como `./{name}.{formato}`.
/// Se espera: HEADER(10) || NONCE(12) || CT||TAG
/// Descifra el archivo `path` (.cka) y lo escribe como `./{name}.{formato}`.
/// Se espera: HEADER(10) || NONCE(12) || CT||TAG
pub fn write_desencryp_file(
    path: &str,
    name: &str,
    password: &str,
    formato: &str,
) -> Result<(), std::io::Error> {
    // Leer todo el archivo
    let mut file = fs::read(path)?;
    if file.len() < 10 + 12 + 16 {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "Archivo demasiado corto",
        ));
    }

    // Quitar header
    file.drain(0..10);
    // Leer nonce
    let nonce_bytes: [u8; 12] = file.drain(0..12).collect::<Vec<u8>>()[..]
        .try_into()
        .unwrap();

    // Resto = CT||TAG
    let ciphertext = file;

    // Derivar clave
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    let key_bytes = hasher.finalize();
    let key = Key::from_slice(&key_bytes);
    let cipher = ChaCha20Poly1305::new(key);
    let nonce = Nonce::from_slice(&nonce_bytes);
    // Leer todo el archivo
    let mut file = fs::read(path)?;
    if file.len() < 10 + 12 + 16 {
        return Err(std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "Archivo demasiado corto",
        ));
    }

    // Quitar header
    file.drain(0..10);
    // Leer nonce
    let nonce_bytes: [u8; 12] = file.drain(0..12).collect::<Vec<u8>>()[..]
        .try_into()
        .unwrap();

    // Resto = CT||TAG
    let ciphertext = file;

    // Derivar clave
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    let key_bytes = hasher.finalize();
    let key = Key::from_slice(&key_bytes);
    let cipher = ChaCha20Poly1305::new(key);
    let nonce = Nonce::from_slice(&nonce_bytes);

    // Descifrar (verifica tag internamente)
    let plaintext = cipher.decrypt(nonce, ciphertext.as_ref()).map_err(|_| {
        std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "Tag Poly1305 no coincide o descifrado fallido",
        )
    })?;

    // Escribir resultado
    let mut f = fs::File::create(format!("./{}.{}", name, formato))?;
    f.write_all(&plaintext)?;
    // Descifrar (verifica tag internamente)
    let plaintext = cipher.decrypt(nonce, ciphertext.as_ref()).map_err(|_| {
        std::io::Error::new(
            std::io::ErrorKind::InvalidData,
            "Tag Poly1305 no coincide o descifrado fallido",
        )
    })?;

    // Escribir resultado
    let mut f = fs::File::create(format!("./{}.{}", name, formato))?;
    f.write_all(&plaintext)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roundtrip() {
        let pwd = "password123";
        let orig = "test.txt";
        fs::write(orig, b"Hola, mundo!").unwrap();
        write_encryp_file(orig, "salida", pwd).unwrap();
        write_desencryp_file("./salida.cka", "recuperado", pwd, "txt").unwrap();
        let recovered = fs::read_to_string("./recuperado.txt").unwrap();
        assert_eq!(recovered, "Hola, mundo!");
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roundtrip() {
        let pwd = "password123";
        let orig = "test.txt";
        fs::write(orig, b"Hola, mundo!").unwrap();
        write_encryp_file(orig, "salida", pwd).unwrap();
        write_desencryp_file("./salida.cka", "recuperado", pwd, "txt").unwrap();
        let recovered = fs::read_to_string("./recuperado.txt").unwrap();
        assert_eq!(recovered, "Hola, mundo!");
    }
}
 