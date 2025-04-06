# import sys
# import os

# # Adiciona o diretório raiz ao PYTHONPATH
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
    
app_run = create_app()

if __name__ == '__main__':
    app_run.run(debug=True)