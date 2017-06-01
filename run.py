from flask import Flask


def create_app():
    app = Flask(__name__)
    from websites.home.views import home
    from websites.mol_2_chemfig.views import mol_2_chemfig
    from websites.ml_app.views import ml_app

    app.register_blueprint(home)
    app.register_blueprint(mol_2_chemfig, url_prefix='/mol_2_chemfig')
    app.register_blueprint(ml_app, url_prefix='/ml_app')
    app.secret_key = '&T\xb0\xe4\xea\xdf\x85%-\xe0\xd6g?;\xa9\xe0vU\xeed"\x806\x9a'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    return app
