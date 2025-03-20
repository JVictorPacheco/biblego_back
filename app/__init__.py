from flask import Flask
# from App.Routes.task_routes import task_blueprint
from  app.Routes.task_routes import task_blueprint


def create_app():
    app_run = Flask(__name__)
    app_run.register_blueprint(task_blueprint)
    return app_run

