from flask import Blueprint, jsonify, request, g
from flasgger import Swagger
from flasgger.utils import swag_from
from library.verify_token import verify_token
from service.user_service import UserService
import traceback

user_api = Blueprint('user', __name__, url_prefix='/user')

user_svc = UserService()

@user_api.route('/register', methods=['POST'])
@swag_from('./swagger_ui/register.yml', methods=['POST'])
def register():
    #only used for req/response logging in UI
    req_id = None
    try:
        request_content = request.get_json()

        if 'requestId' in request_content:
            req_id = int(request_content['requestId'])

        response = user_svc.register(request_content)
        response.request_id = req_id
        
        if response.error:
            return jsonify(response.to_dict()), 500

        return jsonify(response.to_dict()), 200
    except Exception as err:
        return jsonify({
            'data': None,
            'message': 'Error attempting to register user.',
            'error': { 'message': repr(err), 'stackTrace': traceback.format_exc()},
            'authorized': None,
            'requestId': req_id
        }), 500

@user_api.route('/login', methods=['POST'])
@swag_from('./swagger_ui/login.yml', methods=['POST'])
def login():
    #only used for req/response logging in UI
    req_id = None
    try:
        request_content = request.get_json()

        if 'requestId' in request_content:
            req_id = int(request_content['requestId'])

        if not ('username' in request_content and 'password' in request_content):
            return jsonify({
                'data': None,
                'message': 'No username and/or password provided',
                'error': None,
                'authorized': None,
                'requestId': req_id
            }), 500

        req = {
            'username': request_content['username'],
            'pw': request_content['password']
        }

        response = user_svc.login(req)
        response.request_id = req_id
        
        if response.error:
            return jsonify(response.to_dict()), 500

        if response.data and response.authorized:
            return jsonify(response.to_dict()), 200

        return jsonify(response.to_dict()), 401

    except Exception as err:
        return jsonify({
            'data': None,
            'message': 'Error attempting to login user.',
            'error': { 'message': repr(err), 'stackTrace': traceback.format_exc()},
            'authorized': None,
            'requestId': req_id
        }), 500

@user_api.route('/verifyUserSession', methods=['GET'])
#this needs to go before the @swag_from() otherwise swagger page throws an error
@verify_token
@swag_from('./swagger_ui/verify_user_session.yml', methods=['GET'])
def verify_user_session():
    #only used for req/response logging in UI
    req_id = None
    try:
        request_content = request.get_json()

        if request_content and 'requestId' in request_content:
            req_id = int(request_content['requestId'])

        jwt = g.get('jwt', None)
        if not jwt['token']:
            if jwt['sessionRes'].authorized is not None and not jwt['sessionRes'].authorized:
                return jsonify(jwt['sessionRes'].to_dict()), 401
            
            return jsonify(jwt['sessionRes'].to_dict()), 500

        response = user_svc.get_user_from_session(jwt)
        response.request_id = req_id
        
        if response.error:
            return jsonify(response.to_dict()), 500

        return jsonify(response.to_dict()), 200
    except Exception as err:
        return jsonify({
            'data': None,
            'message': 'Error trying to verify user session.',
            'error': { 'message': repr(err), 'stackTrace': traceback.format_exc()},
            'authorized': None,
            'requestId': req_id
        }), 500