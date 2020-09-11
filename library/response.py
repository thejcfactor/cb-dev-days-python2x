class Response(object):
    def __init__(self, data=None, msg=None, error=None, auth=None, req_id=None):
        self.data = data
        self.message = msg
        self.error = error
        self.authorized = auth
        self.request_id = req_id

    def to_dict(self):
        return {
            'data': self.data,
            'message':self.message,
            'error':self.error,
            'authorized':self.authorized,
            'requestId':self.request_id
        }

    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self, value):
        self.__data = value

    @property
    def message(self):
        return self.__message
    
    @message.setter
    def message(self, value):
        self.__message = value

    @property
    def error(self):
        return self.__error
    
    @error.setter
    def error(self, value):
        self.__error = value

    @property
    def authorized(self):
        return self.__authorized
    
    @authorized.setter
    def authorized(self, value):
        self.__authorized = value

    @property
    def request_id(self):
        return self.__request_id
    
    @request_id.setter
    def request_id(self, value):
        self.__request_id = value