from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import datetime, timedelta
import socket, random, secrets, threading, pytz, os, signal
from flask import request, redirect, url_for, session, render_template
from flask import Flask
from emailhelper import EmailHelper


logger = logging.getLogger(__name__)

app = Flask(__name__)
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

def send_email(shutdown_time, notify_email, server_ip, server_port, password, smtp_host, smtp_port):
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
    emailhelper = EmailHelper("Please login to the server", smtp_host, smtp_port)
    emailhelper.append_msg_body(message)
    emailhelper.send_message(receiver)

@app.before_request
def require_password():
    if not session.get('logged_in', False) and request.endpoint != 'login':
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == password:
            session['logged_in'] = True
            return redirect("/admin")
        else:
            error = 'Incorrect password'
    return render_template('login.html', error=error)

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

def find_available_port(host, port_range):
    for port in port_range:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port  # Port is available
            except socket.error as e:
                continue  # This port is already in use, try the next one
    return None  # No available port found

def start_receiver(args, password):
    global timer
    port_range = range(5000, 6000)
    server_port = find_available_port('0.0.0.0', port_range)
    if server_port is None:
        logger.error("No available ports in the specified range.")
        return
    shutdown_time = (datetime.now(pytz.utc) +
                   timedelta(minutes=int(args.timeout_minutes))).strftime("%A, %B %d, %Y at %H:%M:%S %Z")
    send_email(shutdown_time, args.notify_email, get_ip_address(), server_port, password, args.smtp_host, int(args.smtp_port))
    logger.info("Start a timer for automatic shutdown")
    timer = threading.Timer(int(args.timeout_minutes) * 60, shutdown_server)
    timer.start()
    logger.info(f"Starting server on {get_ip_address()}:{server_port}")
    app.run(host='0.0.0.0', port=server_port, debug=True, use_reloader=False)