# -*- coding: utf-8 -*-

import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import pdb
import csv
import sys
print sys.getdefaultencoding()


SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir,
                                   'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    if attachmentFile:
        message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    else:
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"
    return "OK"

def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string())}

def createMessageWithAttachment(
    sender, to, subject, msgHtml, msgPlain, attachmentFile):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msgHtml: Html message to be sent
      msgPlain: Alternative plain text message for older email clients
      attachmentFile: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    messageA = MIMEMultipart('alternative')
    messageR = MIMEMultipart('related')

    messageR.attach(MIMEText(msgHtml, 'html'))
    messageA.attach(MIMEText(msgPlain, 'plain'))
    messageA.attach(messageR)

    message.attach(messageA)

    print("create_message_with_attachment: file: %s" % attachmentFile)
    content_type, encoding = mimetypes.guess_type(attachmentFile)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(attachmentFile, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(attachmentFile, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(attachmentFile, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(attachmentFile, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def send_email(destination_email, message_template_html, message_template_plain):
    to = destination_email
    sender = '''\"Anis Tariq\"'''
    subject = "Looking for Engineering Internship"
    msgHtml = message_template_html
    msgPlain = message_template_plain

    SendMessage(sender, to, subject, msgHtml, msgPlain, 'anis_resume.pdf')

def parse_data(name_recruiter, destination_email, company_name):
    message_template_html = """
    <p>Hi {0},</p>
    <div>&nbsp;</div>
    <div>My name is Jeff and I'm a Computer Science student at McMaster University. I found your email on Linkedin, I hope you don't mind this cold introduction.</div>
    <div>&nbsp;</div>
    <div>I'm very interested in a software engineering internship at {1}. I've heard great things about the culture at {1} and I would see an internship as an opportunity to both learn from experts and make an impact on the product.&nbsp;</div>
    <div>&nbsp;</div>
    <div>&nbsp;</div>
    <div>I previously interned at Zume Inc in their software engineering team where I made routes between our pickup-service and the hardware systems and crafted an integration test plan while heavily using Redis and RabbitMQ along with typescript/javascript.
    </div>
    <div>&nbsp;</div>
    <div>I also have extensive experience with Python and Rails development in a production environment.</div>
    <div>&nbsp;</div>
    <div>I'm looking for a summer 2020 internship - attached is my resume. If there's a potential fit, please do let me know. Happy to chat.</div>
    <div>&nbsp;</div>
    <div>Thanks,</div>
    <p>Anis</p>
    """.format(name_recruiter, company_name)

    message_template_plain = """
    Hi {0},


    My name is Jeff and I'm a Computer Science student at McMaster University. I found your email on Linkedin, I hope you don't mind this cold introduction.

    I'm very interested in a software engineering internship at {1}. I've heard great things about the culture at {1} and I would see an internship as an opportunity to both learn from experts and make an impact on the product. 

    I previously interned at Zume, Inc in Mountain View, CA on their software engineering team where I made routes between our pickup-service and the hardware systems and crafted an integration test plan while heavily using Redis and RabbitMQ along with typescript/javascript.

    I also have extensive experience with Python and Rails development in a production environment.

    I'm looking for a summer 2020 internship - attached is my resume. If there's a potential fit, please do let me know. Happy to chat.

    Thanks,
    Anis
    """.format(name_recruiter, company_name)

    send_email(destination_email, message_template_html, message_template_plain)

def main():

    with open("recruiter_raw_data.csv", "rb") as f:
        reader = csv.reader(f)
        firstLine = True

        for row in reader:
            if firstLine:    #skip first line
                firstLine = False
                continue

            name_recruiter, destination_email, company_name = row
            parse_data(name_recruiter, destination_email, company_name)


if __name__ == '__main__':
    main()
