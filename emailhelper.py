import os, smtplib, getpass, socket, sys, ssl
import traceback

from email.message import EmailMessage
from email.utils import make_msgid
from email.mime.application import MIMEApplication

from os.path import basename
import logging
# Configuration and Init section

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, format='%(levelname)-5s | %(asctime)s | %(message)s | %(filename)s:%(lineno)d', level=logging.INFO)

class EmailHelper:
    def __init__(self, subject, smtphost, port):
        self._smtphost = smtphost
        self._port = port
        self._emailfrom = getpass.getuser() + "@" + self.get_ip_address() + ".inet.arpa"
        self._msgbody = []
        self._subject = subject
        self._file = []
        self._secure=port != 25
        self._msg = EmailMessage()
        self._images = []
        self._asparagus_cid = make_msgid()[1:-1]

    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        logging.info('IP Address: ' + IP)
        return IP

    def append_file(self, file):
        self._file.append(file)

    def get_subject(self):
        return self._subject

    def set_subject(self, subject):
        self._subject = subject

    def append_msg_body(self, new_msg):
        # Ensure new_msg is a string and msg_list is a list
        if isinstance(self._msgbody, list) and isinstance(new_msg, str):
            self._msgbody.append(new_msg)  # Correctly appends the whole string as a single element

    def append_msg_body_image(self, image_file):
        cid = make_msgid()[1:-1]
        self._msgbody.append(f'<img src="cid:{cid}"/>')
        self._images.append((image_file, cid))

    def send_message(self, to):
        if not isinstance(to, list):
            raise Exception("to address list must be a python list.")

        self._msg['Subject'] = self._subject
        self._msg['From'] = self._emailfrom
        self._msg['To'] = ", ".join(to)
        joinedbody = "<br>".join(self._msgbody)
        body = """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
body {
    font-family: Arial, Geneva, Helvetica, san-serif;
    background-color: lightblue;
}
th { background-color: #6BCFE8; }
            </style>
        </head>
        <body>
            """ + joinedbody + f"""
        </body>
        </html>
        """
        self._msg.add_alternative(body, subtype="html")
        for img in self._images:
            with open(img[0], "rb") as img_file:
                self._msg.get_payload()[0].add_related(img_file.read(), 'image', 'png', cid=img[1])

        if(len(self._msgbody) > 0):
            # only if htmlBodyText contains data send email
            for f in self._file or []:
                with open(f, "rb") as fil:
                    part = MIMEApplication(
                        fil.read(),
                        Name=basename(f)
                    )
                # After the file is closed
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                self._msg.attach(part)
            try:
                with smtplib.SMTP(self._smtphost) as smtp:
                    if self._secure:
                        context = ssl.create_default_context()
                        smtp.starttls(context=context)
                        #smtp.login(user, pass)
                    smtp.send_message(self._msg)
                # tell the script to report if your message was sent or which errors need to be fixed
                logger.info('Email sent to: ' + str(to))
            except Exception as e:
                logger.info("SMTP error occurred: " + traceback.format_exc())
