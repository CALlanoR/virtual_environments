import boto3
import hashlib
import hmac
import base64


def calculate_secret_hash(client_id, client_secret, username):
    if client_secret is None:
        return None

    message = username.encode('utf-8') + client_id.encode('utf-8')
    key = client_secret.encode('utf-8')
    hashed = hmac.new(key, message, hashlib.sha256)
    return base64.b64encode(hashed.digest()).decode('utf-8')

def authenticate_user(user_pool_id, client_id, client_secret, username, password, region_name='us-east-1'):

    try:
        cognito_idp_client = boto3.client('cognito-idp', region_name=region_name)

        secret_hash = calculate_secret_hash(client_id, client_secret, username)
        auth_params = {
            'USERNAME': username,
            'PASSWORD': password
        }
        if secret_hash:
            auth_params['SECRET_HASH'] = secret_hash

        response = cognito_idp_client.admin_initiate_auth(
            UserPoolId=user_pool_id,
            ClientId=client_id,
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters=auth_params
        )

        return response
    except Exception as e:
        print(f"Error al autenticar el usuario: {e}")
        return None


def main():
    user_pool_id = ''
    client_id = ''
    client_secret = ''
    username = '' 
    password = ''

    auth_response = authenticate_user(user_pool_id, client_id, client_secret, username, password)

    if auth_response:
        print("Autenticación exitosa!")
        # print(auth_response)
        if 'AuthenticationResult' in auth_response:
            tokens = auth_response['AuthenticationResult']
            print(f"  Access Token: {tokens['AccessToken']}")
            print(f"  Id Token: {tokens['IdToken']}")
            print(f"  Refresh Token: {tokens['RefreshToken']}")
        else:
            print("  No se recibieron tokens en la respuesta.")

    else:
        print("La autenticación falló.  Revisa los errores en la consola.")


if __name__ == "__main__":
    main()