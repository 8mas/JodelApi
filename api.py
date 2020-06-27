import hashlib
import random
import time
import requests
import secrets


class API:
    debug = True
    instances = 0
    api_version = '0.2'

    # Android - found via reverse engineering
    secret = secrets.api_secret
    # Android - Does not really change?
    clientID = "81e8a76e-1e02-4d17-9ba0-8a7020261b26"

    # Version - secret is bound to this / see playstore for version
    client_type = 'android_5.88.1'

    def __init__(self, latitude=53, longitude=9, device_id=0, token=0):
        self.request_session = requests.session()
        self.request_session.verify = False

        # Use local proxy
        if API.debug:
            print("Using proxy")
            self.request_session.proxies.update({'http': 'http://127.0.0.1:8888', 'https': 'https://127.0.0.1:8888', })

        # Randomize the position a bit (up to one km in each direction)
        latseed = float(random.randint(-100000, 100000)) / 10000000
        longseed = float(random.randint(-100000, 100000)) / 10000000

        self.latitude = str(latitude + latseed)
        self.longitude = str(longitude + longseed)

        if device_id == 0:
            device_id = self.get_random_device_id()

        self.device_uid = device_id
        self.iid = self.get_random_iid()
        self.client_id = self.clientID

        if token == 0:
            pass
            # TODO generate new user

        # Token der bei jeden request benutzt wird.
        self.access_token = token
        API.instances += 1

    ########## Helper ##########
    # a bit sloppy but okay for now
    def get_random_device_id(self):
        plainUID = self.get_random_hex(40)
        return hashlib.sha256(plainUID.encode()).hexdigest()

    # Seems to be an ad id?
    def get_random_iid(self):
        first_part = self.get_random_AZaz09(11) + ":APA91b"
        second_part = self.get_random_AZaz09(134, "_-")
        return first_part + second_part

    def get_random_hex(self, n):
        return ''.join([random.choice('0123456789ABCDEF') for x in range(n)]).lower()

    def get_random_AZaz09(self, n, extra_chars=""):
        return ''.join(
            [random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890' + extra_chars) for _ in
             range(n)])

    def log(self, msg):
        print('[%s]\n%s\n' % (time.strftime('%H:%M:%S'), msg.encode('utf-8')))
