from application.database import db
from datetime import datetime
import json
from sqlalchemy import JSON, Text

class Role(db.Model):
	__tablename__ = "Role"
	id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
	name = db.Column(db.String(20), unique=True, nullable=False)
	description = db.Column(db.String(100))

class User(db.Model):
	__tablename__ = "User"
	id =db.Column(db.Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
	email = db.Column(db.String(20), unique=True, nullable=False)
	password = db.Column(db.String(10), nullable=False, unique=True)
	active = db.Column(db.Integer(), nullable=False)
	role = db.Column(db.String(20), db.ForeignKey('Role.name'))

class Category(db.Model):
	__tablename__ = "Category"
	Category_ID = db.Column(db.Integer(), primary_key=True, unique=True, nullable=False, autoincrement=True)
	Category_Name = db.Column(db.String(20), unique=True, nullable=False)
	products = db.relationship('Product', back_populates='category', cascade="all, delete-orphan")

class Product(db.Model):
	__tablename__ = "Product"
	Product_ID = db.Column(db.Integer(), nullable=False, primary_key=True, unique=True)
	Category_Name = db.Column(db.String(20), db.ForeignKey(Category.Category_Name, ondelete='CASCADE'), nullable=False)
	Product_Name = db.Column(db.String(20), nullable=False, unique=True)
	Mfg_Date = db.Column(db.String(15), nullable=False)
	Exp_Date = db.Column(db.String(15), nullable=False)
	Rate_Per_Unit = db.Column(db.Integer(), nullable=False)
	Available_Quantity = db.Column(db.Integer(), nullable=False)

	category = db.relationship('Category', back_populates='products')

class Cart(db.Model):
    __tablename__ = "Cart"
    Cart_ID = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    User_ID = db.Column(db.Integer(), db.ForeignKey('User.id'), nullable=False)
    Purchase_Date = db.Column(db.DateTime(), default=datetime.utcnow)
    Cart_Items = db.Column(JSON)
    Total_Price = db.Column(db.Integer())

    def get_cart_items(self):
    	return json.loads(self.Cart_Items)

    def set_cart_items(self, cart_items):
    	self.Cart_Items = json.dumps(cart_items)
    	

    cart_items = property(get_cart_items, set_cart_items)

class Request(db.Model):
	__tablename__ = "Request"
	id = db.Column(db.Integer(), primary_key=True)
	user_id = db.Column(db.Integer(), nullable=False)
	request_text = db.Column(db.String(255), nullable=False)
	status = db.Column(db.String(10))

class UserRequest(db.Model):
	__tablename__ = "UserRequest"
	email = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
	password = db.Column(db.String(10), nullable=False)
