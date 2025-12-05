import jwt
import json
import boto3
import datetime
from datetime import UTC
from botocore.exceptions import ClientError
from config import AWS_SECRET_NAME, AWS_REGION_NAME, SECRET_JSON_KEY

def get_secret_from_aws(secret_name, region_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    print("client connected.....")
    try:
        response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(f"Error getting secret '{secret_name}' from AWS Secrets Manager: {e}")
        return None
    else:
        print(f"response: {response}")


        if 'SecretString' in response:
            return response['SecretString']
        else:
            return None

def generate_jwt_token(user_payload):
    private_key_pem = get_secret_from_aws(
        AWS_SECRET_NAME, 
        AWS_REGION_NAME
    )

    if not private_key_pem:
        return None
    else:
        print("ok private key")

    try:
        
        if 'exp' not in user_payload:
            # exp: Expiration Time, Fecha y Hora en que el token expira
            user_payload['exp'] = datetime.datetime.now(UTC) + datetime.timedelta(hours=1)
        if 'iat' not in user_payload:
            # iat: Issued At: Fecha/Hora en que fue emitido
            user_payload['iat'] = datetime.datetime.now(UTC)

        print(".........................................")

        encoded_jwt = jwt.encode(
            user_payload,
            private_key_pem,
            algorithm='RS256'
        )
        return encoded_jwt
    except Exception as e:
        print(f"Error al generar el token JWT: {e}")
        return None

if __name__ == "__main__":
    payload_data = {
        'user_id': 789,
        'url': '/codegroups/123...'
        'AuthorizationToken': 'Bearer ....'
    }
    token = generate_jwt_token(payload_data)
    print(token)