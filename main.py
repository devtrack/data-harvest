# -*- coding: utf8 -*-

import sys
import urllib
import geocoder
import requests
import json
import lxml.html as html
import re
from unicodedata import normalize

# regular expression
googlePlusQuery = re.compile('\"([0-9]+)\"\,\,\"https\:\/\/plus\.google\.com\/[0-9]+\"\]\n\,\[\"([\w\ \'\-]+)\"', re.UNICODE)
googlePlusToken = re.compile('\"\w{30,}', re.UNICODE)

class Geolocation:

    def __init__(self, input):

        if (type(input) == str): self.data = geocoder.google(input)
        if (type(input) == list): self.data = geocoder.google(input, method="reverse")

    def getCoords(self): return self.data.lat, self.data.lng
    def getAddress(self): return self.data.address

class GoogleAccount:

    def __init__(self, input):

        if type(input) == list and len(input) == 3:

            self.username = input[1]
            self.id = input[0]
            self.photo = input[2]

class Person:

    def __init__(self, input, typeOfAccount = None):

        if typeOfAccount == "googlePlus" and type(input) == list:

            self.username = input[1]
            self.googleAccount = GoogleAccount(input)

class Cible:

    def __init__(self, input):

        if (type(input) == str):

            self.username = input

            self.relatedUsers = []

            users = self.googlePlusSearch(self.username)
            for user in users: self.relatedUsers.append(Person(user, "googlePlus"))

    def googlePlusSearch(self, username):

        userList = []

        pageToken = ""
        headers = {'x-same-domain' : 1, 'origin' : 'https://plus.google.com', 'referer' : 'https://plus.google.com/'}
        data = {'f.req' : '[["'+ username +'",2,,,,,,],['+ pageToken +'],[,,,,,[,,,,[,],]],,,]'}

        count = 20
        while count == 20:

            text = requests.post("https://plus.google.com/_/s/query", data=data, headers=headers).text
            parsed = re.findall(googlePlusQuery, text)
            count = len(parsed)

            for p in parsed: userList.append(p)

            pageToken = re.search(googlePlusToken, text)
            if pageToken == None: break
            else:
                data = {'f.req' : '[["'+ username +'",2,,,,,,],['+ pageToken.group() +'"],[,,,,,[,,,,[,],]],,,]'}



        for user in userList: print user[0] + " : " + user[1]

        return userList

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        sys.exit()
    elif len(sys.argv) == 2:
        '''c = Geodata(sys.argv[1])
        coords = c.getCoords()
        print str(coords[0]) + ", " + str(coords[1])'''
        c = Cible(sys.argv[1])
        #for u in c.relatedUsers: print u.username + " [" + u.googleAccount.id + "] : " + u.googleAccount.photo

    else:
        c = Cible(sys.argv[1]+" "+sys.argv[2])
        #for u in c.relatedUsers: print u.username + " [" + u.googleAccount.id + "] : " + u.googleAccount.photo
        '''c = Geodata([sys.argv[1], sys.argv[2]])
        address = c.getAddress()
        print str(address)'''
