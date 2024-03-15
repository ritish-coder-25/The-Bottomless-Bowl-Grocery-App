from flask_restful import Resource, fields, marshal_with, reqparse
from application.database import db
from application.models import Category, Product, Cart
from application.validation import NotFoundError, BusinessValidationError
from datetime import datetime
from sqlalchemy import func
from flask import session, request, jsonify
import json
from application.role_required import role_required
from flask_jwt_extended import get_jwt_identity, jwt_required

category_fields = {
    'Category_ID': fields.Integer,
    'Category_Name': fields.String,
}

product_fields = {
    'Product_ID': fields.Integer,
    'Product_Name': fields.String,
    'Category_Name': fields.String,
    'Mfg_Date': fields.String,
    'Exp_Date': fields.String,
    'Rate_Per_Unit': fields.Integer,
    'Available_Quantity': fields.Integer,
}

create_category_parser = reqparse.RequestParser()
create_category_parser.add_argument('Category_Name')

update_category_parser = reqparse.RequestParser()
update_category_parser.add_argument('Category_Name')

create_product_parser = reqparse.RequestParser()
create_product_parser.add_argument('Product_Name')
create_product_parser.add_argument('Category_Name')
create_product_parser.add_argument('Mfg_Date')
create_product_parser.add_argument('Exp_Date')
create_product_parser.add_argument('Rate_Per_Unit', type=int)
create_product_parser.add_argument('Available_Quantity', type=int)

update_product_parser = reqparse.RequestParser()
update_product_parser.add_argument('Product_Name')
update_product_parser.add_argument('Category_Name')
update_product_parser.add_argument('Mfg_Date')
update_product_parser.add_argument('Exp_Date')
update_product_parser.add_argument('Rate_Per_Unit', type=int)
update_product_parser.add_argument('Available_Quantity', type=int)

create_cart_parser = reqparse.RequestParser()
create_cart_parser.add_argument('Cart_Items')

class CategoryAPI(Resource):
    @marshal_with(category_fields)
    def get(self):
        category = Category.query.all()
        if category:
            return category, 200
        else:
            raise NotFoundError(status_code=404)

    @jwt_required()
    @role_required(['ADMIN'])
    @marshal_with(category_fields)
    def put(self, category_id):
        args = update_category_parser.parse_args()
        category_name = args.get('Category_Name')
        category = Category.query.get(category_id)
        if not category:
            raise NotFoundError(status_code=404, error_message='Category Not Found')
        
        if category_name is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="category name is required")

        category_check = db.session.query(Category).filter(Category.Category_Name == category_name).first()
        if category_check:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="Duplicate Category")

        category.Category_Name = category_name
        db.session.commit()
        return category, 203

    @jwt_required()
    @role_required(['ADMIN'])
    @marshal_with(category_fields)
    def delete(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            raise NotFoundError(status_code=404, error_message='Category not found')

        db.session.delete(category)
        db.session.commit()
        return 200

    @jwt_required()
    @role_required(['ADMIN'])
    @marshal_with(category_fields)
    def post(self):
        args = create_category_parser.parse_args()
        category_name = args.get('Category_Name', None)

        if category_name is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="category name is required")
        
        category = db.session.query(Category).filter(Category.Category_Name == category_name).first()
        if category:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="Duplicate Category")
        new_category = Category(Category_Name=category_name)
        db.session.add(new_category)
        db.session.commit()
        return new_category, 201

