from imapclient import IMAPClient
import email
import os.path
import sys
import re
import subprocess
import smtplib, ssl
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from config_parser import get_config_data
from datetime import datetime
from collections import namedtuple

logging.basicConfig(filename="logfile.log", level=logging.INFO)


def connect_server():
    """
        Connect to email sever in ordr to listen
    :return:
        server connection
    """
    email_server_connection = get_config_data()

    try:
        server = IMAPClient(email_server_connection.server_config["SERVER"])
        server.login(email_server_connection.server_config["EMAIL"], email_server_connection.server_config["PASSWORD"])
        logging.info("Connected to email server")

        return server
    except ConnectionError as e:
        logging.fatal(f'Could not connect to specified email server: {e}')
        raise f'Could not connect to specified email server: {e}'


def handle_message():
    """
        main method - receives message, handles it and then sends response
    :return:
    """

    server = connect_server()

    server.select_folder('Inbox')

    print("Connection is now in IDLE mode, send yourself an email or quit with ^c")
    while True:
        try:
            # get next message id and listen on Inbox
            next_id = server.folder_status('Inbox', 'UIDNEXT')[b'UIDNEXT']
            # in idle mode notification on a change in the folder that we listen to
            server.idle()
            logging.debug("Server in idle")
            # Wait for up to 30 seconds for an IDLE response
            trigger = server.idle_check(timeout=30)
            if trigger:
                # need to exit idle in order to fetch email
                server.idle_done()
                logging.debug("Server out of idle")
                response = server.fetch(next_id, [b'RFC822'])
                raw_email_string = response[next_id][b'RFC822'].decode('utf-8')
                email_message = email.message_from_string(raw_email_string)
                parsed_data = parse_message(email_message)
                if parsed_data.domain == get_config_data().domain_config["From"]:
                    if parsed_data.is_key_word:
                        if parsed_data.file_name:
                            # we are not checking that this is a python file (.py) just running it
                            result = download_and_run(parsed_data.file_name, parsed_data.file_part)
                            if result.stdout:
                                send_response(parsed_data.return_address, message='success', file=parsed_data.file_name,
                                              result=result.stdout)
                            elif result.stderr:
                                send_response(parsed_data.return_address, message='error', file=parsed_data.file_name,
                                              result=result.stderr)
                        else:
                            send_response(parsed_data.return_address, message='Attachment missing')
                    else:
                        send_response(parsed_data.return_address, message='Invalid keyword')

        except KeyboardInterrupt:
            break


def parse_message(message, key_word="banana".lower()):
    """
        Parses message for data
    :param message: message
    :param key_word: keyword
    :return: namedtuple "domain is_key_word file_name return_address file_part"
    """
    key_pattern = rf'\b{key_word}\b'
    email_body = ""
    message_file_part = ""
    is_key_word = False
    file_name = message.get_filename()
    return_address = email.utils.parseaddr(message['From'])[1]
    domain = return_address[return_address.index('@') + 1:]

    if message.get_content_maintype() == 'multipart':
        # search for file name
        for part in message.walk():

            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            file_name = part.get_filename()
            message_file_part = part
        # search for email body
        for m in message.get_payload():
            if m.get_default_type() == 'text/plain':
                email_body = m.get_payload()
                break
    else:
        email_body = message.get_payload()

    if re.search(key_pattern, email_body):
        is_key_word = True

    Parsed = namedtuple("Parsed", "domain is_key_word file_name return_address file_part")
    return Parsed(domain, is_key_word, file_name, return_address, message_file_part)


def download_and_run(file_name, message_file_part):
    """
        Download attached file

    :param file_name: file name
    :param message_file_part: a part of email object with relevant section
    :return: The output of ran file
    """
    download_dir = '../downloaded_files/'
    save_to_file = f'{file_name}.{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}'
    file_path = os.path.join(download_dir, save_to_file)
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
    with open(file_path, 'wb') as f:
        f.write(message_file_part.get_payload(decode=True))

    try:
        output = subprocess.run(["python", file_path], capture_output=True)
        return output
    except Exception as e:
        raise f'File run ended with error: {e}'


def send_response(address, message=None, file=None, result=None):
    """
        Sends response to the sender
    :param address: senders address
    :param message: Relevant message
    :param file: Received file name
    :param result: Result of file run
    :return:
    """
    # TODO - refactor the method

    sender_data = get_config_data()
    if message == 'success':
        return_message = f"File {file} that you sent has successfully run. To see the result please open attached file."
    elif message == 'error':
        return_message = f"File {file} that you sent has run with an error. To see the result please open attached file."
    else:
        return_message = f'Your message had {message} '

    smtp_server = 'smtp.gmail.com'

    sender = sender_data.server_config["EMAIL"]
    password = sender_data.server_config["PASSWORD"]

    message = MIMEMultipart('mixed')
    message['From'] = 'Contact <{sender}>'.format(sender = sender)
    message['To'] = address
    message['Subject'] = 'You message'
    msg_content = f'<h4>Hi There,<br>{return_message}</h4>\n'
    body = MIMEText(msg_content, 'html')
    message.attach(body)

    # Save result as file and send it as attachment = result cannot be converted to proper string without data loss

    if file:
        try:
            sent_dir = '../sent_files/'
            save_to_file = f'{file}_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.txt'
            file_path = os.path.join(sent_dir, save_to_file)
            if not os.path.isdir(sent_dir):
                os.mkdir(sent_dir)
            with open(file_path, 'wb') as f:
                f.write(result)

            with open(file_path, "rb") as attachment:
                p = MIMEApplication(attachment.read(), _subtype="txt")
                p.add_header('Content-Disposition', "attachment; filename= %s" % file_path.split("\\")[-1])
                message.attach(p)
        except Exception as e:
            logging.error(str(e))

    msg_full = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, address, msg_full)
        server.quit()

    print("email sent out successfully")


if __name__ == '__main__':
    sys.exit(handle_message())
