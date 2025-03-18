import socket
import ssl
import base64
import configparser
import argparse

def read_message_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Не найден файл {file_path}.")
        exit(1)

def connect_to_smtp(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    response = sock.recv(1024).decode('utf-8')
    if not response.startswith('2'):
        raise RuntimeError("SMTP Server did not respond correctly.")
    return sock

def send_command(sock, command):
    sock.sendall(command.encode() + b'\n')
    response = sock.recv(1024).decode('utf-8')
    print(f">>> Sent: {command}")
    print(f"<<< Received: {response.strip()}")
    if not response.startswith('2') and not response.startswith('354'):
        raise RuntimeError(f"Command '{command}' failed. Response: {response}")

def authenticate(sock, username, password):
    send_command(sock, f'EHLO localhost')
    auth_string = "\0{}\0{}".format(username, password)
    auth_bytes = base64.b64encode(auth_string.encode()).decode('ascii')
    send_command(sock, 'AUTH PLAIN {}'.format(auth_bytes))

def send_mail(sock, from_addr, to_addr, body):
    send_command(sock, f'MAIL FROM:<{from_addr}>')
    send_command(sock, f'RCPT TO:<{to_addr}>')
    send_command(sock, 'DATA')
    message = f'Subject: Письмо из налоговой\r\n\r\n{body}\r\n.'
    send_command(sock, message)

def disconnect(sock):
    send_command(sock, 'QUIT')
    sock.close()

def start_tls(sock, host):
    send_command(sock, 'EHLO localhost')
    sock.sendall(b'STARTTLS\n')
    response = sock.recv(1024).decode('utf-8')
    print(f">>> Sent: STARTTLS")
    print(f"<<< Received: {response.strip()}")
    if not response.startswith('220'):
        raise RuntimeError("Server is not ready for TLS.")

    context = ssl.create_default_context()
    ssock = context.wrap_socket(sock, server_hostname=host)
    return ssock

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('email_client.cfg')

    sender = config.get('Mail', 'sender')
    password = config.get('Mail', 'password')
    smtp_server = config.get('Mail', 'smtp_server')
    smtp_port = int(config.get('Mail', 'smtp_port'))

    parser = argparse.ArgumentParser()
    parser.add_argument('--to', required=True)
    parser.add_argument('--file', required=True)
    args = parser.parse_args()

    body = read_message_from_file(args.file)

    try:
        sock = connect_to_smtp(smtp_server, smtp_port)
        ssock = start_tls(sock, smtp_server)
        authenticate(ssock, sender, password)

        send_command(ssock, 'EHLO localhost')

        send_mail(ssock, sender, args.to, body)
        disconnect(ssock)

        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")