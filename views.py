from flask import Blueprint

views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return "This is the home page!"


@views.route("/nothome")
def nothome():
    return "This is not the home page!"
