from functools import wraps, update_wrapper
from flask_jwt_extended import get_jwt_identity
from application.models import User

def role_required(roles):
	def decorator(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			try:
				curr_user = get_jwt_identity()
				id = curr_user.get('id')

				if not id:
					return {"message": "Invalid Token"}, 403

				user = User.query.filter_by(id = id).first()
				if not user:
					return {"message": "User Not Found"}, 404

				if not user.role in roles:
					return {"message": "Unauthorised"}
				return fn(*args, **kwargs)

			except Exception as e:
				return {"message": "External Server Error"}, 500
		return update_wrapper(wrapper, fn)
	return decorator
