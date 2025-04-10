import socket
import random
import time
import struct
from checksum import calculate_checksum, verify_checksum


class RDTPacket:
    def __init__(self, seq_num: int, data: bytes):
        self.seq_num = seq_num
        self.data = data
        self.checksum = calculate_checksum(self._serialize_without_checksum())

    def _serialize_without_checksum(self) -> bytes:
        return struct.pack('!H', self.seq_num) + self.data

    def serialize(self) -> bytes:
        return self._serialize_without_checksum() + struct.pack('!H', self.checksum)

    @classmethod
    def deserialize(cls, packet_bytes: bytes):
        if len(packet_bytes) < 4:  # seq_num (2) + checksum (2)
            return None

        # print("получил пакет с байтами", packet_bytes[:2], packet_bytes[-2:])
        seq_num = struct.unpack('!H', packet_bytes[:2])[0]
        # print(seq_num)
        data = packet_bytes[2:-2]
        checksum = struct.unpack('!H', packet_bytes[-2:])[0]

        # Проверка контрольной суммы
        calculated_checksum = calculate_checksum(packet_bytes[:-2])
        # print('наша checksum', calculated_checksum)
        if calculated_checksum != checksum:
            return None

        packet = cls(seq_num, data)
        # print('packetttt ', packet.seq_num)
        return packet


class ACKPacket:
    def __init__(self, seq_num: int):
        self.seq_num = seq_num
        self.checksum = calculate_checksum(self._serialize_without_checksum())

    def _serialize_without_checksum(self) -> bytes:
        return struct.pack('!H', self.seq_num)

    def serialize(self) -> bytes:
        return self._serialize_without_checksum() + struct.pack('!H', self.checksum)

    @classmethod
    def deserialize(cls, packet_bytes: bytes):
        if len(packet_bytes) != 4:  # seq_num (2) + checksum (2)
            return None

        seq_num = struct.unpack('!H', packet_bytes[:2])[0]
        # print(seq_num)
        checksum = struct.unpack('!H', packet_bytes[2:])[0]

        # Проверка контрольной суммы
        calculated_checksum = calculate_checksum(packet_bytes[:2])
        if calculated_checksum != checksum:
            return None

        packet = cls(seq_num)
        # print('packetttt ', packet.seq_num)
        return packet


class StopWaitProtocol:
    def __init__(self, sock: socket.socket, loss_probability=0.3, timeout=2.0):
        self.sock = sock
        self.loss_probability = loss_probability
        self.timeout = timeout
        self.seq_num = 0

    def _should_drop_packet(self) -> bool:
        return random.random() < self.loss_probability

    def send_packet(self, data: bytes, addr: tuple) -> bool:
        packet = RDTPacket(self.seq_num, data).serialize()

        while True:
            if not self._should_drop_packet():
                self.sock.sendto(packet, addr)
                # print("отправили пакет с байтами", packet[:2], packet[-2:])

            start_time = time.time()
            while time.time() - start_time < self.timeout:
                try:
                    self.sock.settimeout(self.timeout - (time.time() - start_time))
                    ack_data, _ = self.sock.recvfrom(1024)
                    ack = ACKPacket.deserialize(ack_data)

                    # print(f"получили пакет. его номер {ack.seq_num}, наш {self.seq_num}")

                    if ack is not None and ack.seq_num == self.seq_num:
                        self.seq_num = 1 - self.seq_num  # Переключение между 0 и 1
                        return True
                except socket.timeout:
                    break

            # Таймаут или некорректный ACK - повторная отправка
            if not self._should_drop_packet():
                self.sock.sendto(packet, addr)

    def recv_packet(self) -> tuple:
        while True:
            try:
                packet_data, addr = self.sock.recvfrom(1024)
                packet = RDTPacket.deserialize(packet_data)
                if packet is None:
                    continue

                # print(f"получили пакет. его номер {packet.seq_num}, наш {self.seq_num}")
                ack = ACKPacket(packet.seq_num).serialize()
                if not self._should_drop_packet():
                    self.sock.sendto(ack, addr)

                if packet.seq_num == self.seq_num:
                    self.seq_num = 1 - self.seq_num
                    return packet.data, addr
            except socket.error:
                continue