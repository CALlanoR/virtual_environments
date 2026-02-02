import re

texto = "El pedido incluye los productos XY-502, MZ-110 y el erróneo A1-99."

# Patrón: 
# [A-Z]{2} -> Dos letras mayúsculas
# -         -> Un guion literal
# \d{3}     -> Tres dígitos
patron = r'[A-Z]{2}-\d{3}'

# Extraer todos los que cumplan la regla
productos_validos = re.findall(patron, texto)

print(f"Productos encontrados: {productos_validos}")
# Salida: ['XY-502', 'MZ-110']