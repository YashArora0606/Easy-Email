# -*- coding: utf-8 -*-

import httplib2
import os
import oauth2client
from oauth2client import client, tools, file
import base64
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
import pdb
import csv
import sys


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
        with open(attachmentFile) as fp:
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=sub_type)
    elif main_type == 'image':
        with open(attachmentFile, 'rb') as fp:
            msg = MIMEImage(fp.read(), _subtype=sub_type)
    elif main_type == 'audio':
        with open(attachmentFile, 'rb') as fp:
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
    else:
        with open(attachmentFile, 'rb') as fp:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
        # Encode the payload using Base64
        encoders.encode_base64(msg)
    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_email(destination_email, message_template_html, message_template_plain, company_name):
    to = destination_email
    sender = '''\"Yash Arora\"'''
    subject = "2021 Software Engineering Internship at " + company_name
    msgHtml = message_template_html
    msgPlain = message_template_plain

    SendMessage(sender, to, subject, msgHtml, msgPlain, "YashArora_Resume.pdf")

def parse_data(name_recruiter, destination_email, company_name):
    message_template_html = """
    <p>Hi {0}!</p>
    <div>I'm Yash, a Software Engineering student from the University of Waterloo. I found myself extremely interested in a software internship at {1}, and I wanted to reach out to you personally!</div>
    <div>&nbsp;</div>
    <div>
    Recently I interned at Localintel, a Seattle startup, where I led the development of their client management portal in addition to improving the efficiency and functionality of their platforms.
    Now, I'd love to bring my skills to your table.
    In terms of experience, I've worked extensively with Python, C++, Java, and Javascript (Frameworks), and am familiar with a variety of other languages and tools. 
    As a software enthusiast I'm always working on something new, with my most recent endeavor being the creation of an online collaborative code editor/whiteboard 
    (that you can try for yourself) called <a href="https://itsohana.com">Ohana</a>. 
    If you'd like more detail about the work I've done, feel free to check out my resume; it's attached in this email!
    I'd just like to add that I am a citizen in both the US and Canada, so I don't require any sponsorship of any kind.&nbsp;
    </div>
    <div>&nbsp;</div>
    <div>I'm extremely excited to (hopefully!) meet some of the knowledgeable and passionate people behind {1}. I'd definitely love it if we could set up a time to chat.</div>
    <div>&nbsp;</div>
    <div>Thank you so much!</div>
    <div>&nbsp;</div>
    <div>&nbsp;</div>
    <p>Yash Arora<br></p>
    <small>
    <a href="https://www.yasharora.com">Personal Website<br></a>
    <a href="https://www.linkedin.com/in/yasharora0606/">LinkedIn<br></a>
    <a href="https://github.com/YashArora0606">GitHub<br></a>
    </small>
    """.format(name_recruiter, company_name)

    message_template_plain = """
    Hi {0},

    I'm Yash, a Software Engineering student from the University of Waterloo. I found myself extremely interested in a software internship at {1}, and I wanted to reach out to you personally!

    Recently I interned at Localintel, a Seattle startup, where I led the development of their client management portal in addition to improving the efficiency and functionality of their platforms.
    Now, I'd love to bring my skills to your table.
    In terms of experience, I've worked extensively with Python, C++, Java, and Javascript (Frameworks), and am familiar with a variety of other languages and tools. 
    As a software enthusiast I'm always working on something new, with my most recent endeavor being the creation of an online collaborative code editor/whiteboard 
    (that you can try for yourself) called Ohana.
    If you'd like more detail about the work I've done, feel free to check out my resume; it's attached it in this email!
    I'd just like to add that I am a citizen in both the US and Canada, so I don't require any sponsorship of any kind.

    I'm extremely excited to (hopefully!) meet some of the knowledgable and passionate people behind {1}. I'd definitely love it if we could set up a time to chat.

    Thank you so much,


    Yash.
    """.format(name_recruiter, company_name)

    send_email(destination_email, message_template_html, message_template_plain, company_name)

def main():
    print(sys.getdefaultencoding())

    with open("recruiter_raw_data.csv", "r") as f:
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
