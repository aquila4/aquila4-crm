from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ================= USER =================
class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / marketer

    sales = db.relationship('Sale', backref='marketer', lazy=True)


# ================= SALE =================
class Sale(db.Model):
    __tablename__ = "sale"

    id = db.Column(db.Integer, primary_key=True)

    client_name = db.Column(db.String(100))
    amount = db.Column(db.Float)

    sale_type = db.Column(db.String(20))  # company / marketer

    marketer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    plot_number = db.Column(db.String(50))
    land_location = db.Column(db.String(100))

    marketer_name = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ================= COMMISSION =================
class Commission(db.Model):
    __tablename__ = "commission"

    id = db.Column(db.Integer, primary_key=True)

    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))
    marketer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    amount = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)