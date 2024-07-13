from dotenv import load_dotenv
load_dotenv()
import sys, os, logging, argparse
from flask import Flask, render_template, request, redirect, url_for, session
from flask_admin import Admin
from model import User, Post, Role
from view import UserView, PostView, RoleView
from shared import db, app, password, start_receiver
from flask_admin.menu import MenuLink


logging.basicConfig(stream=sys.stdout, format='%(levelname)-5s | %(asctime)s | %(message)s | %(filename)s:%(lineno)d', level=logging.INFO)

logger = logging.getLogger(__name__)

@app.route("/")
def index():
    return render_template("admin/index.html")

if __name__ == '__main__':

    # Setup argparse
    parser = argparse.ArgumentParser(description='Start the server. Requires the following arguments however you can run setup.py to create a .env file and use that instead.')
    parser.add_argument('--timeout_minutes', required=False, type=int, help='The timeout in minutes after which the server should shut down.')
    parser.add_argument('--notify_email', required=False, type=str, help='The email address to notify about sending the file.')
    parser.add_argument('--smtp_host', required=False, type=str)
    parser.add_argument('--smtp_port', required=False, type=int)
    parser.add_argument('--db_uri', required=False, type=str)
    args = parser.parse_args()

    # Validate arguments and environment variables
    if not args.timeout_minutes and not 'TIMEOUT_MINUTES' in os.environ:
        raise ValueError("TIMEOUT_MINUTES must be provided as a parameter or in the environment variables.")
    if not args.timeout_minutes:
        args.timeout_minutes = os.environ['TIMEOUT_MINUTES']

    if not args.notify_email and not 'NOTIFY_EMAIL' in os.environ:
        raise ValueError("NOTIFY_EMAIL must be provided as a parameter or in the environment variables.")
    if not args.notify_email:
        args.notify_email = os.environ['NOTIFY_EMAIL']

    if not args.db_uri and not 'DB_URI' in os.environ:
        raise ValueError("DB_URI must be provided as a parameter or in the environment variables.")
    if not args.db_uri:
        args.db_uri = os.environ['DB_URI']

    if not args.smtp_host and not 'SMTP_HOST' in os.environ:
        raise ValueError("SMTP_HOST must be provided as a parameter or in the environment variables.")
    if not args.smtp_host:
        args.smtp_host = os.environ['SMTP_HOST']

    if not args.smtp_port and not 'SMTP_PORT' in os.environ:
        raise ValueError("SMTP_PORT must be provided as a parameter or in the environment variables.")
    if not args.smtp_port:
        args.smtp_port = os.environ['SMTP_PORT']

    timer = None
    admin = Admin(name='Flask Admin Temp Server', template_mode='bootstrap4')

    app.config["SQLALCHEMY_DATABASE_URI"] = args.db_uri # "sqlite:///db.sqlite3"
    db.init_app(app)
    admin.init_app(app)

    admin.add_view(UserView(User, db.session, 'Users'))
    admin.add_view(PostView(Post, db.session, 'Posts'))
    admin.add_view(RoleView(Role, db.session, 'Roles'))
    admin.add_link(MenuLink(name='Shutdown', endpoint='shutdown_server'))

    start_receiver(args, password)
