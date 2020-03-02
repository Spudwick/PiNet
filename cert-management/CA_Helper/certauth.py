
from .filetypes import *

from OpenSSL import crypto
from os import mkdir, listdir
from os.path import exists
from random import getrandbits
from socket import gethostname


class CA():
    @property
    def ca_key_path(self):
        return f'{ self.path }/ca.key'
    
    @property
    def ca_crt_path(self):
        return f'{ self.path }/ca.crt'

    @property
    def crt_path(self):
        return f'{ self.path }/certs'

    def __str__(self):
        return self.path

    def __repr__(self):
        parts = self.path.split("/")
        return f'{ self.__class__.__name__ }(root="{ "/".join(parts[0:-1]) }", ca_id="{ parts[-1] }")'

    def __init__(self, root="./ca/", ca_id=None):
        if not root.endswith("/"):
            root = root + "/"
        
        # If no ID is provided for the CA, generate a random numerical ID.
        if not ca_id:
            while ca_id == None or exists(self.path):
                ca_id = f'{ getrandbits(8) }'
                self.path = f'{ root }{ ca_id }'
            self.ca_id = ca_id
        else:
            self.ca_id = ca_id
            self.path = f'{ root }{ ca_id }'

        # Create the CA directory if required.
        if not exists(self.path):
            mkdir(self.path)

        # If CA Key or Certificate is missing, re-generate both.
        if not exists(self.ca_crt_path) or not exists(self.ca_key_path):
            self.__ca_crt_gen()
        else:
            self.ca_key = PKeyFile(PKEY_PRIV_KEY, path=self.ca_key_path)
            self.ca_crt = X509File(path=self.ca_crt_path)

        # Load existing Certificates into object.
        self.__load_crts()

        self.__print()

    def __ca_crt_gen(self):
        # Generate new CA key pair.
        self.ca_key = PKeyFile(PKEY_PRIV_KEY, path=self.ca_key_path)
        self.ca_key.generate_key(crypto.TYPE_RSA, 2048)
        self.ca_key.writefile()

        # Generate and self-sign new CA Certificate.
        self.ca_crt = X509File(path=self.ca_crt_path)
        self.ca_crt.get_subject().C = "UK"
        self.ca_crt.get_subject().ST = "West Midlands"
        self.ca_crt.get_subject().L = "Birmingham"
        self.ca_crt.get_subject().O = "PiNet"
        self.ca_crt.get_subject().OU = self.ca_id
        self.ca_crt.get_subject().CN = gethostname()
        self.ca_crt.gmtime_adj_notBefore(0)
        self.ca_crt.gmtime_adj_notAfter(3600)
        self.ca_crt.set_serial_number(getrandbits(64))
        self.ca_crt.set_pubkey(self.ca_key.inst)            # Public key stored as part of certificate.
        self.ca_crt.sign(self.ca_key.inst, 'sha512')        # Sign certificate using private key.
        self.ca_crt.writefile()

    def __load_crts(self):        
        self.crt_lst = []
        
        if not exists(self.crt_path):
            return

        for f in listdir(self.crt_path):            
            if ".crt" in f and not self.path + "/" + f == self.ca_crt.path:
                self.crt_lst.append(X509File(path=self.crt_path + "/" + f))

    def __print(self):
        print(f'{ self.__class__.__name__ } Object:')
        print(f'   ID          : { self.ca_id }')
        print(f'   Path        : { self.path }')
        print(f'   Private Key : { self.ca_key_path } ({ self.ca_key })')                               # Private Key stored in file.
        print(f'   Public Key  : { self.ca_crt_path }->Public Key ({ self.ca_crt.get_pubkey() })')      # Public Key obtained from within Certificate.
        print(f'   Certificate : { self.ca_crt_path } ({ self.ca_crt })')                               # Certificate stored in file.
        print(f'      Organisation  : { self.ca_crt.get_subject().O }')
        print(f'      Unit          : { self.ca_crt.get_subject().OU }')
        print(f'      Common Name   : { self.ca_crt.get_subject().CN }')
        print(f'      Starts At     : { self.ca_crt.get_notBefore() }')      # TODO : Convert to Human Readable
        print(f'      Expires At    : { self.ca_crt.get_notAfter() }')       # TODO : Convert to Human Readable
        print(f'      Serial Number : { self.ca_crt.get_serial_number() }')
        print(f'   Loaded Certs     : { len(self.crt_lst) }')
        for crt in self.crt_lst:
            print(f'      { crt.path }')

    def gen_csr(self, c="UK", st="West Midlands", l="Birmingham", o=None, ou=None, cn=gethostname()):
        csr = crypto.X509Req()
        csr.get_subject().C = c
        csr.get_subject().ST = st
        csr.get_subject().L = l
        csr.get_subject().O = "Unknown" if not o else o
        csr.get_subject().OU = "Unknown" if not ou else ou
        csr.get_subject().CN = cn
        csr.set_pubkey(self.ca_crt.get_pubkey())
        csr.sign(self.ca_key.inst, 'sha512')

        print(f'Generated new CSR for { cn } at { csr }.')

        return csr

    def sign_csr(self, csr, name=None, nb=0, na=3600):
        if not exists(self.crt_path):
            mkdir(self.crt_path)
        
        # Generate a unique name if one wasn't provided.
        if not name:
            name_root = name = "_".join((self.ca_id, csr.get_subject().CN))
            cnt = 0
            while exists("/".join((self.crt_path, name + ".crt"))):
                cnt += 1
                name = "_".join((name_root, str(cnt)))
        if not name.endswith(".crt"):
            name = name + ".crt"

        # Sign CSR that was passed to the function.
        crt = X509File(path="/".join((self.crt_path, name)))
        crt.set_serial_number(getrandbits(64))
        crt.gmtime_adj_notBefore(nb)
        crt.gmtime_adj_notAfter(na)
        crt.set_issuer(self.ca_crt.get_subject())
        crt.set_subject(csr.get_subject())
        crt.set_pubkey(csr.get_pubkey())
        crt.sign(self.ca_key.inst, 'sha512')
        crt.writefile()

        # Add new Certificate to loaded list.
        self.crt_lst.append(crt)

        print(f'Signed CSR at { csr } to { crt }.')

        return crt

    def gen_crt(self, name=None, c="UK", st="West Midlands", l="Birmingham", o=None, ou=None, nb=0, na=3600, cn=gethostname()):
        csr = self.gen_csr(c=c, st=st, l=l, o=o, ou=ou, cn=cn)
        self.sign_csr(csr=csr, name=name, nb=nb, na=na)


