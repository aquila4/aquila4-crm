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

    # relationships
    sales = db.relationship('Sale', backref='user', lazy=True)
    commissions = db.relationship('Commission', backref='user', lazy=True)

    # link to marketer profile (if user is a marketer)
    marketer = db.relationship('Marketer', backref='user', uselist=False)


# ================= MARKETER =================
class Marketer(db.Model):
    __tablename__ = "marketer"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔥 IMPORTANT: This connects marketer to sales
    sales = db.relationship('Sale', backref='marketer', lazy=True)

    # 🔥 IMPORTANT: This connects marketer to commissions
    commissions = db.relationship('Commission', backref='marketer', lazy=True)


# ================= SALE =================
class Sale(db.Model):
    __tablename__ = "sale"

    id = db.Column(db.Integer, primary_key=True)

    client_name = db.Column(db.String(100))
    amount = db.Column(db.Float)

    sale_type = db.Column(db.String(20))  # company / marketer

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    plot_number = db.Column(db.String(50))
    land_location = db.Column(db.String(100))

    # 🔥 links sale to marketer
    marketer_id = db.Column(db.Integer, db.ForeignKey('marketer.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ================= COMMISSION =================
class Commission(db.Model):
    __tablename__ = "commission"

    id = db.Column(db.Integer, primary_key=True)

    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # 🔥 links commission to marketer
    marketer_id = db.Column(db.Integer, db.ForeignKey('marketer.id'))

    amount = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)