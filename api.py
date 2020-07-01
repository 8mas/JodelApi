import hashlib
import random
import time
import requests
import secrets
import hmac
import json


class API:
    debug = True
    instances = 0
    URL = "https://api.go-tellm.com"
    api_version = "0.2"

    # Android - found via reverse engineering
    secret = secrets.api_secret
    # Android - Does not really change?
    client_id_android = "81e8a76e-1e02-4d17-9ba0-8a7020261b26"

    # Version - secret is bound to this / see playstore for version
    version = "5.88.1"
    client_type = f"android_{version}"

    def __init__(self, latitude=53, longitude=9, iid=None, device_id=None, client_id=client_id_android, city="Hamburg",
                 country="DE", loc_accuracy=7.41, language="en-US", token=None):

        self.request_session = requests.session()
        self.request_session.verify = False

        # Use local proxy
        if API.debug:
            print("Using proxy")
            self.request_session.proxies.update({"http": "http://127.0.0.1:8888", "https": "https://127.0.0.1:8888", })

        # Randomize the position a bit (up to one km in each direction)
        lat_seed = float(random.randint(-100000, 100000)) / 10000000
        long_seed = float(random.randint(-100000, 100000)) / 10000000

        self.latitude = latitude + lat_seed
        self.longitude = longitude + long_seed

        self.city = city
        self.country = country
        self.loc_accuracy = loc_accuracy
        self.language = language
        self.client_id = client_id

        self.iid = iid
        if self.iid is None:
            self.iid = API._get_random_iid()

        self.device_id = device_id
        if self.device_id is None:
            self.device_id = API._get_random_device_id()

        self.access_token = token
        if self.access_token is None:
            self.access_token = self.get_access_token()

        API.instances += 1

    def get_access_token(self):
        # Get new access token
        # TODO: handling of renew token etc.
        payload = {
            "location": {
                "city": self.city,
                "country": self.country,
                "loc_coordinates": {
                    "lat": self.latitude,
                    "lng": self.longitude
                },
                "loc_accuracy": self.loc_accuracy
            },
            "iid": self.iid,
            "client_id": self.client_id,
            "device_uid": self.device_id,
            "language": self.language
        }
        json_string = json.dumps(payload)
        response = self._post("/api/v2/users", json_string)
        # Save response
        return response["access_token"]

    def get_posts(self, from_start=0, to_end=60, channel=None):
        api_version = "v3" if channel else "v3"
        feed = "channel" if channel else "location"

        params = {
            "channel": channel
        }

        resource = f"/api/{api_version}/posts/{feed}/combo"
        self._get(resource, params)

    def _generate_hmac(self, request_type, resource, timestamp, data: str):
        # This format is how jodel needs it. Some requests do not need a valid mac.
        payload = f"{request_type}%api.go-tellm.com%443%{resource}%%{self.latitude};{self.longitude}%{timestamp}%%{data}"

        auth_code = hmac.new(self.secret,
                             payload.encode("utf-8"),
                             hashlib.sha1).hexdigest().upper()
        return auth_code

    # Set headers for request
    def _prepare_request(self, request_type, resource, data):
        timestamp = API._get_timestamp()
        mac = self._generate_hmac(request_type, resource, timestamp, data)

        header_dict = {
            "X-Timestamp": timestamp,
            "X-Location": f"{self.latitude};{self.longitude}",
            "X-Authorization": f"HMAC {mac}",
            "X-Api-Version": API.api_version,
            "X-Client-Type": self.client_type,
            "User-Agent": f"Jodel/{self.version} (iPad; iOS 11.1; Scale/2.10)",
            "Content-Type": "application/json"
        }

        if self.access_token is not None:
            header_dict["Authorization"] = "Bearer " + self.access_token

        self.request_session.headers.update(header_dict)

    def _handle_response(self, response):
        response_dict = json.loads(response.content.decode())
        code = response.status_code
        if code == 477:
            raise SigningException(response_dict)

        return response_dict

    def _get(self, resource, params={}):
        url = API.URL + resource

        self._prepare_request("GET", resource, {})
        response = self.request_session.get(url, params=params)
        return self._handle_response(response)

    def _post(self, resource, payload: str):
        url = API.URL + resource

        self._prepare_request("POST", resource, payload)
        response = self.request_session.post(url, payload)
        return self._handle_response(response)

    def _put(self):
        pass

    def _delete(self):
        pass

    ########## Helper ##########
    # a bit sloppy but okay for now

    @staticmethod
    def _get_random_hex(n):
        return "".join([random.choice("0123456789ABCDEF") for x in range(n)]).lower()

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
        return "".join(
            [random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890" + extra_chars) for _ in
             range(n)])

    @staticmethod
    def _get_timestamp():
        return time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _log(self, msg):
        print("[%s]\n%s\n" % (time.strftime("%H:%M:%S"), msg.encode("utf-8")))


class SigningException(Exception):
    pass


if __name__ == "__main__":
    t = API()
    t.get_posts(channel="informatik")
