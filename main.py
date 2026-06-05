"""VibeDrive Flask application entry point."""

import os

from app import create_app

if __name__ == "__main__":
    env = os.getenv("APP_ENV", "development")
    app = create_app(env)
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=app.config.get("DEBUG", False),
    )
