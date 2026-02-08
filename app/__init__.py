from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_babel import Babel
from flask_login import LoginManager
from flask_mail import Mail

def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

app = Flask(__name__)

babel = Babel(app, locale_selector=get_locale)
admin = Admin(app,template_mode='bootstrap4')

app.config.from_object('config')

login_manager = LoginManager(app)
login_manager.login_view = "login"
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp0001.neo.space'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'noreply@drivehive.site'
app.config['MAIL_PASSWORD'] = 'YellowBeeDriveHive2025!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

from app import views, models,ai
