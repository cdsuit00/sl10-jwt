import os
from flask import Flask, jsonify
from .extensions import db, migrate, bcrypt, jwt
from .config import Config
from .auth_routes import bp_auth
from .expense_routes import bp_exp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Blueprints
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_exp)

    # JSON error handlers for clean API responses
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "bad request"}), 400

    @app.get("/")
    def index():
        return jsonify({"message": "JWT API ok"}), 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 5000)))
