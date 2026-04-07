import os

class Config:
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:IQgcrwOKpdDPYokDWYWzWhXxeputfxbv@maglev.proxy.rlwy.net:42223/railway"
    SQLALCHEMY_TRACK_MODIFICATIONS = False