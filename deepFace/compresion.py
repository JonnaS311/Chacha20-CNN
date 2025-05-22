import numpy as np
from sklearn.decomposition import PCA

# --------- CONFIGURACIÓN INICIAL (SE ENTRENA UNA VEZ) ---------

# Simula un dataset de entrenamiento para generar PCA (esto lo puedes cambiar)
# Usa tu dataset real aquí
np.random.seed(42)
training_data = np.random.uniform(-1, 1, size=(10000, 128))

# Entrena PCA para reducir de 128D a 64D
pca = PCA(n_components=64)
pca.fit(training_data)
projection_matrix = pca.components_  # forma: (64, 128)

# --------- FUNCIONES AUXILIARES ---------

def apply_pca(x, projection_matrix):
    """
    Aplica la reducción PCA con una matriz fija.
    """
    return projection_matrix @ x  # Resultado: (64,)

def quantize_4bit(x, min_val=-1.0, max_val=1.0):
    """
    Cuantiza valores en rango [min_val, max_val] a 4 bits (0–15).
    """
    x_clipped = np.clip(x, min_val, max_val)
    x_scaled = ((x_clipped - min_val) / (max_val - min_val) * 15).astype(np.uint8)
    return x_scaled  # valores de 0 a 15 (4 bits)

def pack_4bit(values_4bit):
    """
    Empaqueta dos valores de 4 bits en un byte.
    """
    packed = bytearray()
    for i in range(0, len(values_4bit), 2):
        byte = (values_4bit[i] << 4) | values_4bit[i + 1]
        packed.append(byte)
    return bytes(packed)  # Longitud: 32 bytes para 64 valores

# --------- FUNCIÓN PRINCIPAL ---------

def compress_embedding(x: np.ndarray) -> bytes:
    """
    Convierte un embedding de 128 floats a exactamente 32 bytes (256 bits).
    
    Args:
        x (np.ndarray): Embedding de forma (128,) y tipo float32/float64.
    
    Returns:
        bytes: Embedding comprimido (32 bytes).
    """
    if x.shape != (128,):
        raise ValueError("El embedding debe tener forma (128,)")
    
    # Paso 1: Aplicar PCA
    x_proj = apply_pca(x, projection_matrix)

    # Paso 2: Cuantizar a 4 bits
    x_q = quantize_4bit(x_proj, min_val=-1.0, max_val=1.0)

    # Paso 3: Empaquetar
    compressed = pack_4bit(x_q)
    return compressed
