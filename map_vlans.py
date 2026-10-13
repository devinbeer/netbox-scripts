import pynetbox
from netbox_connect import nb_connect
import pandas as pd


def read_csv(file):
    df = pd.read_csv(file, header=6)
    return df


def map_vlans():
    print('Getting VLANs...')
    file = '*IP Subnets and VLANS(Sheet1).csv'
    vlan_list = read_csv(file)[['Network','VLAN', 'Description']]

    vlans_filtered = vlan_list[vlan_list['VLAN'].notna()]
    vlans_filtered = vlans_filtered[vlans_filtered['Description'].notna()]
    vlans_filtered['VLAN'] = vlans_filtered['VLAN'].astype(int)

    # Convert the dataframe into a nested list
    vlans_list = vlans_filtered.values.tolist()

    print('Mapping VLANs...')
    print(vlans_list)
    for item in vlans_list:
        subnet = item[0].replace(" ", "")
        vlan_id = item[1]
        name = item[2]

        vlan_obj = nb.ipam.vlans.get(vid=vlan_id)
        if vlan_obj is None:
            print(f"No VLAN with VID {vlan_id} found; skipping {subnet}")
            continue
        try:
             result = nb.ipam.prefixes.create(prefix=subnet, status='active', vlan=vlan_obj.id, description=name, is_pool=True)
             print(result)
        except pynetbox.RequestError as e:
            print(f"Status Code: {e.req.status_code}")
            print(f"Error Message: {e.error}")

nb = nb_connect()
map_vlans()
