from flask import Flask
# from App.Routes.task_routes import task_blueprint
from  app.Routes.user_routes import user_blueprint
from flasgger import Swagger
import os


def create_app():
    app_run = Flask(__name__)
    
    app_run.config['SWAGGER'] = {
        'title': 'API BibleGo',
        'uiversion': 3,
        'specs_route': '/api-docs/',
        'static_url_path': '/flasgger-static',
        'config_file': os.path.join(os.path.dirname(__file__), '..', 'swagger_config.yml')  # Caminho para o YAML
    }
    
    Swagger(app_run)
    app_run.register_blueprint(user_blueprint)
    return app_run
    
    
    # swagger = Swagger(app_run)
    # app_run.register_blueprint(user_blueprint)
    # return app_run

