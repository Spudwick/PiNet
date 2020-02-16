from OpenSSL import crypto
import os
import socket
import random
import datetime


class AuthFile():
	load_method = None
	
	@classmethod
	def fromFile(cls, path):
		ret = cls(path)
		ret.read()
		return ret

	def __init__(self, path=None):

		print(f'Creating new { self.__class__.__name__ } object.')

		self.file = None
		self.path = path

		if self.path and os.path.exists(self.path):
			self.read()

	def __getattr__(self, name):
		try:
			return getattr(self.file, name)
		except AttributeError:
			raise AttributeError(f'Neither { self.__class__.__name__ } or { self.file.__class__.__name__ } objects have attribute { name }!')

	def read(self, path=None):
		if self.load_method == None:
			raise NotImplementedError(f'Load Method not provided for { self.__class__.__name__ } object!')
		
		if path:
			self.path = path
		if not self.path:
			raise ValueError("File path not specified!")

		print(f'Reading file { self.path }')

		with open(self.path) as f:
			self.file = self.__class__.load_method(crypto.FILETYPE_PEM, f.read())

		if self.file == None:
			raise IOError("Failed to read file " + self.path + "!")
		
		print(f'Type of self.file is { self.file.__class__.__name__ }')

	def write(self, path=None):
		if self.dump_method == None:
			raise NotImplementedError(f'Dump Method not provided for { self.__class__.__name__ } object!')
		
		if path:
			self.path = path
		if not self.path:
			raise ValueError("File path not specified!")
		
		print(f'Writing { self.file.__class__.__name__ } to file { self.path }')

		string = self.__class__.dump_method(crypto.FILETYPE_PEM, self.file)

		with open(self.path, "wt") as f:
			f.write(string.decode("utf-8"))

	def generate(self):
		raise NotImplementedError(f'No generate method defined for { self.__class__.__name__ }')


class KeyFile(AuthFile):
	load_method = crypto.load_privatekey
	dump_method = crypto.dump_privatekey

	def generate(self):
		if self.file == None:
			self.file = crypto.PKey()

		print(f'Generating new { self.file.__class__.__name__ }...')

		self.file.generate_key(crypto.TYPE_RSA, 2048)


class CertFile(AuthFile):
	load_method = crypto.load_certificate
	dump_method = crypto.dump_certificate

	def generate(self, country=None, state=None, location=None, organisation=None, unit=None, common_name=None, notBefore=0, notAfter=3600, key=None):
		if self.file == None:
			self.file = crypto.X509()

		print(f'Generating new { self.file.__class__.__name__ }...')

		if country:
			self.file.get_subject().C = country
		if state:
			self.file.get_subject().ST = state
		if location:
			self.file.get_subject().L = location
		if organisation:
			self.file.get_subject().O = organisation
		if unit:
			self.file.get_subject().OU = unit
		if common_name == None:
			self.file.get_subject().CN = socket.gethostname()
		else:
			self.file.get_subject().CN = common_name

		self.file.gmtime_adj_notBefore(notBefore)
		self.file.gmtime_adj_notAfter(notAfter)

		print(f'   Common Name  : { self.file.get_subject().CN }')
		print(f'   Valid From   : { datetime.datetime.strptime(self.file.get_notBefore().decode("ascii"), "%Y%m%d%H%M%SZ") }')
		print(f'   Valid Until  : { datetime.datetime.strptime(self.file.get_notAfter().decode("ascii"), "%Y%m%d%H%M%SZ") }')

		self.file.set_serial_number(random.getrandbits(64))

		if key:
			self.sign(key)

	def sign(self, key):

		print(f'Signing { self.file.__class__.__name__ } using { key }')

		self.file.set_pubkey(key.file)
		self.file.sign(key.file, 'sha512')


if __name__ == "__main__":

	ca_key = KeyFile("./testfiles/ca.key")
	ca_key.generate()
	ca_key.write()

	ca_crt = CertFile("./testfiles/ca.crt")
	ca_crt.generate()
	ca_crt.sign(key=ca_key)
	ca_crt.write()

	svr_key = KeyFile("./testfiles/svr.key")
	svr_key.generate()
	svr_key.write()

	
