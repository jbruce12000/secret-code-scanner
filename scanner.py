#!/usr/bin/env python
#import ntpath
import json
import os
import re

class Pattern:

    def __init__(self,part=None,ptype=None,pattern=None,caption=None,description=None):
        self.part = part
        self.ptype = ptype
        self.pattern = pattern
        self.caption = caption
        self.description = description
        self.compiled_pattern = re.compile(self.pattern)


    def part(self):
        return self.part

    def ptype(self):
        return self.ptype

    def pattern(self):
        return self.pattern

    def caption(self):
        return self.caption

    def description(self):
        return self.description

    def matches(self,dirpath=None,name=None,extension=None):
        if self.part == 'extension':
            if self.ptype == 'match':
                if str(self.pattern) == str(extension):
                    return True
            else:
                if self.compiled_pattern.match(extension):
                    return True
        elif self.part == 'filename':
            if self.ptype == 'match':
                if str(self.pattern) == str(name):
                    return True
            else:
                if self.compiled_pattern.match(name):
                    return True
        elif self.part == 'path':
            if self.ptype == 'match':
                if str(self.pattern) == str(dirpath):
                    return True
            else:
                if self.compiled_pattern.match(dirpath):
                    return True
        else:
            return False
        return False

    def __str__(self):
        return "%s, %s, %s" % (self.part,self.ptype,self.pattern)

class Scanner:
  
    def __init__(self,patterns_file='./patterns.json'):
        self.patterns_file=patterns_file
        self.patterns = []
        self.obj = None
        self.load_patterns()
  
    def load_patterns(self):
        with open(self.patterns_file) as json_data:
            self.obj = json.load(json_data)

        for entry in self.obj:
            try:
                pat = Pattern(part = entry['part'],
                              ptype = entry['type'],
                              pattern = entry['pattern'],
                              caption = entry['caption'],
                              description = entry['description'])
                self.patterns.append(pat)
            except:
                print "ERR loading %s" % entry

    def scan(self,path='.'):
        for dirpath, dirnames, files in os.walk(path):
            for name in files:
                (filename, extension) = os.path.splitext(name)
                #print "OK scan %s" % (dirpath+"/"+name)
                if extension.startswith("."): extension = extension[1:]
                #print "%s, %s, %s" % (dirpath, filename, extension)
                matches = []
                for pattern in self.patterns:
                    if pattern.matches(dirpath,name,extension):
                        matches.append(pattern)
                for pattern in matches:
                    print "OK match %s %s" % (pattern, dirpath+"/"+name)




if __name__ == "__main__":
  s = Scanner()
  s.scan(path='/home/jbruce/repos/')
  #for i in s.patterns_for_extension():
  #    print i
  
