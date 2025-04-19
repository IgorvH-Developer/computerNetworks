import socket
import argparse


def check_ports(ip, start_port, end_port):
    available_ports = []

    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            try:
                s.bind((ip, port))
                available_ports.append(port)
            except (socket.error, socket.timeout):
                pass

    return available_ports


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('ip')
    parser.add_argument('start_port', type=int)
    parser.add_argument('end_port', type=int)

    args = parser.parse_args()

    print(f"Проверка портов с {args.start_port} по {args.end_port} на IP {args.ip}...")
    available_ports = check_ports(args.ip, args.start_port, args.end_port)

    if available_ports:
        print("Доступные порты:")
        for port in available_ports:
            print(port)
    else:
        print("Нет доступных портов в указанном диапазоне.")