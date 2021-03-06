from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from settings.config import database_name, database_password, database_user
from datetime import datetime
import random
import string
# Настройки flask и flasksqlalchemy + migrate
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{database_user}:{database_password}@localhost/{database_name}'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    """
        Модель пользователя
        :id: первичный ключ
        :vk_id: id пользователя вконтакте
        :gender: пол пользователя
        :city: город пользователя
        :count_attempts: количество допустимых попыток поиска
        :time_last_message: время последнего сообщения
        :referral_code: реферальный код
        :do_attempts: Сделано попыток поиска
        :time_last_attempt: время последней попытки
    """

    id = db.Column(db.Integer, primary_key=True)
    vk_id = db.Column(db.Integer, nullable=False, unique=True)
    gender = db.Column(db.String(16), nullable=True)
    city = db.Column(db.String(64), nullable=True)
    count_attempts = db.Column(db.Integer, default=6)
    state = db.Column(db.String(32), nullable=True)
    time_last_message = db.Column(db.DateTime, default=datetime.utcnow)
    search_gender = db.Column(db.String(32), nullable=True)
    referral_code = db.Column(db.String(10),
                    default=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))
    do_attempts = db.Column(db.Integer, default=0)
    time_last_attempt = db.Column(db.DateTime)


class Room(db.Model):
    """
        Модель комнаты
        :id: первичный ключ
        :first_user_vk_id: vk id первого пользователя
        :second_user_vk_id: id второго пользователя
        :city: город по которому ищут
        :search_gender: пол который ищут
        :gender_first_user: пол того, кто создал поиск
    """

    id = db.Column(db.Integer, primary_key=True)
    first_user_vk_id = db.Column(db.Integer)
    second_user_vk_id = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String(64), nullable=True)
    search_gender = db.Column(db.String(16), nullable=True)
    gender_first_user = db.Column(db.String(16), nullable=True)