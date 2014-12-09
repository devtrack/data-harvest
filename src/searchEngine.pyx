# -*- coding: utf8 -*-

import urllib
import requests
import re

# regular expression
cdef inline object googlePlusQuery = re.compile('\"([0-9]+)\"\,\,\"https\:\/\/plus\.google\.com\/[0-9]+\"\]\n\,\[\"([\w\ \'\-]+)\"\,{8}\"((?:https\:)?\/\/[a-zA-Z0-9\-\/\_\.]+)\"', re.UNICODE)
cdef inline object googlePlusToken = re.compile('\"\w{30,}', re.UNICODE)

cdef inline object googlePlusId = re.compile('[0-9]{21}', re.UNICODE)
cdef inline object googleVerify = re.compile('\<meta\ itemprop\=\"name\"\ content\=\"([\w\ \'\-]+)\"\>\<meta\ itemprop\=\"image\" content\=\"((?:https\:)?\/\/[a-zA-Z0-9\-\/\_\.]+)\"\>')

# header
cdef inline object headers = {'x-same-domain' : 1, 'origin' : 'https://plus.google.com', 'referer' : 'https://plus.google.com/'}

def googlePlusSearch(object username):

    cdef object userList = []

    cdef object pageToken = ""
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

def googlePlusSearchFriends(object userid):

  text = requests.get("https://plus.google.com/"+ userid +"/posts",headers=headers).text
  parsed = set(re.findall(googlePlusId, text))

  cdef object friendsList = []

  for p in parsed:

    if p != userid:
      
      friendText = requests.get("https://plus.google.com/"+ p +"/posts", headers=headers).text
      match = re.search(googleVerify, friendText)

      if match != None: friendsList.append([p, match.group(1), match.group(2)])

  return friendsList
