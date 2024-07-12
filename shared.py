from flask_sqlalchemy import SQLAlchemy

import socket

def get_ip_address():
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
    return IP

shared_styles = {
    "body": "font-family: Arial, sans-serif; background-color: #ffffff;",
    "email_container": "padding: 20px;",
    "email_content": "margin: 20px 0;",
    "server_info": "background-color: #f2f2f2; padding: 15px; border-radius: 5px;",
    "highlight": "color: #007bff;"
}

db = SQLAlchemy()
