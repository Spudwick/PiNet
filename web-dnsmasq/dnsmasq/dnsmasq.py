
import os.path
import re

class config():
    def __getitem__(self, key):
        return self.options[key]
    
    def __setitem__(self, key, item):
        self.options[key] = item
    
    def __delitem__(self, key):
        del self.options[key]

    def __contains__(self, key):
        return key in self.options.keys()

    def keys(self):
        return self.options.keys()

    def __init__(self,conf_file=None):
        print('new dnsmasq class!')

        if conf_file == None:
            self.conf_file = "/etc/dnsmasq.conf"
        else:
            self.conf_file = os.path.abspath(conf_file)
        print(self.conf_file)
    
        self.__dict__.update({'this':'works'})
        self.options = {}
        self.parse()

    def parse(self,file=None):
        if file == None:
            file = self.conf_file

        fp = open(file,'r') 
        for line in fp.readlines():
            line = (re.sub('#.*','',line)).strip()          # Get rid of comments and extra whitespaces.

            if len(line) == 0:
                continue

            sets = re.search('=.*',line)
            if sets == None:
                option = line
                sets = [None]
            else:
                option = re.search('.*=',line).group()[:-1]
                sets = sets.group()[1:].split(',')
            if len(sets) == 1:
                sets = sets[0]

            if not option in self.options.keys():
                self.options[option] = [sets]
            else:
                self.options[option].append(sets)

            if option == "conf-file":
                self.parse(sets)

            
