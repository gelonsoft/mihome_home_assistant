import logging
import base64
import datetime
import hashlib
import hmac
import json
import os
import time
import requests
import random
import yaml
from Crypto.Hash import MD5,SHA256,SHA1
import pickle
import gzip


class RC4Coder:
    def __init__(self, key):
        self.logger = logging.getLogger('gelonsoft.mihome.RC4Coder')
        self.S = list(range(256))
        x = 0
        for i in range(256):
            x = (x + key[i % len(key)] + self.S[i]) % 256
            self.S[i], self.S[x] = self.S[x], self.S[i]
        self.m = 0
        self.j = 0
        # 1024 fake rounds
        for x in range(1024):
            self.m = (self.m + 1) % 256
            self.j = (self.j + self.S[self.m]) % 256
            self.S[self.m], self.S[self.j] = self.S[self.j], self.S[self.m]

    def rc4mi(self, data):
        out = []
        for ch in data:
            self.m = (self.m + 1) % 256
            self.j = (self.j + self.S[self.m]) % 256
            self.S[self.m], self.S[self.j] = self.S[self.j], self.S[self.m]
            x = (ch ^ self.S[(self.S[self.m] + self.S[self.j]) % 256]) % 256
            out.append(x)
        return bytes(out)

    @staticmethod
    def rc4mi_once(data, key):
        coder = RC4Coder(key)
        return coder.rc4mi(data)


