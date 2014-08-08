from requests_oauthlib import OAuth1Session
import requests
import datetime
import time
import uuid
import json

# Parse Application IDs
PARSE_PRODUCTION_APPLICATION_ID = 'b6vDzZbjG6f3XfqpskLfv5em3TrLF2qWTBztBHGC'
PARSE_DEVELOPMENT_APPLICATION_ID = 'ccqDgJUh6tpBXIVRRFMjR2Rh4uyvNi80jR1gH0ed'
PARSE_DEVELOPMENT_WILL_APPLICATION_ID = 'T89Z0xGkb69FtbxVFX06voxi4EveWZlWoAqK8uA6'
PARSE_DEVELOPMENT_ROCKY_APPLICATION_ID = 'JOa4BXEsmvlI7f4v332dK46JgTPfKU17cLerKncN'
PARSE_LOAD_DEVELOPMENT_APPLICATION_ID = 'oYf0vSys1RwtIgJAbYDBnM8PTsc01tUW1ENNOp2o'
PARSE_STUDY_APPLICATION_ID = 'qQ7tZHQbZnurNCkru6hefhl3UeJBJUCpGJ2DyqjR'

# Parse Client Keys
PARSE_PRODUCTION_CLIENT_KEY = 'vEDTcLLnUPgPMHkYkLvrzvcPLOj6xBCtSrX27o43'
PARSE_DEVELOPMENT_CLIENT_KEY = 'OCdjam6QvtX6WRazHrMdPZC1X2dIko8SNp55roRK'
PARSE_DEVELOPMENT_WILL_CLIENT_KEY = 'GOdWzpdjgTcPoVqpk4Uq2oJswrIqf4O1y0vo5ZXR'
PARSE_DEVELOPMENT_ROCKY_CLIENT_KEY = 'XIYun0dSwUUSn6qQsrIo4UuGNgeMHXJ2zYNno3dS'
PARSE_LOAD_DEVELOPMENT_CLIENT_KEY = '039Sz0OHVcbgwPdjmfdLDzLMLx0ZuyBEK23iSMu7'
PARSE_STUDY_CLIENT_KEY = 'k6VsPFT8ymTPeNugQHT8icyZQKv7oDRXiafzbpoy'

# AWS
AWS_BASE_URI = 'https://s3.amazonaws.com/files.sling.me/'
AWS_ACCESS_KEY_ID = 'AKIAJDWK6AQDTVGXOZMQ'

PARSE_BASE_URI = 'https://api.parse.com/2/'
VERSION = 'i1.2.19'
LOCALE = 'en_US'
COUNTRY_CODE = '+1'
IID = str(uuid.uuid4())
CLIENT_ID = str(uuid.uuid4())
UUID = str(uuid.uuid4())

#req = parse.post(PARSE_BASE_URI + '/client_function', data)

