#Script to decrypt request or response from dumped traffic between Mi Home App and Mi Home API servers
import urllib.parse
import base64
import requests
from Crypto.Hash import SHA256, SHA1
import gzip
import re

file="data/request_and_response.txt"

REQUEST_DECODE_METHOD = ""
REQUEST_DECODE_URL = ""
REQUEST_DECODE_BODY = ''
RESPONSE_DECODE_BODY = ''
RESPONSE_DECODE_SSECURITY_FROM_REQUEST=''
RESPONSE_DECODE_NONCE_FROM_REQUEST=''

with open(file, 'r') as fp:
    r1 = re.compile('([GETPOS]+)\s+(/app[^\s]+) ', re.VERBOSE)
    r2 = re.compile('(.*rc4_hash__.*)', re.VERBOSE)
    line=None
    while True:
        prev_line=line
        line = fp.readline()
        if not line:
            RESPONSE_DECODE_BODY=prev_line
            break
        line = line.strip()
        m2 = r2.match(line)
        if m2:
            REQUEST_DECODE_BODY=m2.groups()[0]
        if prev_line is None:
            print(line)
            m = r1.match(line)
            print(m)
            if m:
                REQUEST_DECODE_METHOD=m.groups()[0]
                REQUEST_DECODE_URL = 'xxx.com/'+m.groups()[1]
                print(m.groups()[1])






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
    signature = requests.utils.unquote(decoded["signature"][0])
    rc4_hash = requests.utils.unquote(decoded["rc4_hash__"][0])
    ssecurity = requests.utils.unquote(decoded["ssecurity"][0])
    nonce = requests.utils.unquote(decoded["_nonce"][0])
    data_orig = requests.utils.unquote(decoded["data"][0])
    RESPONSE_DECODE_SSECURITY_FROM_REQUEST=ssecurity
    RESPONSE_DECODE_NONCE_FROM_REQUEST=nonce
    sig_nonce = signed_nonce(ssecurity, nonce)
    data = RC4Coder.rc4mi_once(base64.b64decode(data_orig), base64.b64decode(sig_nonce)).decode('UTF-8')
    print("Decoded data from URL: "+url)
    print(data)
    sig_nonce = signed_nonce(RESPONSE_DECODE_SSECURITY_FROM_REQUEST, RESPONSE_DECODE_NONCE_FROM_REQUEST)
    z = RC4Coder.rc4mi_once(base64.b64decode(RESPONSE_DECODE_BODY), base64.b64decode(sig_nonce))
    try:
        x = gzip.decompress(z)
        print(x)
    except:
        print(z)

