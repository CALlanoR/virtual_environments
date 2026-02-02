import re

def validar_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(patron, email):
        return True
    else:
        return False

# Pruebas
emails_a_probar = ["usuario@dominio.com", "hola.mundo@empresa.net", "correo-invalido@com", "test@sitio.ai", "carlos@colombia.gov.co"]

for e in emails_a_probar:
    resultado = "Válido" if validar_email(e) else "Inválido"
    print(f"{e}: {resultado}")