class SlingShot():
    def __init__(self, client_key, client_secret):
        # Parse Session
        self.cookie = ''
        self.client_key = client_key
        self.client_secret = client_secret
        self.parse = OAuth1Session(client_key=self.client_key, client_secret=self.client_secret)
        self.session_token = ''
        # User / Device
        self.user_id = ''
        self.device_id = ''
        # AWS (Uploads)
        self.name = ''
        self.url = ''
        self.acl = ''
        self.key = ''
        self.policy = ''
        self.signature = ''

    def send_request(self, endpoint, data):
        # Request
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        cookies = {'_parse_session': self.cookie}
        url = PARSE_BASE_URI + endpoint
        print(url)

        req = self.parse.post(url, data=json.dumps(data), headers=headers, cookies=cookies)

        # Response
        cookie = req.cookies.get('_parse_session', None)
        if cookie is not None:
            self.cookie = cookie

        if 'sessionToken' in req.text:
            self.session_token = req.json()['sessionToken']

        #if endpoint is 'client_me' and 'objectId' in req.text:
        if endpoint is 'client_me' and req.status_code is requests.codes.ok:
            self.user_id = req.json()['result']['data']['objectId']

        if endpoint is 'upload_file' and req.status_code is requests.codes.ok:
            self.name = req.json()['result']['name']
            self.url = req.json()['result']['url']
            self.acl = req.json()['result']['post_params']['acl']
            self.key = req.json()['result']['post_params']['key']
            self.policy = req.json()['result']['post_params']['policy']
            self.signature = req.json()['result']['post_params']['signature']

        return req

    def get_config(self):
        data = {'data': {},
                'function': 'getConfig',
                'uuid': UUID,
                'iid': IID,
                'v': VERSION}

        return self.send_request('client_function', data)

    def get_authenticated_config(self):
        data = {'data': {},
                'function': 'getAuthenticatedConfig',
                'uuid': UUID,
                'iid': IID,
                'v': VERSION}

        return self.send_request('client_function', data)

    def request_authentication(self, phone_number):
        data = {'data': {'locale': LOCALE,
                         'phoneNumber': COUNTRY_CODE + phone_number },
                'uuid': UUID,
                'function': 'v3_requestAuthentication',
                'v': VERSION,
                'iid': IID}

        return self.send_request('client_function', data)


    def confirm_authentication(self, phone_number, confirmation_code):
        data = {'data': {'confirmationCode': confirmation_code,
                        'phoneNumber': COUNTRY_CODE + phone_number},
                'function': 'confirmAuthentication',
                'uuid': UUID,
                'iid': IID,
                'v': VERSION}

        return self.send_request('client_function', data)

    def me(self):
        data = {'session_token': self.session_token,
                'uuid': UUID,
                'iid': IID,
                'v': VERSION}

        return self.send_request('client_me', data)

    def get_users(self):
        data = {'data': {},
                'function': 'v5_getUsers',
                'session_token': self.session_token,
                'uuid': UUID,
                'iid': IID,
                'v': VERSION}
        
        return self.send_request('client_function', data)

    def find_contacts(self, phone_numbers):
        data = {'phoneNumbers': phone_numbers,
                'function': 'v2_findContacts',
                'session_token': self.session_token,
                'uuid': UUID,
                'iid': IID,
                'v': VERSION}

        return self.send_request('client_function', data)

    def upload_file(self):
        data = {'name': 'photo.jpg',
                'session_token': self.session_token,
                'uuid': UUID,
                'IID': IID,
                'v': VERSION}

        return self.send_request('upload_file', data)

    def save_in_background(self, directory):
        data = {'Content-Type': 'image/jpeg',
                'AWSAccessKeyId': AWS_ACCESS_KEY_ID,
                'acl': self.acl,
                'key': self.key,
                'policy': self.policy,
                'signature': self.signature}
        files = {'file': open(directory, 'rb')}
        print(data)

        return requests.post(AWS_BASE_URI, data=data, files=files)

    def save_shot(self, thumbnail, recipients, **kwargs):
        data = {'data': {
                        # Recipients
                        'recipientIds': recipients,
                        # Media Sources
                        'media': {'__type': 'File',
                                    'name': self.name,
                                    'url': self.url},
                        'thumbnail': {'__type': 'Bytes',
                                        'base64': thumbnail},
                        # Media Info
                        # Time
                        'capturedAt': {'__type': 'Date',
                                        'iso': str(datetime.datetime.now())},
                        'timeZoneOffsetMillis': kwargs.get('offset', 0),
                        # Location
                        'location': {'__type': 'GeoPoint',
                                    'latitude': kwargs.get('latitude', -122.148548),
                                    'longitude': kwargs.get('longitude', 37.484716)},
                        'locationText': kwargs.get('location', 'Facebook HQ'),
                        # Caption
                        'caption': kwargs.get('caption', ''),
                        'captionYPosition': kwargs.get('caption_y_pos', 0),
                        # Drawing
                        'drawing': kwargs.get('drawing', False),
                        # Misc.
                        'selfie': kwargs.get('selfie', True),
                        'mediaMirror': kwargs.get('mirror', False),
                        'mediaOrientation': kwargs.get('orientation', 270),
                        'mediaSize': kwargs.get('size', 103099),
                        'mediaType': kwargs.get('type', 'photo')},
                'function': 'saveShot',
                'session_token': self.session_token,
                'uuid': UUID,
                'iid': IID,
                'v': VERSION}
        print(data)

        return self.send_request('client_function', data)



ss = SlingShot(PARSE_PRODUCTION_APPLICATION_ID, PARSE_PRODUCTION_CLIENT_KEY)

# Pre-Login

# Login
'''
print('GET_CONFIG')
config = ss.get_config()
print(config.text)

print('\nGET_AUTHENTICATED_CONFIG')
authconfig = ss.get_authenticated_config()
print(authconfig.text)

print('\nREQUEST_AUTHENTICATION')
request_auth = ss.request_authentication('2145374007')
print(request_auth.text)

print('\nCONFIRM_AUTHENTICATION')
confirm_auth = ss.confirm_authentication('2145374007', '515316')
print(confirm_auth.text)
print(confirm_auth.request.body)
'''

# Post-Login
print('\nME')
me = ss.me()
print(me.text)

print('\nGET_USERS')
users = ss.get_users()
print(users.text.encode('utf-8'))

print('\nCREATE_INSTALLATION')
create = ss.create_installation(True)
print(create.text)

print('\nFIND_CONTACTS')
contacts = ss.find_contacts(['+12145374007', '+12145474007', '+16507967674'])
print(contacts.text)
'''

'''
print('\nUPLOAD_FILE')
request_upload = ss.upload_file()
print(request_upload.text)

print('\nSAVE_IN_BACKGROUND')
upload = ss.save_in_background('test.jpg')
print(upload.text)

thumbnail = "/9j/4AAQSkZJRgABAQAAAQABAAD/4QBYRXhpZgAATU0AKgAAAAgAAgESAAMAAAABAAEAAIdpAAQAAAABAAAAJgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAACaADAAQAAAABAAAAEAAAAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAQAAkDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCLX7B4ZHVmXPsa5/yR6y/r/hWf4b1CUPfWiPdyWjvugeUYDKSTjn6AnkjP456DzbP/AJ/7P/wKT/4qvLq6TaO7Q//Z"
print('\nSAVE_SHOT')
send = ss.save_shot(thumbnail, [ss.user_id])
print(send.text)