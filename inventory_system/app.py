from flask import Flask, request, jsonify, session, render_template
from auth import auth_bp
from config import Config
from extensions import db
from inventory import inventory_bp
from inventory import InventoryItem  
from auth import login_required  
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
