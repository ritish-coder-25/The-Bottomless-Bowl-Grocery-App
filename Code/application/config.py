import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
	DEBUG = False
	SQLITE_DB_DIR = None
	SQLALCHEMY_DATABASE_URI = None
	SQLALCHEMY_TRACK_NOTIFICATION = False

class LocalDevelopmentConfig(Config):
	SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
	SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "database.sqlite3")
	DEBUG = True
	SECRET_KEY = "238ypnhw13y209386bgal"
	SECURITY_PASSWORD_HASH = "bcrypt"
	SECURITY_PASSWORD_SALT = "Really important to remember that this is very important" #unique paswword key or salt
	SECURITY_REGISTERABLE = True
	SECURITY_SEND_REGISTER_EMAIL = False
	SECURITY_UNAUTHORIZED_VIEW = None
	JWT_SECRET_KEY = 'euathenuiahseoihnp'
	JWT_TOKEN_LOCATION = ['headers']
	JWT_COOKIE_CSRF_PROTECT = False
	JWT_COOKIE_SECURE = False
	JWT_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SAMESITE = None
	SESSION_COOKIE_SECURE = False
	
class ProductionConfig(Config):
	SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
	SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "database.sqlite3")
	DEBUG = False
