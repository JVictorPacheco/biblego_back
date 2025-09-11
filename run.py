import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Para desenvolvimento local
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    # Para produção (Render usará gunicorn)
    app.config['DEBUG'] = False