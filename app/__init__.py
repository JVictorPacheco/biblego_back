from flask import Flask
# from App.Routes.task_routes import task_blueprint
from  app.Routes.task_routes import user_blueprint


def create_app():
    app_run = Flask(__name__)
    app_run.register_blueprint(user_blueprint)
    return app_run

