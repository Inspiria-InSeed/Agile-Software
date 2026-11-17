from flask import Flask
from config import get_config
from models import db

def init_db(app: Flask) -> None:
    """
    Initializes the database by configuration and creates all tables.
    Also handles database connection management binding to the Flask app.
    """
    config_obj = get_config()
    app.config.from_object(config_obj)
    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error initializing database tables: {e}")

def get_db_session():
    """Returns the scoped session managed by SQLAlchemy."""
    return db.session

if __name__ == "__main__":
    # Minimal example of running database creation if called directly
    from flask import Flask
    temp_app = Flask(__name__)
    init_db(temp_app)
    print("Database initialized successfully.")