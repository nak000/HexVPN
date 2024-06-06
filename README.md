# HexVPN

HexVPN is a Python script that sets up a VPN connection using Riseup's VPN service. It fetches the necessary client certificates and VPN gateway configurations, measures latency to select the fastest gateway, and updates the configuration file accordingly.

## Features

- Fetches VPN client certificates from Riseup's API
- Retrieves VPN gateway configurations
- Measures latency to select the fastest gateway
- Creates and configures the `.hexvpn-base.conf` file for use with OpenVPN

## Requirements

- Python 3.x
- `requests` library
- OpenVPN
- `ping` command available on the system

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/HexBuddy/HexVPN
    cd HexVPN
    ```

2. Install the required Python library:

    ```sh
    pip install requests
    ```

## Usage

1. Place your base configuration file named `.hexvpn-base.conf` in the same directory as `hexvpn.py`.

2. Run the script:

    ```sh
    python hexvpn.py
    ```

3. Upon successful completion, run the following command to start the VPN:

    ```sh
    sudo openvpn --config hexvpn-ovpn.conf
    ```

## Configuration Files

### .hexvpn-base.conf

Create a base configuration file named `.hexvpn-base.conf` with the following content:

```conf
client
dev tun
proto tcp
remote <IP> <PORT>
remote-random
nobind
persist-key
persist-tun
remote-cert-tls server
pull-filter ignore "tun-ipv6"
pull-filter ignore "route-ipv6"
pull-filter ignore "ifconfig-ipv6"
block-ipv6
cipher AES-256-GCM
data-ciphers AES-256-GCM
keepalive 10 30
verb 3
<ca>
-----BEGIN CERTIFICATE-----
[Your Certificate Here]
-----END CERTIFICATE-----
</ca>
<key>
-----BEGIN RSA PRIVATE KEY-----
[Your Private Key Here]
-----END RSA PRIVATE KEY-----
<cert>
-----BEGIN CERTIFICATE-----
[Your Certificate Here]
-----END CERTIFICATE-----
</cert>
