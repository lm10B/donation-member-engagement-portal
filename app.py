from flask import Flask

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    from models.user import User

    @app.route("/")
    def home():
        return "Donation and Member Engagement Portal"

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)