class ProductAPI(Resource):
    @marshal_with(product_fields)
    def get(self):
        product_name = request.args.get('Product_Name')
        category_name = request.args.get('Category_Name')
        rate_per_unit = request.args.get('Rate_Per_Unit', type=int)
        available_quantity = request.args.get('Available_Quantity', type=int)

        base_query = db.session.query(Product)

        # Apply filters based on the provided parameters
        if product_name:
            base_query = base_query.filter(func.lower(Product.Product_Name) == func.lower(product_name))

        if category_name:
            base_query = base_query.filter(func.lower(Product.Category_Name) == func.lower(category_name))

        if rate_per_unit is not None:
            base_query = base_query.filter(Product.Rate_Per_Unit == rate_per_unit)

        if available_quantity is not None:
            base_query = base_query.filter(Product.Available_Quantity == available_quantity)

        # Execute the final query and return the results
        products = base_query.all()

        if products:
            return products, 200
        else:
            return {"message": "No products match the specified criteria"}, 404
              
    @jwt_required()
    @role_required(['STORE MANAGER', 'ADMIN'])
    @marshal_with(product_fields)
    def put(self, product_id):
        args = update_product_parser.parse_args()
        product_name = args.get('Product_Name')
        category_name = args.get('Category_Name')
        mfg_date = args.get('Mfg_Date')
        exp_date = args.get('Exp_Date')
        rate_per_unit = args.get('Rate_Per_Unit')
        available_quantity = args.get('Available_Quantity')
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundError(status_code=404)

        if product_name is None:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="product name is required")

        if category_name is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="category name is required")

        if mfg_date is None:
            raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="mfg date is required")

        if exp_date is None:
            raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="exp date is required")

        if rate_per_unit is None:
            raise BusinessValidationError(status_code=400, error_code="BE1006", error_message="rate per unit is required")

        if available_quantity is None:
            raise BusinessValidationError(status_code=400, error_code="BE1007", error_message="available quantity is required")

        product_check = db.session.query(Product).filter(Product.Product_Name == product_name).first()
        if product_check:
            raise BusinessValidationError(status_code=409, error_code="BE1008", error_message="Duplicate Product")

        product.Product_Name = product_name
        product.Category_Name = category_name
        product.Mfg_Date = mfg_date
        product.Exp_Date = exp_date
        product.Rate_Per_Unit = rate_per_unit
        product.Available_Quantity = available_quantity
        db.session.commit()
        return product, 203

    @jwt_required()
    @role_required(['STORE MANAGER', 'ADMIN'])
    @marshal_with(product_fields)
    def delete(self, product_id):
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundError(status_code=404)
        db.session.delete(product)
        db.session.commit()
        return 204

    @jwt_required()
    @role_required(['STORE MANAGER', 'ADMIN'])
    @marshal_with(product_fields)
    def post(self):
        args = create_product_parser.parse_args()
        product_name = args.get('Product_Name', None)
        category_name = args.get('Category_Name', None)
        mfg_date = args.get('Mfg_Date', None)
        exp_date = args.get('Exp_Date', None)
        rate_per_unit = args.get('Rate_Per_Unit', None)
        available_quantity = args.get('Available_Quantity', None)

        if product_name is None:
            raise BusinessValidationError(status_code=400, error_code="BE1003", error_message="product name is required")

        if category_name is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="category name is required")

        if mfg_date is None:
            raise BusinessValidationError(status_code=400, error_code="BE1004", error_message="mfg date is required")

        if exp_date is None:
            raise BusinessValidationError(status_code=400, error_code="BE1005", error_message="exp date is required")

        if rate_per_unit is None:
            raise BusinessValidationError(status_code=400, error_code="BE1006", error_message="rate per unit is required")

        if available_quantity is None:
            raise BusinessValidationError(status_code=400, error_code="BE1007", error_message="available quantity is required")

        product_check = db.session.query(Product).filter(Product.Product_Name == product_name).first()
        if product_check:
            raise BusinessValidationError(status_code=409, error_code="BE1008", error_message="Duplicate Product")

        product = Product(Product_Name=product_name, Category_Name=category_name, Mfg_Date=mfg_date, Exp_Date=exp_date, Rate_Per_Unit=rate_per_unit, Available_Quantity=available_quantity)
        db.session.add(product)
        db.session.commit()
        return product, 200

class PurchaseAPI(Resource):
    @jwt_required()
    def post(self):
        try:
            curr_user = get_jwt_identity()
            user_id = curr_user.get('id')
            data = request.get_json()
            cart_data = data.get('cart')
            total_price = data.get('total')

            cart_entry = Cart(User_ID=user_id, Purchase_Date=datetime.utcnow(), Cart_Items=cart_data, Total_Price=total_price)
            db.session.add(cart_entry)
            db.session.commit()

            return {"message": "Purchase Successful"}, 200
        except Exception as e:
            return {"message": "Purchase Failed", "error": str(e)}, 500


