"""Authentication view routes (HTML pages)."""

import logging
from functools import wraps

from flask import Blueprint, g, redirect, render_template, request, session, url_for

from app.auth.auth import (
    create_access_token,
    get_current_user_from_token,
)

logger = logging.getLogger(__name__)

bp = Blueprint("auth", __name__)


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


@bp.route("/login", methods=["GET", "POST"])
def login():
    """GET /login - Show login form, POST /login - Handle login."""
    if request.method == "GET":
        return render_template("auth/login.html")

    # POST: Handle login
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return (
            render_template("auth/login.html", error="Username and password required"),
            400,
        )

    # TODO: Verify against database
    # For now, stub implementation
    user_id = 1  # Placeholder

    token = create_access_token({"user_id": user_id})
    session["access_token"] = token
    session["user_id"] = user_id

    return redirect(url_for("dashboard.list_skills"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    """GET /register - Show registration form, POST /register - Handle registration."""
    if request.method == "GET":
        return render_template("auth/register.html")

    # POST: Handle registration
    username = request.form.get("username")
    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")

    if not username or not password or not password_confirm:
        return render_template("auth/register.html", error="All fields required"), 400

    if password != password_confirm:
        return (
            render_template("auth/register.html", error="Passwords do not match"),
            400,
        )

    if len(password) < 8:
        return (
            render_template(
                "auth/register.html", error="Password must be at least 8 characters"
            ),
            400,
        )

    # TODO: Create user in database
    # For now, stub implementation
    user_id = 1  # Placeholder

    token = create_access_token({"user_id": user_id})
    session["access_token"] = token
    session["user_id"] = user_id

    return redirect(url_for("dashboard.list_skills"))


@bp.route("/logout", methods=["GET"])
def logout():
    """GET /logout - Logout user."""
    session.clear()
    return redirect(url_for("auth.login"))
