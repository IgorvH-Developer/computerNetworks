def calculate_checksum(data: bytes) -> int:
    """
    Вычисляет 16-битную контрольную сумму для данных по алгоритму, используемому в TCP/IP.
    """
    if len(data) % 2 != 0:
        data += b'\x00'  # Дополнение до четного количества байт

    total = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        total += word
        total = (total & 0xffff) + (total >> 16)  # Перенос битов

    return ~total & 0xffff


def verify_checksum(data: bytes, checksum: int) -> bool:
    """
    Проверяет, соответствует ли контрольная сумма данным.
    """
    if len(data) % 2 != 0:
        data += b'\x00'

    total = checksum
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i + 1]
        total += word
        total = (total & 0xffff) + (total >> 16)

    return total == 0xffff


# Тесты для контрольных сумм
if __name__ == "__main__":
    # Тест 1: Корректные данные
    test_data1 = b'Hello, world!'
    checksum1 = calculate_checksum(test_data1)
    print(f"Test 1 - Checksum matches: {verify_checksum(test_data1, checksum1)} (should be True)")

    # Тест 2: Ошибка в данных
    corrupted_data = b'Hellp, world!'
    print(f"Test 2 - Checksum matches: {verify_checksum(corrupted_data, checksum1)} (should be False)")

    # Тест 3: Пустые данные
    empty_data = b''
    checksum_empty = calculate_checksum(empty_data)
    print(f"Test 3 - Empty data checksum: {verify_checksum(empty_data, checksum_empty)} (should be True)")