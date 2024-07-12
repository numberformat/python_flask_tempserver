import sys, os, logging, argparse, threading, signal, pytz, random, secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from flask_admin import Admin
from emailhelper import EmailHelper
from model import User, Post, Role
from view import UserView, PostView, RoleView
from shared import db, get_ip_address, shared_styles, send_email, app, server_port, password, start_receiver
from flask_admin.menu import MenuLink

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, format='%(levelname)-5s | %(asctime)s | %(message)s | %(filename)s:%(lineno)d', level=logging.INFO)

logger = logging.getLogger(__name__)


timer = None
admin = Admin(name='Flask Admin Temp Server', template_mode='bootstrap4')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
db.init_app(app)
admin.init_app(app)

admin.add_view(UserView(User, db.session, 'Users'))
admin.add_view(PostView(Post, db.session, 'Posts'))
admin.add_view(RoleView(Role, db.session, 'Roles'))
admin.add_link(MenuLink(name='Shutdown', endpoint='shutdown_server'))


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
