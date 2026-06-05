"""Authentication API routes (JSON endpoints)."""

import logging

from flask import Blueprint, jsonify, request

from app.auth.auth import create_access_token
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

bp = Blueprint("api_auth", __name__)


@bp.route("/token", methods=["POST"])
def get_token():
    """POST /api/auth/token - Get JWT token."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = UserService.authenticate_user(username, password)
    if user is None:
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_access_token({"user_id": user.id})
    return jsonify({"access_token": token, "token_type": "bearer"}), 200


@bp.route("/refresh", methods=["POST"])
def refresh_token():
    """POST /api/auth/refresh - Refresh JWT token."""
    # TODO: Implement token refresh logic
    return jsonify({"error": "Not implemented"}), 501
