from flask import Flask, render_template
from flask_admin import Admin

#from model import User, Post, Role
#from view import UserView, PostView, RoleView
from shared import db

admin = Admin(name='Flask Admin Temp Server', template_mode='bootstrap4')

#admin.add_view(UserView(User, db.session, 'Users'))
#admin.add_view(PostView(Post, db.session, 'Posts'))
#admin.add_view(RoleView(Role, db.session, 'Roles'))

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SECRET_KEY"] = "mysecret"
    db.init_app(app)
    admin.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app