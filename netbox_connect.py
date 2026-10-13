import os
from dotenv import load_dotenv
import pynetbox
import requests
import urllib3

def nb_connect():
    # Suppress InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Disable SSL verification
    session = requests.Session()
    session.verify = False

    # Load environment variables
    load_dotenv()
    nb_url = os.environ.get("NETBOX_URL")
    nb_token = os.environ.get("NETBOX_API_TOKEN")
    if not nb_url or not nb_token:
        raise ValueError("Missing NETBOX_URL or NETBOX_API_TOKEN in environment.")
    
    nb = pynetbox.api(nb_url, token=nb_token)
    nb.http_session = session

    return nb
