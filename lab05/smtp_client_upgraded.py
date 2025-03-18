import os
import socket
import ssl
import base64
import configparser
import argparse
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def read_image_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Не найден файл {file_path}.")
        exit(1)

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

def send_mail(sock, from_addr, to_addr, text_body=None, image_filename=None):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr

    if text_body:
        part_text = MIMEText(text_body, 'plain')
        msg.attach(part_text)

    if image_filename:
        img_data = read_image_file(image_filename)
        img_mime = MIMEImage(img_data, name=os.path.basename(image_filename))
        img_mime.add_header('Content-ID', '<image>')
        msg.attach(img_mime)

    send_command(sock, 'MAIL FROM:<{}>'.format(from_addr))
    send_command(sock, 'RCPT TO:<{}>'.format(to_addr))
    send_command(sock, 'DATA')

    full_msg = msg.as_string().replace('\n.', '.') + "."
    send_command(sock, full_msg)

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
    parser.add_argument('--body', required=True)
    parser.add_argument('--image-file')
    args = parser.parse_args()

    body = read_message_from_file(args.body)

    try:
        sock = connect_to_smtp(smtp_server, smtp_port)
        ssock = start_tls(sock, smtp_server)
        authenticate(ssock, sender, password)

        send_command(ssock, 'EHLO localhost')

        # Отправка письма
        send_mail(
            ssock,
            sender,
            args.to,
            text_body=body,
            image_filename=args.image_file
        )

        disconnect(ssock)

        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")