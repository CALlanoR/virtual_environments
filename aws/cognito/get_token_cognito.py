import base64
import requests

oauth_base_url = "https://xyz.amazoncognito.com/oauth2/token?grant_type=client_credentials"
client_id = ""
client_secret = ""

# Base64 encode auth info and add to headers
auth_b64 = base64.b64encode(f"{client_id}:{client_secret}".encode())
oauth_headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {auth_b64.decode('utf-8')}",
}

# Post returns JSON with "access_token" as the Bearer token.
resp = requests.post(oauth_base_url,
                     headers=oauth_headers)   #, data=oauth_payload_txt)
print(resp.json())