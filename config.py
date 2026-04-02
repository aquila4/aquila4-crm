import os

class Config:
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:jGNEMNdfkQiNnUlvVSlbxQamOkwTAchb@centerbeam.proxy.rlwy.net:25167/railway?sslmode=require"
    SQLALCHEMY_TRACK_MODIFICATIONS = False