#Script to decrypt request or response from dumped traffic between Mi Home App and Mi Home API servers
import urllib.parse
import base64
import requests
from Crypto.Hash import SHA256, SHA1
import gzip

#PARAMETERS:
# Request decrypt:
#REQUEST_DECODE_URL = "https://api.io.mi.com/app/mipush/eventsubbatch"
REQUEST_DECODE_URL = ""
#REQUEST_DECODE_BODY = 'data=Tnlz7l7uCaBRU8k***yFDyFrVGopfyCFmMgBmpMHZvJovcEBA765ocHYEVCK&rc4_hash__=8X+NC8Dcr*****g==&signature=+SXrHrOQ1u****pDxs=&_nonce=+jryIY***NJ&ssecurity=00z7c6V/p****Q=='
REQUEST_DECODE_BODY = ''

# Response decrypt:
#RESPONSE_DECODE_BODY = 'ocyXovIV9Z515L4N99X43oicHykskUXPMj7+w55t5DC***********wE3eM3JJSJhhgw='
RESPONSE_DECODE_BODY = ''
#RESPONSE_DECODE_SSECURITY_FROM_REQUEST = 'Pz3PEkO*****=='
RESPONSE_DECODE_SSECURITY_FROM_REQUEST = ''
#RESPONSE_DECODE_NONCE_FROM_REQUEST = 'wwR2*****kkd'
RESPONSE_DECODE_NONCE_FROM_REQUEST = ''

# RESPONSE_DECODE_SSECURITY_FROM_REQUEST=requests.utils.unquote(RESPONSE_DECODE_SSECURITY_FROM_REQUEST)


class RC4Coder:
    def __init__(self, key):
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


def signed_nonce(ssecurity, nonce):
    hash_object = SHA256.new()
    hash_object.update(base64.b64decode(ssecurity) + base64.b64decode(nonce))
    return base64.b64encode(hash_object.digest()).decode('utf-8')


def generate_signature2(method, path, params, signed_nonce):
    signature_params = [method, path]
    for k, v in params.items():
        signature_params.append(f"{k}={v}")
    signature_params.append(signed_nonce)
    signature_string = "&".join(signature_params)
    s = SHA1.new()
    s.update(signature_string.encode('UTF-8'))
    return base64.b64encode(s.digest())

################
# REQUEST_DECRYPT:
################

if REQUEST_DECODE_URL:
    url = REQUEST_DECODE_URL
    message = REQUEST_DECODE_BODY
    message = message.replace('+', '%2B')
    decoded = urllib.parse.parse_qs(message)
    print("Original request body:")
    print(decoded)
    signature = requests.utils.unquote(decoded["signature"][0])
    rc4_hash = requests.utils.unquote(decoded["rc4_hash__"][0])
    ssecurity = requests.utils.unquote(decoded["ssecurity"][0])
    nonce = requests.utils.unquote(decoded["_nonce"][0])
    data_orig = requests.utils.unquote(decoded["data"][0])

    sig_nonce = signed_nonce(ssecurity, nonce)
    data = RC4Coder.rc4mi_once(base64.b64decode(data_orig), base64.b64decode(sig_nonce)).decode('UTF-8')
    print("Decoded data:")
    print(data)

    rc4encoder = RC4Coder(base64.b64decode(sig_nonce))
    params = {"data": data}
    params["rc4_hash__"] = generate_signature2("POST", url.split('com')[1].replace("/app", ""), params, sig_nonce).decode(
        'UTF-8')
    params = {k: base64.b64encode(rc4encoder.rc4mi(v.encode())).decode('UTF-8') for k, v in params.items()}
    params["signature"] = generate_signature2("POST", url.split('com')[1].replace("/app", ""), params, sig_nonce).decode(
        'UTF-8')
    params["nonce"] = nonce
    params["ssecurity"] = ssecurity
    print("Calculated request body:")
    print(params)

################
# RESPONSE_DECRYPT:
################
if RESPONSE_DECODE_BODY:
    sig_nonce = signed_nonce(RESPONSE_DECODE_SSECURITY_FROM_REQUEST, RESPONSE_DECODE_NONCE_FROM_REQUEST)
    z = RC4Coder.rc4mi_once(base64.b64decode(RESPONSE_DECODE_BODY), base64.b64decode(sig_nonce))
    print("Response before gunzip:")
    print(z)
    z = gzip.decompress(z)
    print("Response gunzipped:")
    print(z)
