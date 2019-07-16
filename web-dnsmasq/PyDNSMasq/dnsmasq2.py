
import os.path
import re

VER_MAJOR = 1
VER_MINOR = 1
VER_STRING = str(VER_MAJOR) + "." + str(VER_MINOR)




class DNSMasq_file():
	@property
	def switches(self):
		array = []

		for line in self.lines:
			if len(line.split('=')) == 1:
				array.append(line)
		
		return array
	
	def __getitem__(self,key):
		array = []

		for line in self.lines:
			if not re.search(key,line) == None:
				try:
					option,value = line.split('=')
					array.append(value)
				except ValueError:
					return True

		if not array == []:
			return array
		else:
			return None

	def __init__(self,path):
		self.path = path
		self.lines = []

		self.parse()

		print(self.lines)

	def parse(self):
		with open(self.path,"r") as fp:
			for line in fp.readlines():
				line = re.sub("#.*","",line).strip()
				if len(line) == 0:
					continue

				self.lines.append(line)

	def add(self,option,value):
		self.lines.append(option + "=" + value)

	def write(self,path=None):
		if path == None:
			path = self.path + ".new"

		with open(path,"w") as fp:
			for line in self.lines:
				fp.write(line + "\n")