import hashlib
import random
import time
import requests
import secrets
import hmac


class API:
    debug = True
    instances = 0
    api_version = '0.2'

    # Android - found via reverse engineering
    secret = secrets.api_secret
    # Android - Does not really change?
    client_id_android = "81e8a76e-1e02-4d17-9ba0-8a7020261b26"

    # Version - secret is bound to this / see playstore for version
    client_type = 'android_5.88.1'

    def __init__(self, latitude=53, longitude=9, iid=None, device_id=None, client_id=client_id_android, city="Hamburg",
                 country="DE", loc_accuracy="5.14", language="en-US", token=None):

        self.request_session = requests.session()
        self.request_session.verify = False

        # Use local proxy
        if API.debug:
            print("Using proxy")
            self.request_session.proxies.update({'http': 'http://127.0.0.1:8888', 'https': 'https://127.0.0.1:8888', })

        # Randomize the position a bit (up to one km in each direction)
        lat_seed = float(random.randint(-100000, 100000)) / 10000000
        long_seed = float(random.randint(-100000, 100000)) / 10000000

        self.latitude = str(latitude + lat_seed)
        self.longitude = str(longitude + long_seed)

        self.city = city
        self.country = country
        self.loc_accuracy = loc_accuracy
        self.language = language
        self.client_id = client_id

        if iid is None:
            self.iid = API._get_random_iid()
        if device_id is None:
            self.device_id = API._get_random_device_id()
        if token is None:
            pass
            # TODO generate new user

        self.access_token = token
        API.instances += 1

    def get_access_token(self):
        payload = {
            "location": {
                "city": self.city,
                "country": self.country,
                "loc_coordinates": {
                    "lat": self.latitude,
                    "lon": self.longitude
                },
                "loc_accuracy": self.loc_accuracy
            },
            "iid": self.iid,
            "client_id": self.client_id,
            "device_uid": self.device_id,
            "language": self.language
        }

    def _generate_hmac(self, type, url, timestamp, data):
        resource_with_parameters = url.split("https://api.go-tellm.com")[1]
        resource = resource_with_parameters.split("?")[0]

        # This format is how jodel needs it. Some requests do not need a valid mac.
        payload = f"{type}%api.go-tellm.com%443%{resource}%%{self.latitude};{self.longitude}%{timestamp}%%{data}"

        auth_code = hmac.new(self.secret,
                             payload.encode("utf-8"),
                             hashlib.sha1).hexdigest().upper()
        return auth_code

    def _get(self, url, **kwargs):
        pass

    def _post(self):
        pass

    def _put(self):
        pass

    def _delete(self):
        pass

    ########## Helper ##########
    # a bit sloppy but okay for now

    @staticmethod
    def _get_random_hex(n):
        return ''.join([random.choice('0123456789ABCDEF') for x in range(n)]).lower()

    @staticmethod
    def _get_random_device_id():
        plainUID = API._get_random_hex(40)
        return hashlib.sha256(plainUID.encode()).hexdigest()

    @staticmethod
    def _get_random_iid():
        # Seems to be an ad id?
        first_part = API._get_random_AZaz09(11) + ":APA91b"
        second_part = API._get_random_AZaz09(134, "_-")
        return first_part + second_part

    @staticmethod
    def _get_random_AZaz09(n, extra_chars=""):
        return ''.join(
            [random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890' + extra_chars) for _ in
             range(n)])

    def _log(self, msg):
        print('[%s]\n%s\n' % (time.strftime('%H:%M:%S'), msg.encode('utf-8')))
