
import os.path
import re


class DNSMasq():
	def __getitem__(self,key):
		array = []

		for file in self.conf_files:
			array = array + file[key]

		return array

	def __init__(self,root_conf=None):
		if root_conf == None:
			root_conf = "/etc/dnsmasq.conf"
		self.root_conf = root_conf

		self.conf_files = []
		self.parse()

	def parse(self,path=None):
		if path == None:
			self.conf_files = []
			path = self.root_conf;

		file = conf_file(path)
		self.conf_files.append(file)

		if "conf-file" in file:
			for f in file["conf-file"]:
				self.parse(f)

	def write(self,files=None):
		if files == None:
			queue = self.conf_files
		else:
			if type(files) == type([]):
				queue = files
			else:
				queue = [files]

		for file in queue:
			if file in self.conf_files:
				file.write()



class conf_file():
	def __init__(self, path):
		self.path = os.path.abspath(path)
		self.options = {}

		self.parse()

	def __getitem__(self,key):
		return self.options[key]

	def __setitem__(self,key,item):
		self.options[key] = item

	def __contains__(self,key):
		return key in self.options

	def keys(self):
		return self.options.keys()

	def parse(self):
		print("Parsing %s" % self.path)

		file = open(self.path,"r")
		for line in file.readlines():
			# Remove comments:
			line = re.sub('#.*','',line).strip()
			if len(line) == 0:
				continue

			# Extract Option and Settings:
			parts = line.split('=')
			option = parts[0]
			if len(parts) > 1:
				settings = parts[1]
			else:
				settings = None

			# Add to lists:
			if option in self.options.keys():
				self.options[option].append(settings)
			else:
				self.options[option] = [settings]

	def write(self,path=None):
		if path == None:
			path = self.path

		print("Writing to %s" % path)
