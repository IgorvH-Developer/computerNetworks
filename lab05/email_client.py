import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
import argparse

def read_message_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Не найден файл {file_path}.")
        exit(1)


def send_email(recipient, body, is_html=False):
    if is_html:
        message = MIMEMultipart('alternative')
        part_text = MIMEText(body, 'plain', 'utf-8')
        part_html = MIMEText(body, 'html', 'utf-8')
        message.attach(part_text)
        message.attach(part_html)
    else:
        message = MIMEText(body, 'plain', 'utf-8')

    message['From'] = sender
    message['To'] = recipient

    print(sender, password)
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, message.as_string())


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('email_client.cfg')

    sender = config.get('Mail', 'sender')
    password = config.get('Mail', 'password')
    smtp_server = config.get('Mail', 'smtp_server')
    smtp_port = int(config.get('Mail', 'smtp_port'))

    print(sender, password, smtp_server, smtp_port)

    parser = argparse.ArgumentParser()
    parser.add_argument('--to', help='Адрес получателя', required=True)
    parser.add_argument('--file', help='Файл с содержанием письма', required=True)
    parser.add_argument('--html', action='store_true', help='Использовать HTML формат')
    args = parser.parse_args()

    body = read_message_from_file(args.file)

    send_email(args.to, body, args.html)