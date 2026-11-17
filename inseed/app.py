from flask import Flask
from config import get_config
from database import init_db
from routes import api_bp

def create_app() -> Flask:
    """
    Application factory function that sets up the Flask application,
    loads configuration, initializes the database, and registers blueprints.
    """
    app = Flask(__name__)
    
    # Load configuration
    config_obj = get_config()
    app.config.from_object(config_obj)

    # Initialize database
    init_db(app)

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000)