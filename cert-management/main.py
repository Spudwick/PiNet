
from CA_Helper import *


CertAuth = CA("./ca/test-ca")
print(CertAuth.path)
print(CertAuth.path_ca)
print(CertAuth.path_certs)
print(CertAuth.ca_files)
print(CertAuth.certs)
