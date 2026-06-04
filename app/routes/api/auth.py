"""Authentication API routes (JSON endpoints)."""

import logging

from flask import Blueprint, request, jsonify

from app.auth.auth import create_access_token

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

    # TODO: Verify username/password against database
    # For now, stub implementation
    user_id = 1  # Placeholder

    token = create_access_token({"user_id": user_id})
    return jsonify({"access_token": token, "token_type": "bearer"}), 200


@bp.route("/refresh", methods=["POST"])
def refresh_token():
    """POST /api/auth/refresh - Refresh JWT token."""
    # TODO: Implement token refresh logic
    return jsonify({"error": "Not implemented"}), 501
