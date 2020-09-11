from controllers.main_controller import api

#gunicorn -b 0.0.0.0:8000 app
#will work with below line, it is looking for "application"
application = api
#gunicorn -b 0.0.0.0:8000 app:service
#with below line need to tell gunicorn what to use for application
#service = service
if __name__ == '__main__':
    application.run()