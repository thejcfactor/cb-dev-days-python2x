from flask import Blueprint, jsonify, request, g
import yaml
from flasgger import Swagger
from flasgger.utils import swag_from
#from functools import wraps
from library.verify_token import verify_token

from configuration.config import get_secret
from service.user_service import UserService

test_api = Blueprint('test', __name__, url_prefix='/test')

user_svc = UserService()

@test_api.route('/ping', methods=['GET'])
@swag_from('./swagger_ui/ping.yml', methods=['GET'])
#@swag_from('/swagger_ui/ping.yml', methods=['GET'])
def ping():
    return jsonify(
        {
            'data': None,
            'message': 'test api:  pong!',
            'error': None,
            'authorized': None
        }
    )

@test_api.route('/authorizedPing', methods=['GET'])
#this needs to go before the @swag_from() otherwise swagger page throws some errors
@verify_token
@swag_from('./swagger_ui/authorized_ping.yml', methods=['GET'])
def authorized_ping():
    jwt = g.get('jwt', None)
    if jwt:
        print(jwt)
    return jsonify(
        {
            'data': None,
            'message': 'test api:  pong!',
            'error': None,
            'authorized': None
        }
    )

@test_api.route('/createUser', methods=['POST'])
@swag_from('./swagger_ui/create_user.yml', methods=['POST'])
def create_user():
    request_args = request.args
    print(request_args)

    if 'username' not in request_args or 'password' not in request_args:
        return jsonify(
            {
                'data': None,
                'message': 'No username and/or password provided.',
                'error': None,
                'authorized': None
            }
        )
    req = {
        'username': request_args.get('username'),
        'pw': str.encode(request_args.get('password'))
    }
    user_svc.create_user(req)
    return jsonify("ok!"), 200

@test_api.route('/login', methods=['GET'])
@swag_from('./swagger_ui/test_login.yml', methods=['GET'])
def login():
    request_args = request.args

    if 'username' not in request_args or 'password' not in request_args:
        return jsonify(
            {
                'data': None,
                'message': 'No username and/or password provided.',
                'error': None,
                'authorized': None
            }
        )

    req = {
        'username': request_args.get('username'),
        'password': str.encode(request_args.get('password'))
    }

    response = user_svc.login(req)

    if response:
        return jsonify(
            {
                'data': response,
                'message': 'Successfully logged in.',
                'error': None,
                'authorized': True
            }
        ), 200
    else:
        return jsonify("not ok!"), 200

    
    