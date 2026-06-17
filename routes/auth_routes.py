from flask import Blueprint, request, jsonify
from database.db import signup_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():

    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    success = signup_user(name, email, password)

    if success:
        return jsonify({"status": "user_created"})

    return jsonify({"status": "email_exists"})


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    user = login_user(email, password)

    if user:

        return jsonify({
            "status": "success",
            "user_id": user["id"],
            "name": user["name"],
            "role": user["role"]
        })

    return jsonify({"status": "invalid_credentials"})