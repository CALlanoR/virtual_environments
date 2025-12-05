1. Generar cadena aleatoria larga
```
import os
import secrets
key_long = secrets.token_urlsafe(64)
```

2. Usar claves asimetricas (RSA o ECC)
Clave privada: Se usa para firmar el JWT. Debe mantenerse en secreto absoluto en el servidor que emite los tokens.
Clave pública: Se usa para verificar la firma del JWT. Puede ser compartida públicamente (por ejemplo, a través de un endpoint JWKS).

Generación de Claves RSA (Ejemplo con OpenSSL):
Generar clave privada RSA (por ejemplo, de 2048 bits): openssl genrsa -out private_key.pem 2048
Extraer la clave pública de la clave privada: openssl rsa -pubout -in private_key.pem -out public_key.pem

Guardar la clave en AWS Secrets.

Rotar la clave cada mes.

pip install PyJWT cryptography


# Define the secret name for the private key and your AWS region
PRIVATE_KEY_SECRET_NAME="your-app/jwt/private-key"
AWS_REGION_NAME="us-east-1" 

echo "Storing private key in secret '$PRIVATE_KEY_SECRET_NAME' in region '$AWS_REGION_NAME'..."

aws secretsmanager create-secret \
    --name "healthnexus/jwt/internal-api/private-key/dev" \
    --description "RSA Private Key for JWT signing" \
    --secret-string file://./private_key.pem \
    --region us-east-1

aws secretsmanager create-secret \
    --name "healthnexus/jwt/internal-api/public-key/dev" \
    --description "RSA Public Key for JWT verification" \
    --secret-string file://./public_key.pem \
    --region us-east-1