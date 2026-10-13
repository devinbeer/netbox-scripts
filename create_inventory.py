import pynetbox
from netbox_connect import nb_connect
import pandas as pd
import re


def read_csv(file):
    df = pd.read_csv(file, header=6)
    return df


def get_models():
    models = ''
    return models


def get_devices():
    devices = ''
    return devices


def create_device_type(nb, models):
    print('Creating device types...')

    models_unique = models.unique()

    manufacturer_id = nb.dcim.manufacturers.get(name='Cisco').id
    for item in models_unique:
        try:
            result = nb.dcim.device_types.create(manufacturer=manufacturer_id, model=item, slug=item.replace(' ', '-'))
            print(result)
        except pynetbox.RequestError as e:
            print(f"Status Code: {e.req.status_code}")
            print(f"Error Message: {e.error}")
    print('Objects created.')


def create_device():
    print('Creating devices...')
    device_role = nb.dcim.device_roles.get(name='Access Switches').id
    device_dict = [list(item) for item in zip(device_list, models_list)]

    for item in device_dict:
        try:
            type_id = nb.dcim.device_types.get(model=item[1]).id
            result = nb.dcim.devices.create(name=item[0], role=device_role, device_type=type_id, site=1)
            print(result)
        except pynetbox.RequestError as e:
                    print(f"Status Code: {e.req.status_code}")
                    print(f"Error Message: {e.error}")


def update_devices():
    print('Updating devices...')
    devices = nb.dcim.devices.filter(q='swv')
    for device in devices:
        regex_match = re.match(r'^(\S+)\s*\[(\d+)\]$', device.name)

        if regex_match:
            chassis_name = regex_match.group(1).upper()
            stack_position = regex_match.group(2)
            chassis = nb.dcim.virtual_chassis.get(name=chassis_name)

            # Update device
            device.virtual_chassis = chassis.id
            device.vc_position = stack_position
            device.save()

            print(f'Successfully updated {device}')

        else:
             print(f'No match for {device.name}')
             continue

    print('Update finished.')


def create_vlans():
    print('Getting VLANs...')
    file = '*IP Subnets and VLANS(Sheet1).csv'
    vlan_list = read_csv(file)[['VLAN', 'Description']]

    vlans_filtered = vlan_list[vlan_list['VLAN'].notna()]
    vlans_filtered = vlans_filtered[vlans_filtered['Description'].notna()]
    vlans_filtered['VLAN'] = vlans_filtered['VLAN'].astype(int)

    # Convert the dataframe into a nested list
    vlans_list = vlans_filtered.values.tolist()

    print('Creating VLANs...')
    for item in vlans_list:
        vlan_id = item[0]
        description = item[1]
        try:
             result = nb.ipam.vlans.create(vid=vlan_id, name=description)
             print(result)
        except pynetbox.RequestError as e:
            print(f"Status Code: {e.req.status_code}")
            print(f"Error Message: {e.error}")
             

     
nb = nb_connect()
models_list = get_models()
device_list = get_devices()
# create_device()

create_vlans()
