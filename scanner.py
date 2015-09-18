#!/usr/bin/env python

import json
import os
import re
import argparse

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
        scanned = 0
        total_matches = 0
        for dirpath, dirnames, files in os.walk(path):
            for name in files:
                scanned = scanned + 1
                (filename, extension) = os.path.splitext(name)
                #print "OK scan %s" % (dirpath+"/"+name)
                if extension.startswith("."):
                    extension = extension[1:]
                matches = []
                for pattern in self.patterns:
                    if pattern.matches(dirpath,name,extension):
                        matches.append(pattern)
                total_matches = total_matches + len(matches)
                for pattern in matches:
                    print "OK match %s %s" % (pattern, dirpath+"/"+name)
        print "\nFiles scanned = %d" % scanned
        print "Files with potential secrets = %d" % total_matches




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Find secrets')
    parser.add_argument('-d', '--parent-dir', nargs='?',
                       help='parent directory for recursive scanning of files')
    parser.add_argument('-g', '--github-clone-url', nargs='?',
                       help='github url to clone and scan')
    parser.add_argument('-p', '--patterns-file', nargs='?',
                       help='json file of patterns for scanning')

    args = parser.parse_args()

    s = Scanner()
    if args.parent_dir:
        s.scan(path='/home/jbruce/repos/')

