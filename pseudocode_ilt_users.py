
from fastapi import FastAPI

## establish db connection

ilt_app = FastAPI()

ilt_app.post('/api/v1/login')
async def fn_auth_user(sesssion, userId, password):
	## try to get the user from the users table

	try:
		user_record = users_tbl.query.filter(user_id = userId).first()

		if len(user_record) > 0:
			# get user_id, password inside database for user_record
			# see if user id and password match
			if match:
				return success_response
			else:
				return wrong_cred_response
		else:
			return user_not_found error
	except:
		return 500_server_error_here

