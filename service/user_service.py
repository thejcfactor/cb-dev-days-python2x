import bcrypt
import jwt
import traceback

from repository.repository import Repository
from configuration.config import get_secret, get_ttl
from library.response import Response

class UserService(object):

    def __init__(self):
        self.repository = Repository()

    """
        exposed methods
    """

    def register(self, req):
        req['password'] = bcrypt.hashpw(str.encode(req['password']),bcrypt.gensalt()).decode()
        response = Response(None, 'Operation not built yet.', None, None)
        result = self.repository.create_account(req)
        if 'error' in result:
            response.error = result['error']
            response.message = 'Error registering customer/user.'
        else:
            if result == 'NOP':
                return response
            response.data = result['acct']
            response.message = 'Successfully registered customer/user.'

        return response

    def login(self, req):
        valid_user_res = self.verify_user(req['username'], str.encode(req['pw']))
        if valid_user_res.error or 'Operation not' in valid_user_res.message:
            return valid_user_res

        response = Response(None, 'Operation not built yet.', None, None)
        
        if not valid_user_res.data:
            response.message = 'Invalid user.  Check username and password.'
            response.authorized = False
            return response
        
        key = 'customer_{0}'.format(valid_user_res.data['custId'])
        customer_info = self.repository.get_object_by_key(key)

        session_res = self.create_session(req['username'])

        if session_res.error:
            return session_res
            
        secret = get_secret()
        encoded_jwt = jwt.encode({'id': session_res.data}, secret, algorithm='HS256')
        response.data = {
            'userInfo':{
                'userId': valid_user_res.data['userId'],
                'username': valid_user_res.data['username'],
                'token': encoded_jwt.decode()
            },
            'customerInfo':customer_info
        }
        response.message = 'Successfully logged in (session created).'
        response.authorized = True

        return response

    def get_user_from_session(self, jwt):
        valid_user_res = self.verify_user(jwt['sessionRes'].data['username'], None, True)
        if valid_user_res.error or 'Operation not' in valid_user_res.message:
            return valid_user_res

        response = Response(None, 'Operation not built yet.', None, None)
        
        if not valid_user_res.data:
            response.message = 'Invalid user.  Check username and password.'
            response.authorized = False
            return response

        response.data = {
            'userInfo':{
                'userId': valid_user_res.data['userId'],
                'username': valid_user_res.data['username'],
                'token': jwt['token']
            }
        }
        response.message = 'Successfully verified and extended session.'
        response.authorized = True

        return response

    """
    Private methods
    """
    
    def create_session(self, username):
        response = Response(None, 'Operation not built yet.', None, None)

        expiry = int(get_ttl())
        session = self.repository.create_session(username, expiry)

        if 'error' in session:
            response.message = 'Error creating session.'
            response.error = session['error']
            return response
        
        if 'sessionId' in session:
            response.data = session['sessionId']
            response.message = 'Session created.'

        return response

    def extend_session(self, token):
        secret = get_secret()
        response = Response(None, 'Operation not built yet.', None, None)
        decoded = None
        try:
            decoded_jwt = jwt.decode(token, secret, algorithms=['HS256'])
        except Exception as ex:
            print(ex)
            response.message = 'Error extending session.  Invalid token.'
            response.error = ex
            return response
        
        expiry = int(get_ttl())
        session = self.repository.extend_session(decoded_jwt['id'], expiry)
        if 'error' in session:
            if session['error'].CODE == 13:
                response.message = 'Unauthorizeed.  Session expired'
                response.authorized = False
            else:
                response.message = "Error trying to verify session."
            
            response.error = {
                'message': repr(session['error']),
                'stackTrace': traceback.format_exc()
            }
            return response

        if session == 'NOP':
            return response
        
        response.data = session
        response.message = 'Successfully extended session.'
        response.authorized = True
        return response

    def verify_user(self, username, pw, jwt=None):
        result = self.repository.get_user_info(username)
        response = Response(None, 'Operation not built yet.', None, None)
        if 'error' in result:
            response.error = result['error']
            response.message = 'Could not find user.'
            return response
        
        if result == 'NOP':
            return response
        
        #no password when using JWT, if user is found, consider valid
        if jwt:
            response.data = result['user_info']
            response.message = 'JWT - no password verification needed.'
            return response
        
        if bcrypt.checkpw(pw, str.encode(result['user_info']['password'])):
            response.data = result['user_info']
            response.message = 'Password verified.'

        return response

    def create_user(self, req):
        pw = bcrypt.hashpw(req['password'], bcrypt.gensalt())
        self.repository.create_user(req['username'],pw.decode())

