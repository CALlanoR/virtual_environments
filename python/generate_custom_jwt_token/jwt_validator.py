import jwt
import boto3
from botocore.exceptions import ClientError

AWS_SECRET_NAME = 'healthnexus/jwt/internal-api/public-key/dev'
AWS_REGION_NAME = 'us-east-1'

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
        if 'SecretString' in response:
            return response['SecretString']
        else:
            return None

def verify_jwt_token(token):
    public_key_pem = get_secret_from_aws(
        AWS_SECRET_NAME,
        AWS_REGION_NAME
    )

    if not public_key_pem:
        return None

    try:
        decoded_payload = jwt.decode(
            token,
            public_key_pem,
            algorithms=['RS256']
        )
        print(decoded_payload)
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("\nError: The token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        print(f"\nError: Invalid Token: {e}")
        return None
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return None

if __name__ == "__main__":
    example_token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3ODksInVybCI6Ii9jb2RlZ3JvdXBzLzEyMy4uLiIsImV4cCI6MTc0ODI4OTU4NCwiaWF0IjoxNzQ4Mjg1OTg0fQ.1DXPkxOR_UgBzDQwSxrAx8EK3PKO4-NXigUJnoFzNpE4WafgoRfiMCfo5MjuNSvAKLaHrIdrvd2iH9iktn8R_GLqwYaaN5OGwnmmqudXRq_R8QQUX_OzHOudRjjud1OumKeSfpWUebg7sNYTsyUyT1who5IFiuHftdEQVjnrOY9iw0E6OHpdiutFenYFdzJPuChFCp6pWhWcn3Vkss_3763HZTL11LCDpwvT5wjY3AcwZSjhwSOPyA5lJzIL76sbiCIhcSzGeeO1kSacyttNZLPSKiBFmuV_x7k74wYggi5etsmNeK-WOAdL48ZIG_YSmchM8CfTvkwiYnewOmBf2A"

    verified_data = verify_jwt_token(example_token)

    if verified_data:
        print("ok")
    else:
        print("error")