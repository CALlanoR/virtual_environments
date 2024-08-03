import os
import json
import requests
import google.oauth2.id_token
import google.auth.transport.requests

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './gcp-key.json'
request = google.auth.transport.requests.Request()
audience = 'https://datacore-patient-groups-operations-3wgxqirajq-uc.a.run.app'
TOKEN = google.oauth2.id_token.fetch_id_token(request,
                                              audience)

r = requests.post(
    audience, 
    headers={
        'Authorization': f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    },
    data=json.dumps({"key": "value"})
)
r.status_code, r.reason