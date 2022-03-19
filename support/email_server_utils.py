from imapclient import IMAPClient
import email
import os.path
import re
from config_parser import get_config_data
from datetime import datetime


def connect_server():
    email_server_connection = get_config_data()
    try:
        server = IMAPClient(email_server_connection["SERVER"])
        server2 = IMAPClient(email_server_connection["SERVER"])

        server.login(email_server_connection["EMAIL"], email_server_connection["PASSWORD"])
        server2.login(email_server_connection["EMAIL"], email_server_connection["PASSWORD"])
        return server
    except ConnectionError as e:
        raise f'Could not connect to specified email server: {e}'


def get_message():

    server = connect_server()
    # get next message id and listen on Inbox
    next_id = server.folder_status('Inbox', 'UIDNEXT')[b'UIDNEXT']
    server.select_folder('Inbox')

    # Start IDLE mode
    server.idle()
    print("Connection is now in IDLE mode, send yourself an email or quit with ^c")
    while True:
        try:

            # Wait for up to 30 seconds for an IDLE response
            trigger = server.idle_check(timeout=30)
            if trigger:
                server.idle_done()

                response = server.fetch(next_id, [b'RFC822'])
                raw_email_string = response[next_id][b'RFC822'].decode('utf-8')
                email_message = email.message_from_string(raw_email_string)
                _parse_message(email_message)
                server.idle()

        except KeyboardInterrupt:
            break

        finally:
            server.idle_done()
            server.logout()


def _parse_message(message, key_word="banana".lower()):
    pattern = rf'\b{key_word}\b'
    for part in message.walk():
        email_body = ""
        file_name = part.get_filename()
        if message.get_content_maintype() == 'multipart':
            for p in message.get_payload():
                if p.get_content_maintype() == 'text':
                    email_body = p.get_payload()
                    break
        else:
            email_body = part.get_payload()

        if re.search(pattern, email_body):
            if file_name:
                if file_name.lower().endswith('.py'):
                    download_dir = '../downloaded_files/'
                    save_to_file = f'{file_name}.{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}'
                    file_path = os.path.join(download_dir, save_to_file)
                    if not os.path.isdir(download_dir):
                        os.mkdir(download_dir)
                    with open(file_path, 'wb') as f:
                        f.write(part.get_payload(decode=True))

get_message()