# -*- coding: utf8 -*-

import urllib
import requests
import re

# regular expression
cdef inline object googlePlusQuery = re.compile('\"([0-9]+)\"\,\,\"https\:\/\/plus\.google\.com\/[0-9]+\"\]\n\,\[\"([\w\ \'\-]+)\"\,{8}\"((?:https\:)?\/\/[a-zA-Z0-9\-\/\_\.]+)\"', re.UNICODE)
cdef inline object googlePlusToken = re.compile('\"\w{30,}', re.UNICODE)

def googlePlusSearch(object username):

    cdef object userList = []

    cdef object pageToken = ""
    cdef object headers = {'x-same-domain' : 1, 'origin' : 'https://plus.google.com', 'referer' : 'https://plus.google.com/'}
    cdef object data = {'f.req' : '[["'+ username +'",2,,,,,,],['+ pageToken +'],[,,,,,[,,,,[,],]],,,]'}

    cdef int count = 20
    while count == 20:

        text = requests.post("https://plus.google.com/_/s/query", data=data, headers=headers).text
        parsed = re.findall(googlePlusQuery, text)
        count = len(parsed)

        for p in parsed:

            ident = p[0]
            user = p[1]
            photo = p[2]

            if photo.startswith("https:") == False: photo = "https:" + photo
            userList.append([user, ident, photo])

        pageToken = re.search(googlePlusToken, text)
        
        if pageToken == None: break
        else: data = {'f.req' : '[["'+ username +'",2,,,,,,],['+ pageToken.group() +'"],[,,,,,[,,,,[,],]],,,]'}

    return userList
