from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import datetime, timedelta
import socket, random, secrets, threading, pytz, os, signal
from flask import request, redirect, url_for, session
from flask import Flask
from emailhelper import EmailHelper


logger = logging.getLogger(__name__)

app = Flask(__name__)
server_port=5001
app.secret_key = 'something_random'+str(random.randint(1, 100)) # Needed for session management
password = secrets.token_urlsafe(16)

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

def send_email(shutdown_time, notify_email, server_ip, server_port=server_port, password=""):
    receiver = [notify_email]
    server_ip = get_ip_address()
    message = f"""
    <html>
    <head></head>
    <body style="{shared_styles['body']}">
    <div style="{shared_styles['email_container']}">
    <h2>Admin Panel Connection Details</h2>
    <div style="{shared_styles['email_content']}">
        An Admin Panel has been started by a team member.
        <p>You may connect to <a href="http://{server_ip}:{server_port}/admin" style="{shared_styles['highlight']}">http://{server_ip}:{server_port}/admin</a>.
        <p>Use the following password to access: <span style="{shared_styles['highlight']}">{password}</span></p>
        <div style="{shared_styles['server_info']}">
        <p><strong>Note:</strong> The server will be automatically shut down after the specified time</p>
        <p><span style="{shared_styles['highlight']}">{shutdown_time}</span></p>
        </div>
    </div>
    </div>
    </body>
    </html>
    """
    logger.debug(message)
    emailhelper = EmailHelper("Please send the file to the server")
    emailhelper.append_msg_body(message)
    emailhelper.send_message(receiver)

@app.before_request
def require_password():
    if not session.get('logged_in', False) and request.endpoint != 'login':
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == password:
            session['logged_in'] = True
            return redirect("/admin")
        else:
            return 'Incorrect password', 401
    return '''
    <!doctype html>
    <title>Login</title>
    <h1>Login</h1>
    <form method=post>
      Password: <input type=password name=password>
      <input type=submit value=Login>
    </form>
    '''

@app.route('/shutdown', methods=['GET'])
def shutdown_server():
    if timer.is_alive():
        timer.cancel()
    os.kill(os.getpid(), signal.SIGINT)
    return '''
    <script type="text/javascript">
        alert("Server has been shut down. Please close this browser tab.");
        window.close(); // This will not always work due to browser security restrictions.
    </script>
    '''

def start_receiver(timeout_minutes, notify_email, password):
    global timer
    shutdown_time = (datetime.now(pytz.utc) +
                   timedelta(minutes=timeout_minutes)).strftime("%A, %B %d, %Y at %H:%M:%S %Z")
    send_email(shutdown_time, notify_email, get_ip_address(), server_port, password)
    logger.info("Start a timer for automatic shutdown")
    timer = threading.Timer(timeout_minutes * 60, shutdown_server)
    timer.start()
    app.run(host='0.0.0.0', port=server_port, debug=True, use_reloader=False)