from flask import Flask

from auth import auth_bp
from config import Config
from extensions import db, mongo
from inventory import inventory_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    mongo.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
