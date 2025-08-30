from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from .extensions import db, JWT_BLOCKLIST
from .models import User
from .schemas import UserSchema

bp_auth = Blueprint("auth", __name__)
user_schema = UserSchema()

@bp_auth.post("/signup")
def signup():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400
    if password != password_confirmation:
        return jsonify({"error": "passwords do not match"}), 422
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already taken"}), 409

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user_schema.dump(user)}), 201

@bp_auth.post("/login")
def login():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        # do not leak which part failed
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token, "user": user_schema.dump(user)}), 200

@bp_auth.get("/me")
@jwt_required()
def me():
    uid = get_jwt_identity()
    user = User.query.get_or_404(uid)
    return jsonify(user_schema.dump(user)), 200

# Optional: JWT "logout" via revocation
@bp_auth.post("/logout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    JWT_BLOCKLIST.add(jti)
    return jsonify({"message": "token revoked"}), 200