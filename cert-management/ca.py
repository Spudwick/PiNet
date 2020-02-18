
import datetime
import socket
import random
from OpenSSL import crypto

from CA_Helper import *


if __name__ == "__main__":
    # Generate RSA Key Pair.
    # This becomes the CA Certificate Public and Private Key.
    CA_privkeyfile = PKeyFile(PKEY_PRIV_KEY, path="testfiles/ca_priv.key")
    CA_privkeyfile.generate_key(crypto.TYPE_RSA, 2048)
    CA_privkeyfile.writefile()

    # Create a new PKeyFile object that contains the same PKey instance to also save the Public Key.
    CA_pubkeyfile = PKeyFile(PKEY_PUB_KEY, obj=CA_privkeyfile.inst, path="testfiles/ca_pub.key")
    CA_pubkeyfile.writefile()

    # Generate the CA Certificate.
    CA_certfile = X509File("testfiles/ca.crt")
    CA_certfile.get_subject().C = "UK"
    CA_certfile.get_subject().ST = "West Midlands"
    CA_certfile.get_subject().L = "Birmingham"
    CA_certfile.get_subject().O = "Test"
    CA_certfile.get_subject().OU = "Test Unit"
    CA_certfile.get_subject().CN = socket.gethostname()
    CA_certfile.gmtime_adj_notBefore(0)
    CA_certfile.gmtime_adj_notAfter(3600)
    CA_certfile.set_serial_number(random.getrandbits(64))
    # Set the Public Key field to the Public Key from the pair generated above.
    CA_certfile.set_pubkey(CA_pubkeyfile.inst)
    # Sign the CA Certificate using the Private Key from the pair generated above.
    CA_certfile.sign(CA_privkeyfile.inst, 'sha512')
    CA_certfile.writefile()
    # Result is a SELF-SIGNED CA Certificate.
    # The certificate contains the Public Key and we have already saved the Private Key to a file.

    # Generate a CSR for signing using our generated CA details.
    csrfile = X509ReqFile("testfiles/server.csr")
    csrfile.get_subject().C = "UK"
    csrfile.get_subject().ST = "West Midlands"
    csrfile.get_subject().L = "Birmingham"
    csrfile.get_subject().O = "Test"
    csrfile.get_subject().OU = "Test CSR"
    csrfile.get_subject().CN = socket.gethostname()
    csrfile.set_pubkey(CA_pubkeyfile.inst)
    csrfile.sign(CA_privkeyfile.inst, 'sha512')
    csrfile.writefile()

    # Sign the CSR using our generated CA details.
    certfile = X509File("testfiles/server.crt")
    certfile.set_serial_number(random.getrandbits(64))
    certfile.gmtime_adj_notBefore(0)
    certfile.gmtime_adj_notAfter(3600)
    certfile.set_issuer(CA_certfile.get_subject())
    certfile.set_subject(csrfile.get_subject())
    certfile.set_pubkey(csrfile.get_pubkey())
    certfile.sign(CA_privkeyfile.inst, 'sha512')
    certfile.writefile()
    # Results in a CA-SIGNED Certificate.
