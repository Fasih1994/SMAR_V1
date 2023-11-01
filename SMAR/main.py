from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

import resources
from db import db
from SMAR.auth_jwt import configure_jwt
from resources import (
    UserBlueprint,
    StoreBlueprint,
    ItemBlueprint,
    KeytermBlueprint
)

from flask import jsonify
from blocklist import BLOCKLIST


load_dotenv()
def create_app(db_url:str = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config["API_TITLE"] = "SMAR API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/keyterm/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", "sqlite:///data.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True


    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    

    app.config["JWT_SECRET_KEY"] = "Fasih's_version_of_SMAR"
    jwt = JWTManager(app)
    configure_jwt(jwt)

    # JWT configuration ends
    
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(KeytermBlueprint)
    
    return app



