#!/usr/bin/env python

import json
import os
import re
import argparse
import time
from github import Github
from pprint import pprint

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
        return "%s|%s|%s" % (self.part,self.ptype,self.pattern)

class Scanner:
  
    def __init__(self,patterns_file='./patterns.json',
                      github_api_token=None,
                      github_base_url='http://github.com/api/v3'):
        self.patterns_file=patterns_file
        self.patterns = []
        self.obj = None
        self.load_patterns()
        self.github_api_token = github_api_token
        self.github_base_url = github_base_url
        self.github_throttle_at = 100
        self.github_throttle_count = 0
        self.github_throttle_sleep = 1
  
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

    def scan_file_names(self, files=[], repo=None):
        scanned = 0
        total_matches = 0
        for f in files:
            scanned = scanned + 1
            matches = self.scan_file_name(f)
            total_matches = total_matches + len(matches)
            for pattern in matches:
                print "OK MATCH %s|%s|%s|%s" % (
                    repo.organization.html_url,
                    repo.name,
                    repo.html_url + '/tree/master/' + f,
                    pattern)

    def scan_file_name(self,file):
        dirpath,name = os.path.split(file)
        extension = os.path.splitext(file)[1]
        if extension.startswith("."):
            extension = extension[1:]
        matches = []
        for pattern in self.patterns:
            if pattern.matches(dirpath,name,extension):
                matches.append(pattern)
        return matches

    def crawl_github(self,repo,path):
       files = []
       r = None 
       try:
           r = repo.get_dir_contents(path)
           self.github_throttle_count = self.github_throttle_count + 1
           if self.github_throttle_count % self.github_throttle_at == 0:
               time.sleep(self.github_throttle_sleep)
               print "sleeping"
       except:
           return []

       for cfile in r:
           if cfile.type == "file":
               files.append(cfile.path)
           if cfile.type == "dir":
               files.extend(self.crawl_github(repo,cfile.path))
       return files

    def repos(self):
        from github import Github
        g = Github(login_or_token=self.github_api_token,
                   base_url=self.github_base_url)
        # all repos for a user
        for repo in g.get_user().get_repos():
            # pygithub fails to get a connection sometimes
            # this makes sure the repo I am about to connect to is valid
            # fix - needs limit
            while True:
                if repo.update():
                    break
            yield repo

    def scan_github(self):
        for repo in self.repos():
            try:
                print "starting repo %s" % repo.name
                files = self.crawl_github(repo,'/')
                self.scan_file_names(files=files,repo=repo)
            except:
                print "error getting repo data"
                import pdb; pdb.set_trace()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Find secrets')
    parser.add_argument('-t', '--github-api-token', nargs='?',
                       help='github api token')
    parser.add_argument('-b', '--github-base-url', nargs='?',
                       help='github base url')
    parser.add_argument('-p', '--patterns-file', nargs='?',
                       help='json file of patterns for scanning')

    args = parser.parse_args()

    if args.patterns_file:
        s = Scanner(patterns_file=args.patterns_file)
    else:
        s = Scanner()

    if args.github_api_token:
        s = Scanner(github_api_token = args.github_api_token,
                    github_base_url = args.github_base_url)
        s.scan_github()
