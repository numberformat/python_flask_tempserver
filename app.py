import sys, os, logging, argparse, threading, signal, pytz, random, secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from flask_admin import Admin
from emailhelper import EmailHelper
from model import User, Post, Role
from view import UserView, PostView, RoleView
from shared import db, get_ip_address, shared_styles
from flask_admin.menu import MenuLink

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, format='%(levelname)-5s | %(asctime)s | %(message)s | %(filename)s:%(lineno)d', level=logging.INFO)

logger = logging.getLogger(__name__)

## Constants BEGIN
app = Flask(__name__)
server_port=5001
app.secret_key = 'something_random'+str(random.randint(1, 100)) # Needed for session management
password = secrets.token_urlsafe(16)
## Constrants END

timer = None
admin = Admin(name='Flask Admin Temp Server', template_mode='bootstrap4')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
db.init_app(app)
admin.init_app(app)

admin.add_view(UserView(User, db.session, 'Users'))
admin.add_view(PostView(Post, db.session, 'Posts'))
admin.add_view(RoleView(Role, db.session, 'Roles'))
admin.add_link(MenuLink(name='Shutdown', endpoint='shutdown_server'))

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

def start_receiver(timeout_minutes, notify_email, password):
    global timer
    shutdown_time = (datetime.now(pytz.utc) +
                   timedelta(minutes=timeout_minutes)).strftime("%A, %B %d, %Y at %H:%M:%S %Z")
    send_email(shutdown_time, notify_email, get_ip_address(), server_port, password)
    logger.info("Start a timer for automatic shutdown")
    timer = threading.Timer(timeout_minutes * 60, shutdown_server)
    timer.start()
    app.run(host='0.0.0.0', port=server_port, debug=True, use_reloader=False)

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

@app.route("/")
def index():
    return render_template("admin/index.html")

if __name__ == '__main__':
    # Setup argparse
    parser = argparse.ArgumentParser(description='Start the file upload receiver.')
    parser.add_argument('--timeout_minutes', required=False, default=1440, type=int, help='The timeout in minutes after which the server should shut down.')
    parser.add_argument('--notify_email', required=True, type=str, help='The email address to notify about sending the file.')
    args = parser.parse_args()

    start_receiver(args.timeout_minutes, args.notify_email, password)
