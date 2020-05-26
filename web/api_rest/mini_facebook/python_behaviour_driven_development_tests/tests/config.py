from pathlib import Path

environment = "dev"

api_domains = {
   "dev": "localhost:8383",
   "stage": "localhost:8383",
   "prod": "localhost:8383"
}

endpoint_url_http = api_domains[environment]
