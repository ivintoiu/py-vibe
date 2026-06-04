"""Dashboard view routes (HTML pages)."""

import logging
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, g

from app.auth.auth import get_current_user_from_token

logger = logging.getLogger(__name__)

bp = Blueprint("dashboard", __name__)


def login_required(f):
    """Require user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("access_token")
        if not token:
            return redirect(url_for("auth.login"))

        user_id = get_current_user_from_token(token)
        if user_id is None:
            session.clear()
            return redirect(url_for("auth.login"))

        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function


@bp.route("/dashboard", methods=["GET"])
@login_required
def list_skills():
    """GET /dashboard - Show user's skills dashboard."""
    user_id = g.user_id
    # TODO: Fetch skills from database
    skills = []
    return render_template("dashboard.html", skills=skills)


@bp.route("/skills", methods=["GET"])
@login_required
def view_skills():
    """GET /skills - List all user's skills."""
    user_id = g.user_id
    # TODO: Fetch skills from database
    skills = []
    return render_template("skills/list.html", skills=skills)


@bp.route("/skills/create", methods=["GET", "POST"])
@login_required
def create_skill():
    """GET /skills/create - Show create skill form, POST /skills/create - Create skill."""
    if request.method == "GET":
        return render_template("skills/create.html")

    # POST: Handle skill creation
    user_id = g.user_id
    name = request.form.get("name")
    description = request.form.get("description")
    difficulty_level = request.form.get("difficulty_level", 1, type=int)
    estimated_hours = request.form.get("estimated_hours", 0, type=int)

    if not name:
        return render_template("skills/create.html", error="Skill name required"), 400

    # TODO: Create skill in database
    return redirect(url_for("dashboard.list_skills"))


@bp.route("/skills/<int:skill_id>", methods=["GET"])
@login_required
def view_skill(skill_id):
    """GET /skills/{id} - View skill details."""
    user_id = g.user_id
    # TODO: Fetch skill from database
    skill = None
    if not skill:
        return "Skill not found", 404
    return render_template("skills/detail.html", skill=skill)


@bp.route("/skills/<int:skill_id>/edit", methods=["GET", "POST"])
@login_required
def edit_skill(skill_id):
    """GET /skills/{id}/edit - Show edit form, POST - Update skill."""
    user_id = g.user_id
    # TODO: Fetch skill from database
    skill = None
    if not skill:
        return "Skill not found", 404

    if request.method == "GET":
        return render_template("skills/edit.html", skill=skill)

    # POST: Handle skill update
    name = request.form.get("name")
    description = request.form.get("description")
    difficulty_level = request.form.get("difficulty_level", type=int)
    estimated_hours = request.form.get("estimated_hours", type=int)

    if not name:
        return render_template("skills/edit.html", skill=skill, error="Skill name required"), 400

    # TODO: Update skill in database
    return redirect(url_for("dashboard.view_skill", skill_id=skill_id))


@bp.route("/skills/<int:skill_id>/delete", methods=["POST"])
@login_required
def delete_skill(skill_id):
    """POST /skills/{id}/delete - Delete skill."""
    user_id = g.user_id
    # TODO: Delete skill from database
    return redirect(url_for("dashboard.list_skills"))
