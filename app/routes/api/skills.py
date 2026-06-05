"""Skill management API routes (JSON endpoints)."""

import logging
from functools import wraps

from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.auth.auth import get_current_user_from_token
from app.models import SkillCreate, SkillUpdate
from app.services.skill_service import SkillService

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
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    skills = SkillService.get_user_skills(g.user_id, skip, limit)
    return jsonify([s.model_dump(mode="json") for s in skills]), 200


@bp.route("", methods=["POST"])
@require_api_auth
def create_skill():
    """POST /api/skills - Create a new skill."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    try:
        skill_create = SkillCreate(**data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 422

    skill = SkillService.create_skill(g.user_id, skill_create)
    return jsonify(skill.model_dump(mode="json")), 201


@bp.route("/<int:skill_id>", methods=["GET"])
@require_api_auth
def get_skill(skill_id):
    """GET /api/skills/{id} - Get a specific skill."""
    skill = SkillService.get_skill(g.user_id, skill_id)
    if skill is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(skill.model_dump(mode="json")), 200


@bp.route("/<int:skill_id>", methods=["PATCH"])
@require_api_auth
def update_skill(skill_id):
    """PATCH /api/skills/{id} - Update a skill."""
    data = request.get_json(silent=True) or {}

    try:
        skill_update = SkillUpdate(**data)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 422

    skill = SkillService.update_skill(g.user_id, skill_id, skill_update)
    if skill is None:
        return jsonify({"error": "Not found"}), 404

    return jsonify(skill.model_dump(mode="json")), 200


@bp.route("/<int:skill_id>", methods=["DELETE"])
@require_api_auth
def delete_skill(skill_id):
    """DELETE /api/skills/{id} - Delete a skill."""
    deleted = SkillService.delete_skill(g.user_id, skill_id)
    if not deleted:
        return jsonify({"error": "Not found"}), 404
    return "", 204
