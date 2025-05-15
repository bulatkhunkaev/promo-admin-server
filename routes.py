from flask import Blueprint, request, jsonify
from models import Brand, PromoCode
from db import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bcrypt = Bcrypt()
auth = Blueprint("auth", __name__)

# Регистрация бренда
@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required_fields = ["name", "channel", "avatar", "topic", "email", "login", "password", "confirm_password"]
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Заполните все поля"}), 400

    if Brand.query.filter_by(username=data["login"]).first():
        return jsonify({"message": "Такой логин уже занят"}), 400

    if data["password"] != data["confirm_password"]:
        return jsonify({"message": "Пароли не совпадают"}), 400

    brand = Brand(
        name=data["name"],
        channel=data["channel"],
        avatar_url=data["avatar"],
        category=data["topic"],
        email=data["email"],
        username=data["login"]
    )
    brand.set_password(data["password"])

    db.session.add(brand)
    db.session.commit()

    return jsonify({"message": "Бренд зарегистрирован успешно"})

# Авторизация бренда
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if "login" not in data or "password" not in data:
        return jsonify({"message": "Укажите логин и пароль"}), 400

    brand = Brand.query.filter_by(username=data["login"]).first()

    if brand and brand.check_password(data["password"]):
        access_token = create_access_token(identity=str(brand.id))
        return jsonify(access_token=access_token)

    return jsonify({"message": "Неверные учетные данные"}), 401

# Создание промокода
@auth.route("/promo/create", methods=["POST"])
@jwt_required()
def create_promo():
    data = request.get_json()
    brand_id = get_jwt_identity()

    if "code" not in data or "discount" not in data:
        return jsonify({"message": "Укажите промокод и скидку"}), 400

    promo = PromoCode(
        brand_id=int(brand_id),
        code=data["code"],
        discount=data["discount"]
    )

    db.session.add(promo)
    db.session.commit()

    return jsonify({"message": "Промокод опубликован"})

# ✅ Получение всех брендов с последним промокодом
@auth.route("/brands", methods=["GET"])
def get_brands():
    brands = Brand.query.all()
    result = []
    for brand in brands:
        latest_promo = PromoCode.query.filter_by(brand_id=brand.id).order_by(PromoCode.id.desc()).first()
        result.append({
            "id": brand.id,
            "name": brand.name,
            "channel": brand.channel,
            "avatar": brand.avatar_url,
            "category": brand.category,
            "discount": latest_promo.discount if latest_promo else ""
        })
    return jsonify(result)

# 🔹 Получение всех промокодов бренда
@auth.route("/promos/<int:brand_id>", methods=["GET"])
def get_promos(brand_id):
    promos = PromoCode.query.filter_by(brand_id=brand_id).all()
    return jsonify([
        {"code": p.code, "discount": p.discount}
        for p in promos
    ])
