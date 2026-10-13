# netbox-scripts

A collection of Python scripts for uploading data to, and manipulating data inside, a local [NetBox](https://github.com/netbox-community/netbox) instance. The scripts use [pynetbox](https://github.com/netbox-community/pynetbox) for API access and [pandas](https://pandas.pydata.org/) to read source data from CSV and Excel files.

This repository is public but maintained primarily for personal use. More scripts will be added over time.

## Scripts

| Script | Purpose |
| --- | --- |
| `netbox_connect.py` | Shared helper. `nb_connect()` returns an authenticated pynetbox client using environment variables. |
| `create_ip_addresses.py` | Reads Excel files and creates IP addresses in NetBox with status `reserved`. |
| `create_inventory.py` | Creates VLANs, device types, and devices, and updates devices with virtual chassis membership. |
| `map_vlans.py` | Reads a CSV and creates prefixes linked to existing VLANs. |

## Requirements

- Python: `3.14.4`
- NetBox: `4.6.5`
- Python packages:
  - `pynetbox`
  - `pandas`
  - `python-dotenv`
  - `requests`
  - `urllib3`
  - `openpyxl` (needed by pandas to read `.xlsx` files)

```bash
pip install pynetbox pandas python-dotenv requests urllib3 openpyxl
```

## Configuration

`netbox_connect.py` reads two environment variables, loaded from a `.env` file in the working directory:

| Variable | Description |
| --- | --- |
| `NETBOX_URL` | Base URL of the NetBox instance |
| `NETBOX_API_TOKEN` | NetBox API token |

Example `.env`:

```
NETBOX_URL=<netbox-url>
NETBOX_API_TOKEN=<api-token>
```

If either variable is missing, `nb_connect()` raises a `ValueError`.

**Do not commit `.env` or any source data files.** Add them to `.gitignore`.

> **Note:** `netbox_connect.py` disables SSL certificate verification and suppresses the related `InsecureRequestWarning`. This is intended for a local instance with a self-signed certificate.

## Usage

Each script connects to NetBox and runs when executed directly:

```bash
python <script_name>.py
```

Scripts create objects through the API. When NetBox rejects a request (for example, a duplicate object), the script prints the HTTP status code and error message and continues to the next row.

### `create_ip_addresses.py`

- **Input:** every non-hidden file in the `./ip_addressing` directory, read with `pandas.read_excel`.
- **Format:** the header row is row 7 of the sheet (`header=6`). Required columns: `IP Address` and `Assigned to:`.
- **Behavior:** rows with an empty `Assigned to:` value are skipped. The remaining `IP Address` values are created with status `reserved`.

### `map_vlans.py`

- **Input:** `*IP Subnets and VLANS(Sheet1).csv`, read with `pandas.read_csv`.
- **Format:** the header row is row 7 of the file (`header=6`). Required columns: `Network`, `VLAN`, `Description`.
- **Behavior:** rows missing a `VLAN` or `Description` value are skipped. For each remaining row, the script looks up the existing VLAN by VID and creates a prefix with status `active`, `is_pool=True`, linked to that VLAN, with the description set from `Description`. Rows whose VID is not found in NetBox are skipped.
- **Prerequisite:** the VLANs must already exist in NetBox (see `create_vlans()` in `create_inventory.py`).

### `create_inventory.py`

| Function                         | Behavior                                                                                                                                                                                                                           |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `create_vlans()`                 | Reads `*IP Subnets and VLANS(Sheet1).csv` (header row 7; columns `VLAN`, `Description`) and creates VLANs with `vid` from `VLAN` and `name` from `Description`. Rows missing either value are skipped.                             |
| `create_device_type(nb, models)` | Creates a device type for each unique model in `models`, under the existing `Cisco` manufacturer. The slug is the model name with spaces replaced by hyphens.                                                                      |
| `create_device()`                | Creates devices from `device_list` and `models_list` with the existing `Access Switches` device role, the matching device type, and `site=1`.                                                                                      |
| `update_devices()`               | Finds devices matching the search term `swv` whose names match the pattern `<name> [<number>]`. Sets each device's virtual chassis to the existing chassis named with the uppercased `<name>` and its `vc_position` to `<number>`. |

## License

This project is licensed under the MIT License -- see the [LICENSE](LICENSE) file for details.
