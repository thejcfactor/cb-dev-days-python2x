from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from .test_controller import test_api
from .user_controller import user_api

api = Flask('PYTHON_2X_API')

CORS(api, resources={r'/*': {'origins':'*'}})

api.config['SWAGGER']={
    'title':'Python 2.x API',
    'description': 'Python 2.x API for retailsample',
    'uiversion': 3,
    'openapi': '3.0.2',
    'components':{
        'securitySchemes':{
            'bearerAuth':{
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'in': 'header'
            }
        }
    }
}

# swagger_config = {
#     'openapi': "3.0.2",
#     'title': 'Python 2.x API',
#     'uiversion': 3,
#     'description': 'Temp description',
#     'headers': [],
#     'specs':[
#         {
#             'endpoint': 'apispec',
#             'route': '/apispec.json'
#         }
#     ],
#     'components':{
#         'securitySchemes':{
#             'BearerAuth':{
#                 'type': 'http',
#                 'scheme': 'bearer',
#                 'bearerFormat': 'JWT',
#                 'in': 'header'
#             }
#         }
#     }
# }

api.register_blueprint(test_api)
api.register_blueprint(user_api)

#swag = Swagger(api, config=swagger_config)
swag = Swagger(api)

@api.route('/', methods=['GET', 'POST'])
def default():
    return jsonify('Python 2.x API default route.')

