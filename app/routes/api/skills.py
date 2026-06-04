"""Skill management API routes (JSON endpoints)."""

import logging
from functools import wraps

from flask import Blueprint, g, jsonify, request

from app.auth.auth import get_current_user_from_token

logger = logging.getLogger(__name__)

bp = Blueprint("api_skills", __name__)


def require_api_auth(f):
    """Require JWT authentication for API routes."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing authorization token"}), 401

        token = auth_header.split(" ")[1]
        user_id = get_current_user_from_token(token)
        if user_id is None:
            return jsonify({"error": "Invalid token"}), 401

        g.user_id = user_id
        return f(*args, **kwargs)

    return decorated_function


@bp.route("", methods=["GET"])
@require_api_auth
def list_skills():
    """GET /api/skills - List user's skills."""
    _skip = request.args.get("skip", 0, type=int)
    _limit = request.args.get("limit", 10, type=int)
    _user_id = g.user_id
    # TODO: Implement with skill service
    return jsonify([]), 200


@bp.route("", methods=["POST"])
@require_api_auth
def create_skill():
    """POST /api/skills - Create a new skill."""
    _user_id = g.user_id
    _data = request.get_json()
    # TODO: Implement with skill service
    return jsonify({"error": "Not implemented"}), 501


@bp.route("/<int:skill_id>", methods=["GET"])
@require_api_auth
def get_skill(skill_id):
    """GET /api/skills/{id} - Get a specific skill."""
    _user_id = g.user_id
    # TODO: Implement with skill service
    return jsonify({"error": "Not implemented"}), 501


@bp.route("/<int:skill_id>", methods=["PATCH"])
@require_api_auth
def update_skill(skill_id):
    """PATCH /api/skills/{id} - Update a skill."""
    _user_id = g.user_id
    _data = request.get_json()
    # TODO: Implement with skill service
    return jsonify({"error": "Not implemented"}), 501


@bp.route("/<int:skill_id>", methods=["DELETE"])
@require_api_auth
def delete_skill(skill_id):
    """DELETE /api/skills/{id} - Delete a skill."""
    _user_id = g.user_id
    # TODO: Implement with skill service
    return "", 204
