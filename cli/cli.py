import os
import json
import sys
import subprocess
from urllib.parse import urlparse
import http.client

if len(sys.argv) < 2 or sys.argv[1] != '--':
    raise Exception('Please provide a command to run: secretsfly -- <command>')

SECRETSFLY_TOKEN = os.environ.get('SECRETSFLY_TOKEN')
SECRETSFLY_API_BASE_URL = os.environ.get('SECRETSFLY_API_BASE_URL', 'http://localhost:5000/api')

del os.environ['SECRETSFLY_TOKEN']

if 'SECRETSFLY_API_BASE_URL' in os.environ:
    del os.environ['SECRETSFLY_API_BASE_URL']

if not SECRETSFLY_TOKEN:
    raise Exception('SECRETSFLY_TOKEN is not set')

if not SECRETSFLY_API_BASE_URL:
    raise Exception('SECRETSFLY_API_BASE_URL is not set')

parsed_api_url = urlparse(SECRETSFLY_API_BASE_URL)

if parsed_api_url.scheme == 'http':
    conn = http.client.HTTPConnection(parsed_api_url.netloc)
elif parsed_api_url.scheme == 'https':
    conn = http.client.HTTPSConnection(parsed_api_url.netloc)

conn.request("GET", "/api/secrets/",
             headers={"Authorization": SECRETSFLY_TOKEN})
response = conn.getresponse()
body = response.read().decode('utf-8')

if response.status != 200:
    raise Exception(f"Issue retrieving secrets, status={response.status}, body={body}")

parsed_json_body = json.loads(body)

for secret in parsed_json_body['secrets']:
    os.environ[secret['name']] = secret['value']

command_to_run = " ".join(sys.argv[2:])

subprocess.call(command_to_run, shell=True)
