from flask import Blueprint, render_template

ml_app = Blueprint('ml_app', __name__,
                   template_folder='templates',
                   static_folder='static')


@ml_app.route('/')
def home():
    return render_template('ml_app/index.html')
