"""VibeDrive Flask application factory."""

import logging

from flask import Flask, jsonify

from app.config.settings import settings
from app.db.database import init_db_pool, teardown_db

logger = logging.getLogger(__name__)


def create_app(env: str = "development") -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Configuration
    app.config.update(
        ENVIRONMENT=env,
        DEBUG=settings.debug,
        SECRET_KEY=settings.secret_key,
        JSON_SORT_KEYS=False,
        SESSION_COOKIE_SECURE=env == "production",
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
    )

    # Initialize database pool
    init_db_pool(app)
    app.teardown_appcontext(teardown_db)

    # Register blueprints
    from app.routes.api import auth as api_auth
    from app.routes.api import skills as api_skills
    from app.routes.views import auth as view_auth
    from app.routes.views import dashboard as view_dashboard

    # API routes (JSON)
    app.register_blueprint(api_auth.bp, url_prefix="/api/auth")
    app.register_blueprint(api_skills.bp, url_prefix="/api/skills")

    # View routes (HTML)
    app.register_blueprint(view_auth.bp)
    app.register_blueprint(view_dashboard.bp)

    # Error handlers
    try:
        import psycopg2

        @app.errorhandler(psycopg2.OperationalError)
        def handle_db_error(e):
            logger.error(f"Database error: {e}")
            return jsonify({"error": "Service temporarily unavailable"}), 503
    except ImportError:
        pass

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return {"status": "ok", "version": settings.app_version}, 200

    # Home page
    @app.route("/")
    def index():
        from flask import render_template

        return render_template("index.html")

    logger.info(f"Flask app created for environment: {env}")
    return app
