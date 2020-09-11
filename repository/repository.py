import os
import datetime
import uuid
import traceback

from configuration.config import get_db_config

from couchbase.cluster import Cluster, PasswordAuthenticator
from couchbase.bucket import Bucket
from couchbase.n1ql import N1QLQuery
from couchbase.exceptions import CouchbaseError


class Repository(object):
    __instance = None
    host = ''
    bucket_name = ''
    username = ''
    password = ''

    __cluster = None
    __bucket = None

    # Singleton pattern - only 1 CB instance / bucket
    def __new__(cls):
        if Repository.__instance is None:

            Repository.__instance = object.__new__(cls)
            db_config = get_db_config()
            Repository.__instance.host = db_config['host']
            Repository.__instance.bucket_name = db_config['bucket']
            Repository.__instance.username = db_config['username']
            Repository.__instance.password = db_config['password']
            Repository.__instance.connect()
        return Repository.__instance

    def connect(self):
        connection_str = 'couchbase://{0}'.format(self.host)

        try:
            self.__cluster = Cluster(connection_str)
            authenticator = PasswordAuthenticator(self.username, self.password)
            self.__cluster.authenticate(authenticator)

            self.__bucket = self.__cluster.open_bucket(self.bucket_name)
            print('connected')
            print(self.__bucket)
        except Exception as error:
            print('Could not open bucket: {0}.  Error: {1}'.format(
                self.bucket_name, error))
            raise

        self.connected = True
        return self.connected

    def create_account(self, user_info):
        try:
            customer_doc = self.get_new_customer_document(user_info)
            saved_customer = self.__bucket.insert(
                customer_doc['_id'], customer_doc)
            if not saved_customer:
                return None

            user_doc = self.get_new_user_document(user_info)
            saved_user = self.__bucket.insert(user_doc['_id'], user_doc)
            if not saved_user:
                return None

            user_doc['password'] = None

            return {'acct': {
                'customerInfo': customer_doc,
                'userInfo': user_doc
            }}

        except Exception as err:
            # TODO - consistent output message
            print(err)
            return {'error': {
                'message': repr(err),
                'stackTrace': traceback.format_exc()
            }}

    def get_user_info(self, username):
        try:
            sql = """
            SELECT c.custId, u.userId, u.username, u.`password`
            FROM `{0}` u
            JOIN `{0}` c ON c.username = u.username AND c.doc.type = 'customer'
            WHERE u.docType ='user' AND u.username = $1
            ORDER BY u.userId DESC
            LIMIT 1;
            """.format(self.bucket_name)

            params = [username]
            n1ql = N1QLQuery(sql, *params)

            result = self.__bucket.n1ql_query(n1ql).get_single_result()

            return {'user_info': result if result else None }

        except Exception as err:
            # TODO - consistent output message
            print(err)
            return {'error': {
                'message': repr(err),
                'stackTrace': traceback.format_exc()
            }}

    def create_session(self, username, expiry):
        try:
            session = {
                'sessionId': str(uuid.uuid4()),
                'username': username,
                'docType': 'SESSION'
            }

            key = 'session::{0}'.format(session['sessionId'])
            result = self.__bucket.insert(key, session, ttl=expiry)
            return { 'sessionId': session['sessionId'] if result else None }
        except Exception as err:
            # TODO - consistent output message
            print(err)
            return {'error': {
                'message': repr(err),
                'stackTrace': traceback.format_exc()
            }}

    def extend_session(self, sessionId, expiry):
        try:
            key = 'session::{0}'.format(sessionId)
            result = self.__bucket.get(key, ttl=expiry)
            return result.value if result else None
        except CouchbaseError as error:
            print(error)
            return {'error': error}

    # helper methods

    def get_new_customer_document(self, user_info):
        cust_id = self.get_last_customer_id()
        key = 'customer_{0}'.format(cust_id + 1)
        now = datetime.datetime.now()
        timestamp = int(now.timestamp())
        return {
            'doc': {
                'type': 'customer',
                'schema': '1.0.0.0',
                'created': timestamp,
                'createdBy': 1234
            },
            '_id': key,
            'custId': cust_id + 1,
            'custName': {
                'firstName': user_info['firstName'],
                'lastName': user_info['lastName'],
            },
            'username': user_info['username'],
            'email': user_info['email'],
            'createdOn': '{0:%Y-%m-%d}'.format(now),
            'address': {
                'home': {
                    'address1': '1234 Main St',
                    'city': 'Some City',
                    'state': 'TX',
                    'zipCode': '12345',
                    'country': 'US',
                },
                'work': {
                    'address1': '1234 Main St',
                    'city': 'Some City',
                    'state': 'TX',
                    'zipCode': '12345',
                    'country': 'US',
                }
            },
            'mainPhone': {
                'phone_number': '1234567891',
                'extension': '1234'
            },
            'additionalPhones': {
                'type': 'work',
                'phone_number': '1234567891',
                'extension': '1234'
            }
        }

    def get_new_user_document(self, user_info):
        user_id = self.get_last_user_id()
        key = 'user_{0}'.format(user_id + 1)

        return {
            'docType': 'user',
            '_id': key,
            'userId': user_id + 1,
            'username': user_info['username'],
            'password': user_info['password']
        }

    def get_last_customer_id(self):
        sql = """
        SELECT c.custId
        FROM `{0}` c
        WHERE c.doc.`type` ='customer'
        ORDER BY c.custId DESC
        LIMIT 1;
        """.format(self.bucket_name)

        n1ql = N1QLQuery(sql)

        result = self.__bucket.n1ql_query(n1ql).get_single_result()
        if result:
            return int(result['custId'])

        return 0

    def get_last_user_id(self):
        sql = """
        SELECT u.userId
        FROM `{0}` u
        WHERE u.docType ='user'
        ORDER BY u.userId DESC
        LIMIT 1;
        """.format(self.bucket_name)

        n1ql = N1QLQuery(sql)

        result = self.__bucket.n1ql_query(n1ql).get_single_result()
        if result:
            return int(result['userId'])

        return 0

    def get_objects(self, query):
        n1ql = N1QLQuery(query)
        query_result = self.__bucket.n1ql_query(n1ql)
        results = []
        for result in query_result:
            results.append(result)

        return results

    def get_object_by_key(self, key):
        try:
            result = self.__bucket.get(key)
            return result.value
        except Exception as err:
            # TODO - consistent output message
            print(err)
            return {'error': {
                'message': repr(err),
                'stackTrace': traceback.format_exc()
            }}

    def get_objects_by_keys(self, keys):
        results = []
        for key, result in self.__bucket.get_multi(keys).items():
            # results.append({
            #     'id': key,
            #     'doc': result.value
            # })
            results.append(result.value)

        return results
