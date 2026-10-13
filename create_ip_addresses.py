import pynetbox
import pandas as pd
from netbox_connect import nb_connect
from pathlib import Path


def read_excel(file, usecols=None):
    df = pd.read_excel(file, header=6, usecols=usecols)
    return df


def create_ip_addresses():
    file_path = Path("./ip_addressing")

    for file in file_path.iterdir():
        if file.name.startswith('.'):
            continue
        print("File name: ", file)
        ip_list = read_excel(file, usecols=['IP Address', 'Assigned to:'])
        ip_list_filtered = ip_list[ip_list['Assigned to:'].notna()]

        print('Creating IP addresses...')
        print(ip_list_filtered)
        for item in ip_list_filtered['IP Address']:
            try:
                result = nb.ipam.ip_addresses.create(address=item, status='reserved')
                print(result)
            except pynetbox.RequestError as e:
                print(f"Status Code: {e.req.status_code}")
                print(f"Error Message: {e.error}")


nb = nb_connect()
create_ip_addresses()
