import subprocess
import sys
import importlib

OUTPUT_FILE = "hexvpn-ovpn.conf"
API_CERT_URL = "https://api.black.riseup.net/3/cert"
API_GATEWAYS_URL = "https://api.black.riseup.net/3/config/eip-service.json"
VERBOSE = True

def verbose_log(message):
    if VERBOSE:
        print(f"> {message}")

def install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
    except subprocess.CalledProcessError as e:
        verbose_log(f"Failed to install package {package_name}: {e}")
        verbose_log("Attempting to install with --break-system flag...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name, "--break-system"])
        except subprocess.CalledProcessError as e:
            verbose_log(f"Failed to install package {package_name} with --break-system flag: {e}")
            sys.exit(1)

def check_and_install_requirements():
    try:
        importlib.import_module('requests')
    except ImportError:
        verbose_log("requests module not found. Installing...")
        install_package('requests')

    if subprocess.run(["ping", "-c", "1", "127.0.0.1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
        verbose_log("ping utility not found. Please install ping.")
        sys.exit(1)

def fetch_data(url):
    import requests
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.text if 'cert' in url else response.json()

def write_to_file(file_path, content, mode='w'):
    with open(file_path, mode) as file:
        file.write(content)

def append_key_cert(output_file, key_cert):
    with open(output_file, 'a') as file:
        file.write(f"\n<key>\n{key_cert}\n</key>\n<cert>\n{key_cert}\n</cert>")

def get_latency(ip_address):
    try:
        result = subprocess.run(["ping", "-c", "1", ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            time_ms = result.stdout.split('\n')[1].split('time=')[-1].split(' ')[0]
            return float(time_ms)
    except Exception as e:
        verbose_log(f"Error pinging {ip_address}: {e}")
    return float('inf')

def find_fastest_gateway(gateways):
    fastest_gateway = None
    fastest_latency = float('inf')
    for gateway in gateways:
        ip_address = gateway['ip_address']
        latency = get_latency(ip_address)
        verbose_log(f"Latency to {gateway['host']} ({ip_address}): {latency} ms")
        if latency < fastest_latency:
            fastest_latency = latency
            fastest_gateway = gateway
    return fastest_gateway, fastest_latency

def update_conf_with_gateway(output_file, gateway, latency):
    ip_address = gateway['ip_address']
    port = next(port['ports'][0] for port in gateway['capabilities']['transport'] if 'openvpn' in port['type'])
    with open(output_file, 'r') as file:
        lines = file.readlines()
    with open(output_file, 'w') as file:
        for line in lines:
            if "remote-random" in line:
                file.write(f"remote {ip_address} {port} # {gateway['host']} ({gateway['location']})\n")
            file.write(line)
    verbose_log(f"Fastest gateway: {gateway['host']} ({ip_address}) with latency {latency} ms")
    print(f"\033[92mHexVPN setup completed successfully. You can now run: sudo openvpn --config {output_file}\033[0m")

def main():
    verbose_log("Starting HexVPN setup...")

    check_and_install_requirements()

    verbose_log(f"Fetching VPN client certs from: {API_CERT_URL}")
    key_cert = fetch_data(API_CERT_URL)

    verbose_log(f"Creating/Open output file: {OUTPUT_FILE}")
    write_to_file(OUTPUT_FILE, open(".hexvpn-base.conf", 'r').read())

    verbose_log(f"Appending key_cert to {OUTPUT_FILE}")
    append_key_cert(OUTPUT_FILE, key_cert)

    verbose_log(f"Fetching VPN gateways from: {API_GATEWAYS_URL}")
    gateways = fetch_data(API_GATEWAYS_URL)['gateways']

    verbose_log("Measuring latency to VPN gateways")
    fastest_gateway, fastest_latency = find_fastest_gateway(gateways)

    if fastest_gateway:
        update_conf_with_gateway(OUTPUT_FILE, fastest_gateway, fastest_latency)
    else:
        print("\033[91mNo valid gateways found.\033[0m")

if __name__ == "__main__":
    main()
