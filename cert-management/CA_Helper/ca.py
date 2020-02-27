
from .filetypes import *

from OpenSSL import crypto
import os
from random import getrandbits
from socket import gethostname


class CA():
    @property
    def path_ca(self):
        return self.path
    
    @property
    def path_certs(self):
        return os.path.join(self.path, "cert")

    def __init__(self, path="./"):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        self.ca_files = {
            "key" : None,
            "crt" : None,
        }
        self.certs = []

        self.__load_ca_files()
        self.__load_certs()

    def __load_ca_files(self):
        key_path = os.path.join(self.path_ca, "ca.key")
        crt_path = os.path.join(self.path_ca, "ca.crt")

        if not os.path.exists(key_path) or not os.path.exists(crt_path):
            self.__gen_ca_files(key=key_path, crt=crt_path)
        
        self.ca_files["key"] = PKeyFile(PKEY_PRIV_KEY, path=key_path)
        self.ca_files["crt"] = X509File(path=crt_path)

    def __gen_ca_files(self, key=None, crt=None):
        # Generate new CA key pair.
        ca_key = PKeyFile(PKEY_PRIV_KEY, path=key)
        ca_key.generate_key(crypto.TYPE_RSA, 2048)
        ca_key.writefile()

        # Generate and self-sign new CA Certificate.
        ca_crt = X509File(path=crt)
        ca_crt.get_subject().C = "UK"
        ca_crt.get_subject().ST = "West Midlands"
        ca_crt.get_subject().L = "Birmingham"
        ca_crt.get_subject().O = "PiNet"
        ca_crt.get_subject().OU = "PiNet-CA"
        ca_crt.get_subject().CN = gethostname()
        ca_crt.gmtime_adj_notBefore(0)
        ca_crt.gmtime_adj_notAfter(3600)
        ca_crt.set_serial_number(getrandbits(64))
        ca_crt.set_pubkey(ca_key.inst)            # Public key stored as part of certificate.
        ca_crt.sign(ca_key.inst, 'sha512')        # Sign certificate using private key.
        ca_crt.writefile()

    def __load_certs(self):
        if os.path.exists(self.path_certs):
            for f in os.listdir(self.path_certs):
                if f.endswith(".crt"):
                    self.certs.append( X509File(path=os.path.join(self.path_certs, f)) )

    def sign_csr(self, csr):
        if type(csr) == type("type"):
            csr = X509ReqFile(path=csr)

        
