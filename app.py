from flask import Flask
from flask_cors import CORS
from db import db
from models import Brand, PromoCode
from routes import auth
from flask_jwt_extended import JWTManager

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///brands.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"

db.init_app(app)
jwt = JWTManager(app)
app.register_blueprint(auth)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Promo Admin Backend работает!"

if __name__ == "__main__":
    app.run(debug=True)
