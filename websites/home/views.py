from flask import Blueprint, render_template, redirect, url_for

home = Blueprint('home', __name__,
                 template_folder='templates',
                 static_folder='static')


@home.route('/')
def main():
    return redirect(url_for("mol_2_chemfig.home"))
