from flask import Flask
# from App.Routes.task_routes import task_blueprint
from  app.Routes.user_routes import user_blueprint
from app.Routes.auth_routes import auth_blueprint
from app.Routes.devotional_routes import devotional_blueprint
from flasgger import Swagger
#import os


def create_app():
    app_run = Flask(__name__)
    
    app_run.config['SWAGGER'] = {
    'title': 'API BibleGo',
    'uiversion': 3,
    'specs_route': '/api-docs/',
    'securityDefinitions': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Insira o token JWT no formato: Bearer {seu_token}'
        }
    },
    'security': [{'BearerAuth': []}]
}
    
    Swagger(app_run)
    app_run.register_blueprint(auth_blueprint)
    app_run.register_blueprint(user_blueprint)
    app_run.register_blueprint(devotional_blueprint)
  
    return app_run
    
    
    # swagger = Swagger(app_run)
    # app_run.register_blueprint(user_blueprint)
    # return app_run

