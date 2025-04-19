import socket
import netifaces

def get_ip_and_netmask():
    hostname = socket.gethostname()

    interfaces = netifaces.interfaces()

    for interface in interfaces:
        if interface == 'lo':
            continue

        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr_info in addrs[netifaces.AF_INET]:
                ip = addr_info.get('addr')
                netmask = addr_info.get('netmask')
                if ip and netmask:
                    print(f"Интерфейс: {interface}")
                    print(f"IP-адрес: {ip}")
                    print(f"Маска сети: {netmask}")
                    print()


if __name__ == "__main__":
    print("IP-адрес и маска сети:")
    get_ip_and_netmask()