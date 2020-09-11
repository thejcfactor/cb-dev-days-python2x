from flask import jsonify, request, g
from functools import wraps
from service.user_service import UserService
from library.response import Response

user_svc = UserService()

def verify_token(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        bearer_header = request.headers.get('Authorization', None)
        response = Response(None, None, None, None)
        if not bearer_header:
            response.message = 'No authorization token provided.'
            response.authorized = False
            g.jwt = {
                'token': None,
                'sessionRes': response
            }
            return f(*args, **kwargs)

        try:
            token = bearer_header.replace('Bearer ', '')
            ext_session_res = user_svc.extend_session(token)
            #Couchbase KeyNotFound - unauthorized (i.e. session expired)
            # if response.error:
            #     response.request_id = req_id
            #     if response.authorized is not None and not response.authorized:
            #         return jsonify(response.to_dict()), 401
            #     else:
            #         return jsonify(response.to_dict()), 500
                    
            #https://stackoverflow.com/questions/22256862/flask-how-to-store-and-retrieve-a-value-bound-to-the-request/22256956
            g.jwt = {
                'token': None if ext_session_res.error else token,
                'sessionRes': ext_session_res
            }
            #return f(*args, **kwargs)
        except Exception as err:
            response.error = err
            response.message
            g.jwt = {
                'token': None,
                'sessionRes': response
            }

        return f(*args, **kwargs)

    
    return decorated