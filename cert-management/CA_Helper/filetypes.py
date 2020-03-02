
from .containers import FileContainer

from OpenSSL import crypto


class X509File(FileContainer):
    def __init__(self, path=None):
        super().__init__(obj=crypto.X509, path=path, read=self._read_, write=self._write_)

    def _read_(self, path, cls):
        with open(path) as f:
            return crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

    def _write_(self, path, cls, inst):
        with open(path, "wt") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, inst).decode("utf-8"))


PKEY_PRIV_KEY = "PRIVATE"
PKEY_PUB_KEY = "PUBLIC"
class PKeyFile(FileContainer):
    def __init__(self, typ, path=None):
        self.typ = typ

        super().__init__(obj=crypto.PKey, path=path, read=self._read_, write=self._write_)

    def _read_(self, path, cls):
        with open(path) as f:
            if self.typ == PKEY_PRIV_KEY:
                return crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())
            elif self.typ == PKEY_PUB_KEY:
                return crypto.load_publickey(crypto.FILETYPE_PEM, f.read())

    def _write_(self, path, cls, inst):
        with open(path, "wt") as f:
            if self.typ == PKEY_PRIV_KEY:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, inst).decode("utf-8"))
            elif self.typ == PKEY_PUB_KEY:
                f.write(crypto.dump_publickey(crypto.FILETYPE_PEM, inst).decode("utf-8"))


class X509ReqFile(FileContainer):
    def __init__(self, path=None):
        super().__init__(obj=crypto.X509Req, path=path, read=self._read_, write=self._write_)

    def _read_(self, path, cls):
        with open(path) as f:
            return crypto.load_certificate_request(crypto.FILETYPE_PEM, f.read())

    def _write_(self, path, cls, inst):
        with open(path, "wt") as f:
            f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, inst).decode("utf-8"))