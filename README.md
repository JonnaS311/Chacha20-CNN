
# Chacha20-CNN

Este proyecto combina técnicas de visión por computadora y criptografía para implementar un sistema de reconocimiento facial utilizando redes neuronales convolucionales (CNN) y el cifrado ChaCha20 para proteger los datos sensibles.

## 📂 Estructura del Proyecto

- **`cara.py`**: Script principal para capturar imágenes faciales y generar embeddings.
- **`mi_cara_embedding.json`**: Archivo JSON que almacena los embeddings faciales generados.
- **`requeriment.txt`**: Lista de dependencias necesarias para ejecutar el proyecto.

## 🚀 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/JonnaS311/Chacha20-CNN.git
   cd Chacha20-CNN
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requeriment.txt
   ```

## 🧠 Uso

Ejecuta el script principal para capturar una imagen facial y generar su embedding:

```bash
python cara.py
```

El embedding generado se almacenará en el archivo `mi_cara_embedding.json`.

## 🔐 Seguridad

Este proyecto utiliza el algoritmo de cifrado ChaCha20 para proteger los embeddings faciales, asegurando que los datos sensibles estén resguardados contra accesos no autorizados.

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 👤 Autor

Desarrollado por [Jonnathan Sotelo](https://github.com/JonnaS311).
