import socket
import struct
import time
import select
import argparse
from datetime import datetime

class AdvancedTraceroute:
    def __init__(self):
        self.udp_socket = None
        self.recv_socket = None
        self.timeout = 1.0
        self.max_hops = 30
        self.num_probes = 3
        self.port = 33434
        self.dest_ip = None
        self.dest_name = None
        self.last_hop = None
        self.resolved_names = {}

    def create_udp_packet(self, size=32):
        return b'\x00' * size

    def resolve_hostname(self, ip_addr):
        if ip_addr in self.resolved_names:
            return self.resolved_names[ip_addr]

        try:
            hostname, _, _ = socket.gethostbyaddr(ip_addr)
            self.resolved_names[ip_addr] = hostname
            return hostname
        except (socket.herror, socket.gaierror):
            self.resolved_names[ip_addr] = ip_addr
            return ip_addr

    def init_sockets(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.recv_socket.settimeout(self.timeout)

    def close_sockets(self):
        if self.udp_socket:
            self.udp_socket.close()
        if self.recv_socket:
            self.recv_socket.close()

    def send_udp_probe(self, ttl, probe_num):
        port = self.port + (ttl - 1) * self.num_probes + probe_num
        packet = self.create_udp_packet()
        self.udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        send_time = time.time()
        self.udp_socket.sendto(packet, (self.dest_ip, port))
        return send_time, port

    def receive_icmp_response(self, expected_port):
        try:
            ready = select.select([self.recv_socket], [], [], self.timeout)
            if ready[0]:
                packet, addr = self.recv_socket.recvfrom(1024)
                recv_time = time.time()

                icmp_type = packet[20]
                icmp_code = packet[21]

                # Time Exceeded
                if icmp_type == 11 and icmp_code == 0:
                    return addr[0], recv_time, 'time_exceeded'

                if icmp_type == 3 and icmp_code == 3:
                    if len(packet) >= 28:
                        orig_port = struct.unpack('!H', packet[50:52])[0]
                        if orig_port == expected_port:
                            return addr[0], recv_time, 'port_unreachable'

                return None, None, None
        except (socket.error, struct.error):
            pass

        return None, None, None

    def format_output_line(self, ttl, ip_addr, rtts):
        if ip_addr:
            hostname = self.resolve_hostname(ip_addr)
            if hostname != ip_addr:
                line = f"{ttl:2d}  {hostname} ({ip_addr})"
            else:
                line = f"{ttl:2d}  {ip_addr}"

            for rtt in rtts:
                if rtt is not None:
                    line += f"  {rtt:.3f} ms"
                else:
                    line += "  *"
        else:
            line = f"{ttl:2d}  * * *"

        return line

    def trace(self, dest_addr, max_hops=30, timeout=1.0, num_probes=3, resolve_names=True):
        self.max_hops = max_hops
        self.timeout = timeout
        self.num_probes = num_probes

        try:
            self.dest_ip = socket.gethostbyname(dest_addr)
            self.dest_name = dest_addr
        except socket.gaierror:
            print(f"Error: Could not resolve hostname {dest_addr}")
            return

        print(f"traceroute to {self.dest_name} ({self.dest_ip}), {self.max_hops} hops max, 28 byte packets")

        self.init_sockets()

        for ttl in range(1, self.max_hops + 1):
            ip_addr = None
            rtts = []
            got_response = False

            for probe_num in range(self.num_probes):
                send_time, port = self.send_udp_probe(ttl, probe_num)
                current_ip, recv_time, response_type = self.receive_icmp_response(port)

                if current_ip:
                    ip_addr = current_ip
                    rtt = (recv_time - send_time) * 1000 if recv_time else None
                    rtts.append(rtt)

                    if response_type == 'port_unreachable':
                        got_response = True
                else:
                    rtts.append(None)

            print(self.format_output_line(ttl, ip_addr, rtts))

            if got_response:
                break

            time.sleep(0.1)

        self.close_sockets()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('-m', '--max-hops', type=int, default=30)
    parser.add_argument('-t', '--timeout', type=float, default=1.0)
    parser.add_argument('-n', '--num-probes', type=int, default=3)
    parser.add_argument('--no-resolve', action='store_false', dest='resolve_names')

    args = parser.parse_args()

    tracer = AdvancedTraceroute()

    try:
        print(f"# traceroute started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        tracer.trace(args.host, args.max_hops, args.timeout,
                     args.num_probes, args.resolve_names)
    except Exception as e:
        print(f"Error: {str(e)}")