class XiaomiCloudConnector:

    def __init__(self, name, username, password, config_directory):
        self.name = name.replace('/', '')
        self.logger = logging.getLogger('gelonsoft.mihome.XiaomiCloudConnector')
        self._username = username
        self._password = password
        self._session = requests.session()
        self._config_path = config_directory + name
        self.load_from_yaml(self._config_path)
        self._last_login_time = None
        self._min_seconds_between_login = 30
        self._state = 0
        if not self._auth_data["logged_in"]:
            self.login()

    def can_login_again(self):
        if not (self._last_login_time is None):
            seconds = (datetime.datetime.now() - self._last_login_time).total_seconds()
            if seconds < self._min_seconds_between_login:
                self.logger.warning("Too many login calls. %s seconds < Min %s seconds", seconds,
                                    self._min_seconds_between_login)
                return False
        return True

    def save_to_yaml(self):
        with open(self._config_path + "-auth.yaml", 'w') as file:
            yaml.dump(self._auth_data, file)
        with open(self._config_path + ".cookies", 'wb') as file:
            pickle.dump(self._session.cookies, file)

    def reinit_auth_data(self):
        self.logger.info("Reinit auth data")
        self._session = requests.session()
        self._location = None
        self._auth_data = {
            "agent": self.generate_agent(),
            "device_id": self.generate_device_id(),
            "sign": None,
            "ssecurity": None,
            "cUserId": None,
            "userId": None,
            "serviceToken": None,
            "logged_in": False
        }
        if os.path.exists(self._config_path + "-auth.yaml"):
            try:
                os.remove(self._config_path + "-auth.yaml")
            except OSError as e:  # name the Exception `e`
                self.logger.error("Failed removing config %s: %s", self._config_path + "-auth.yaml",
                                  e.strerror)  # look what it says
        if os.path.exists(self._config_path + ".cookies"):
            try:
                os.remove(self._config_path + ".cookies")
            except OSError as e:  # name the Exception `e`
                self.logger.error("Failed removing cookies file %s: %s", self._config_path + ".cookies", e.strerror)

    def load_from_yaml(self, path):
        if (os.path.exists(path + "-auth.yaml")):
            with open(path+ "-auth.yaml", 'r') as file:
                self._auth_data = yaml.safe_load(file)
                if not self._auth_data:
                    self.reinit_auth_data()
            if (os.path.exists(path + ".cookies")):
                with open(path + ".cookies", 'rb') as file:
                    self._session.cookies.update(pickle.load(file))
        else:
            self.reinit_auth_data()

    @property
    def logged_in(self):
        return self._auth_data["logged_in"]

    def login_step_1(self):
        self.logger.debug("login_step_1")
        url = "https://account.xiaomi.com/pass/serviceLogin?sid=xiaomiio&_json=true"
        headers = {
            "User-Agent": self._auth_data["agent"],
            "Content-Type": "application/x-www-form-urlencoded"
        }
        cookies = {
            "userId": self._username
        }
        response = self._session.get(url, headers=headers, cookies=cookies)
        valid = response.status_code == 200 and "_sign" in self.to_json(response.text)
        if valid:
            self._auth_data["sign"] = self.to_json(response.text)["_sign"]
        return valid

    def login_step_2(self):
        self.logger.debug("login_step_2")
        url = "https://account.xiaomi.com/pass/serviceLoginAuth2"
        headers = {
            "User-Agent": self._auth_data["agent"],
            "Content-Type": "application/x-www-form-urlencoded"
        }
        fields = {
            "sid": "xiaomiio",
            "hash": (MD5.new(str.encode(self._password)).hexdigest() + "").upper(),
            "callback": "https://sts.api.io.mi.com/sts",
            "qs": "%3Fsid%3Dxiaomiio%26_json%3Dtrue",
            "user": self._username,
            "_sign": self._auth_data["sign"],
            "_json": "true"
        }
        response = self._session.post(url, headers=headers, params=fields)
        valid = response.status_code == 200 and "ssecurity" in self.to_json(response.text)
        if valid:
            json_resp = self.to_json(response.text)
            self._auth_data["ssecurity"] = json_resp["ssecurity"]
            self._auth_data["userId"] = json_resp["userId"]
            self._auth_data["cUserId"] = json_resp["cUserId"]
            # self._auth_data["passToken"] = json_resp["passToken"]
            self._location = json_resp["location"]
            # self._auth_data["code"] = json_resp["code"]
        return valid

    def login_step_3(self):
        self.logger.debug("login_step_3")
        headers = {
            "User-Agent": self._auth_data["agent"],
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = self._session.get(self._location, headers=headers)
        if response.status_code == 200:
            self._auth_data["serviceToken"] = response.cookies.get("serviceToken")
        return response.status_code == 200

    def login(self):
        self.reinit_auth_data()
        self.logger.info("Logging into Xiaomi...")
        self._last_login_time = datetime.datetime.now()
        self._session.cookies.set("sdkVersion", "accountsdk-18.8.15", domain="mi.com")
        self._session.cookies.set("sdkVersion", "accountsdk-18.8.15", domain="xiaomi.com")
        self._session.cookies.set("deviceId", self._auth_data["device_id"], domain="mi.com")
        self._session.cookies.set("deviceId", self._auth_data["device_id"], domain="xiaomi.com")

        if self.login_step_1():
            if self.login_step_2():
                if self.login_step_3():
                    self._auth_data["logged_in"] = True
                    self.save_to_yaml()
                    self.logger.info("Log in success")
                    return True
                else:
                    self.logger.warning("Unable to get service token during Xiaomi login")
            else:
                self.logger.error("Invalid login or password during Xiaomi login")
        else:
            self.logger.error("Invalid username during Xiaomi login")
        self._auth_data["logged_in"] = False
        return False

    def execute_mi_api(self,url_path,country,params):
        url = self.get_api_url(country) + url_path
        return self.execute_api_call(url,params)

    def get_devices(self, country):
        url = self.get_api_url(country) + "/home/device_list"
        params = {
            "data": '{"getVirtualModel":false,"getHuamiDevices":0}'
        }
        return self.execute_api_call(url, params)

    def get_device_datas(self, country):
        url = self.get_api_url(country) + "/device/batchdevicedatas"
        params = {
            "data": '[{"did":"blt.3.1153bjkholc00","props":["prop.s_auth_config"]}]'
        }
        return self.execute_api_call(url, params)

    def get_user_get_user_device_data(self, country):
        url = self.get_api_url(country) + "/user/get_user_device_data"
        params = {
            "data": '{"did":"blt.3.1153bjkholc00","key":"4109","type":"prop","time_end":1612728638,"limit":1}'
        }
        return self.execute_api_call(url, params)

    def execute_api_call(self, url, params):
        self.logger.debug("execute_api_call %s with params %s", url, json.dumps(params))
        if not self._auth_data["logged_in"]:
            if not self.login():
                return None
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": self._auth_data["agent"],
            "Content-Type": "application/x-www-form-urlencoded",
            "X-XIAOMI-PROTOCAL-FLAG-CLI": "PROTOCAL-HTTP2",
            "MIOT-ENCRYPT-ALGORITHM": "ENCRYPT-RC4",
            "MIOT-ACCEPT-ENCODING": "GZIP"
        }
        cookies = {
            "cUserId": str(self._auth_data["cUserId"]),
            "userId": str(self._auth_data["userId"]),
            "yetAnotherServiceToken": str(self._auth_data["serviceToken"]),
            "serviceToken": str(self._auth_data["serviceToken"]),
            "locale": "en_GB",
            "timezone": "GMT+02:00",
            "is_daylight": "1",
            "dst_offset": "3600000",
            "channel": "MI_APP_STORE"
        }
        millis = round(time.time() * 1000)
        nonce = self.generate_nonce(millis)
        sig_nonce = self.signed_nonce(nonce)
        rc4encoder = RC4Coder(base64.b64decode(sig_nonce))
        params["rc4_hash__"] = self.generate_signature2("POST", url.split('com')[1].replace("/app", ""), params,
                                                        sig_nonce).decode('UTF-8')
        params = {k: base64.b64encode(rc4encoder.rc4mi(v.encode())).decode('UTF-8') for k, v in params.items()}
        params["signature"] = self.generate_signature2("POST", url.split('com')[1].replace("/app", ""), params,
                                                       sig_nonce).decode('UTF-8')
        params["_nonce"] = nonce
        params["ssecurity"] = self._auth_data["ssecurity"]

        self.logger.debug("execute_api_call request to URL %s with headers %s with cookies %s and params %s", url,
                          json.dumps(headers), json.dumps(cookies), json.dumps(params))
        response = self._session.post(url, headers=headers, cookies=cookies, data=params)
        self.logger.debug("execute_api_call response from URL %s have response code %s headers %s and body %s", url,
                          response.status_code, json.dumps(dict(response.headers)), response.text)
        if response.status_code == 200:
            response_decrypted = RC4Coder.rc4mi_once(base64.b64decode(response.text), base64.b64decode(sig_nonce))
            if response.headers.get('Miot-Content-Encoding') == 'GZIP':
                response_decrypted = gzip.decompress(response_decrypted)
            self.logger.debug("Decrypted response body from url %s is %s", url, response_decrypted)
            result = json.loads(response_decrypted)
            return result
        if response.status_code == 401:
            self.logger.warning("Handled auth error")
            if self.login():
                self.logger.warning("Second try of request")
                return self.execute_api_call(url, params)
            else:
                self.logger.error("Xiaomi login failed, skipping request to url %s", url)
                return
        return None

    def execute_api_call_old(self, url, params):
        if not self._auth_data["logged_in"]:
            if not self.login():
                return None
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": self._auth_data["agent"],
            "Content-Type": "application/x-www-form-urlencoded",
            "x-xiaomi-protocal-flag-cli": "PROTOCAL-HTTP2"
        }
        cookies = {
            "userId": str(self._auth_data["userId"]),
            "yetAnotherServiceToken": str(self._auth_data["serviceToken"]),
            "serviceToken": str(self._auth_data["serviceToken"]),
            "locale": "en_GB",
            "timezone": "GMT+02:00",
            "is_daylight": "1",
            "dst_offset": "3600000",
            "channel": "MI_APP_STORE"
        }
        millis = round(time.time() * 1000)
        nonce = self.generate_nonce(millis)
        signed_nonce = self.signed_nonce(nonce)
        signature = self.generate_signature(url.replace("/app", ""), signed_nonce, nonce, params)
        fields = {
            "signature": signature,
            "_nonce": nonce,
            "data": params["data"]
        }
        print(url)
        print(headers)
        print(cookies)
        print(fields)
        response = self._session.post(url, headers=headers, cookies=cookies, params=fields)
        print(response.status_code)
        print(response.text)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 401:
            print("Handled auth error")
            if self.login():
                print("Second try of request")
                return self.execute_api_call_old(url, params)
            else:
                return
        return None

    def get_api_url(self, country):
        return "https://" + ("" if country == "cn" else (country + ".")) + "api.io.mi.com/app"

    def signed_nonce(self, nonce):
        hash_object = SHA256.new()
        hash_object.update(base64.b64decode(self._auth_data["ssecurity"]) + base64.b64decode(nonce))
        return base64.b64encode(hash_object.digest()).decode('utf-8')

    def generate_signature2(self, method, path, params, signed_nonce):
        signature_params = [method, path]
        for k, v in params.items():
            signature_params.append(f"{k}={v}")
        signature_params.append(signed_nonce)
        signature_string = "&".join(signature_params)
        s = SHA1.new()
        s.update(signature_string.encode('UTF-8'))
        return base64.b64encode(s.digest())

    @staticmethod
    def create_rc4_key(ssecurity, nonce):
        return base64.b64encode(hashlib.sha256(base64.b64encode(ssecurity) + base64.b64encode(nonce)).digest())

    @staticmethod
    def generate_nonce(millis):
        nonce_bytes = os.urandom(8) + (int(millis / 60000)).to_bytes(4, byteorder='big')
        return base64.b64encode(nonce_bytes).decode()

    @staticmethod
    def generate_agent():
        agent_id = "".join(map(lambda i: chr(i), [random.randint(65, 69) for _ in range(13)]))
        return f"Android-7.1.1-1.0.0-ONEPLUS A3010-136-{agent_id} APP/xiaomi.smarthome APPV/62830"

    @staticmethod
    def generate_device_id():
        return "".join(map(lambda i: chr(i), [random.randint(97, 122) for _ in range(6)]))

    @staticmethod
    def generate_signature(url, signed_nonce, nonce, params):
        signature_params = [url.split("com")[1], signed_nonce, nonce]
        for k, v in params.items():
            signature_params.append(f"{k}={v}")
        signature_string = "&".join(signature_params)
        signature = hmac.new(base64.b64decode(signed_nonce), msg=signature_string.encode(), digestmod=hashlib.sha256)
        return base64.b64encode(signature.digest()).decode()

    @staticmethod
    def to_json(response_text):
        return json.loads(response_text.replace("&&&START&&&", ""))
