use  std::fs;

pub struct ChcaCha20 {
    pub counter:usize
}

impl ChcaCha20 {
    pub fn cifrar(&mut self, plain: Vec<u32>, password:String ) -> Vec<u32> {
        let mut counter_tmp = self.counter;
        let mut cypher: Vec<u32> = Vec::new();

        // obtenemos la cantidad de rondas de encriptación que debe hacer
        let iteraciones = plain.len().wrapping_div_euclid(16);

        for k in 0..iteraciones  {
            // creamos el bloque en esa iteración
            let bloque: [[u32; 4]; 4] = chacha(password.clone(), counter_tmp);
            counter_tmp = counter_tmp.wrapping_add(1);   
            let mut tmp = sumar(plain[k*16..(k+1)*16].to_vec(), bloque);
            // añadimos el bloque cifrado
            cypher.append(&mut tmp);
        }
        cypher.append(&mut plain[(iteraciones)*16..plain.len()].to_vec());

        cypher
    }
}

fn chacha(mut key: String, counter: usize) -> [[u32; 4]; 4] {
    let expand_key: &[u8] = "er4un50nid0frioK".as_bytes();
    let nonce: [u32; 3] = [194057 as u32, 22709 as u32, 42157 as u32];

    if key.len() < 32 {
        let tam = 32 - key.len();
        for _ in 0..tam {
            key += "*";
        }
    }

    let key_char: &[u8] = key.as_bytes();

    let mut matrix: [[u32; 4]; 4] = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]];

    // llenar con el expand key la matriz

    for i in 0..4 {
        matrix[0][i] = expand_key[i * 4] as u32
            + expand_key[i * 4 + 1] as u32
            + expand_key[i * 4 + 2] as u32
            + expand_key[i * 4 + 3] as u32;
    }

    // llenar la key en la matriz

    for j in 1..3 {
        for i in 0..4 {
            matrix[j][i] = key_char[i * 4 * j] as u32
                + key_char[i * 4 * j + 1] as u32
                + key_char[i * 4 * j + 2] as u32
                + key_char[i * 4 * j + 3] as u32;
        }
    }

    // llenar counter & nonce
    // generar números aleatorios random.gen_range(0..4294967296 as i64) as u32;
    matrix[3][0] = counter as u32;
    matrix[3][1] = nonce[0];
    matrix[3][2] = nonce[1];
    matrix[3][3] = nonce[2];

    for _ in 0..20 {
        // Realizar las 20 rondas
        for i in 0..4 {
            horizontal(i, &mut matrix);
        }

        for i in 0..4 {
            diagonal(i, &mut matrix);
        }
    }

    matrix
}

fn horizontal(level: usize, matrix: &mut [[u32; 4]; 4]) {
    let (a, b) = matrix.split_at_mut(1);
    let (b, c) = b.split_at_mut(1);
    let (c, d) = c.split_at_mut(1);
    let (d, _) = d.split_at_mut(1);

    quarter_round(
        &mut a[0][level],
        &mut b[0][level],
        &mut c[0][level],
        &mut d[0][level],
    );
}

fn diagonal(level: usize, matrix: &mut [[u32; 4]; 4]) {
    let (a, b) = matrix.split_at_mut(1);
    let (b, c) = b.split_at_mut(1);
    let (c, d) = c.split_at_mut(1);
    let (d, _) = d.split_at_mut(1);

    quarter_round(
        &mut a[0][level % 4],
        &mut b[0][(level + 1) % 4],
        &mut c[0][(level + 2) % 4],
        &mut d[0][(level + 3) % 4],
    );
}

fn quarter_round(a: &mut u32, b: &mut u32, c: &mut u32, d: &mut u32) {
    // se debe realizar una ronda de ARX (adición, rotación y XOR)

    fn rotar(x: u32, n: u32) -> u32 {
        return (x << n) | (x >> (32 - n)) as u32;
    }

    *a = a.wrapping_add(*b);
    *d ^= *a;
    rotar(*d, 16);

    *c = c.wrapping_add(*d);
    *b ^= *c;
    rotar(*b, 12);

    *a = a.wrapping_add(*b);
    *d ^= *a;
    rotar(*d, 8);

    *c = c.wrapping_add(*d);
    *b ^= *c;
    rotar(*b, 7);
}

fn sumar(plain: Vec<u32>, bloque: [[u32; 4]; 4]) -> Vec<u32>{
    let mut contador: usize = 0;
    let mut cypher:Vec<u32> = Vec::new();
    for i in bloque {
        for j in i {
            cypher.push(plain[contador] as u32 ^ j);
            contador += 1;
        }
    }
   cypher
}

pub fn write_encryp_file(path: &str, name: &str, password: &str) -> Result<(), std::io::Error>{

       let data: Vec<u8> = fs::read(path)?;
       let to_32: Vec<u32> = data.iter().map(|&c| c as u32).collect();
   
       let mut cifrador = ChcaCha20 { counter: 0 };
   
       let datos_cifrados = cifrador.cifrar(to_32.clone(), String::from(password));
   
       //let datos_resueltos:Vec<u32> = cifrador.cifrar(datos_cifrados, String::from("unaLlaveSimple"));
   
       // Convertir el Vec<u32> en Vec<u8>
       let mut byte_data: Vec<u8> = datos_cifrados
           .iter()
           .map(|&num| num as u8) // Convertir cada u32 en un array de 4 bytes
           .collect();
   
       let Some((index,_)) = path.char_indices().find(|(_, c)| *c == '.') else {
           panic!("not exist format on that file");
       };
   
       let cadena = path.as_bytes();
   
       // Encabezado del formato .cka 
       byte_data.insert(0, 0x00);
       byte_data.insert(1, 0x63);
       byte_data.insert(2, 0x68);
       byte_data.insert(3, 0x61);
       byte_data.insert(4, 0x00);
       byte_data.insert(5, match cadena.get(index+1){
           Some(x) => *x,
           None => 0x00
       });
       byte_data.insert(6, match cadena.get(index+2){
           Some(x) => *x,
           None => 0x00
       });
       byte_data.insert(7, match cadena.get(index+3){
           Some(x) => *x,
           None => 0x00
       });
       byte_data.insert(8, match cadena.get(index+4){
           Some(x) => *x,
           None => 0x00
       });
       byte_data.insert(9, 0x00);
   
       fs::write(format!("./{}.cka",name), byte_data)?;

       Ok(())
}


pub fn write_desencryp_file(path: &str, name: &str, password: &str, formato: &str) -> Result<(), std::io::Error>{
    let mut data: Vec<u8> = fs::read(path)?;
    data.drain(0..10);

    let to_32: Vec<u32> = data.iter().map(|&c| c as u32).collect();

    let mut descifrador = ChcaCha20 { counter: 0 };

    let datos_descifrados = descifrador.cifrar(to_32.clone(), String::from(password));

    // Convertir el Vec<u32> en Vec<u8>
    let byte_data: Vec<u8> = datos_descifrados
    .iter()
    .map(|&num| num as u8) // Convertir cada u32 en un array de 4 bytes
    .collect();

    fs::write(format!("./{}.{}",name, formato), byte_data)?;

    Ok(())
}
