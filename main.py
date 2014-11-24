# -*- coding: utf8 -*-

import sys
import urllib
import geocoder
import requests
import json
import re

# Adding gui for project
from PyQt4 import QtCore, QtGui, QtWebKit

# regular expression
googlePlusQuery = re.compile('\"([0-9]+)\"\,\,\"https\:\/\/plus\.google\.com\/[0-9]+\"\]\n\,\[\"([\w\ \'\-]+)\"\,{8}\"((?:https\:)?\/\/[a-zA-Z0-9\-\/\_\.]+)\"', re.UNICODE)
googlePlusToken = re.compile('\"\w{30,}', re.UNICODE)

class Geolocation:

    def __init__(self, input):

        if (type(input) == str): self.data = geocoder.google(input)
        if (type(input) == list): self.data = geocoder.google(input, method="reverse")

    def getCoords(self): return self.data.lat, self.data.lng
    def getAddress(self): return self.data.address

    '''c = Geodata(sys.argv[1])
    coords = c.getCoords()
    print str(coords[0]) + ", " + str(coords[1])'''

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

class Target:

    def __init__(self, input):

        self.username = str(input)

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

            for p in parsed:

                ident = p[0]
                user = p[1]
                photo = p[2]

                if photo.startswith("https:") == False: photo = "https:" + photo
                userList.append([ident, user, photo])

            pageToken = re.search(googlePlusToken, text)
            if pageToken == None: break
            else:
                data = {'f.req' : '[["'+ username +'",2,,,,,,],['+ pageToken.group() +'"],[,,,,,[,,,,[,],]],,,]'}

        return userList

class Bridge(QtCore.QObject):

    @QtCore.pyqtSlot(str)
    def search(self, target):

        #QtGui.QMessageBox.information(None, "Info", msg)
        c = Target(target)
        retour = []
        for u in c.relatedUsers:
            retour.append([u.username, u.googleAccount.id, u.googleAccount.photo])

        mainFrame.evaluateJavaScript("searchCallback(%s)" % json.dumps(retour))

if __name__ == '__main__':

    f = open(sys.path[0] + "/gui.html")
    html = f.read()
    f.close()

    # Replace path file for include
    html = html.replace("css/metro-bootstrap.min.css", "file://" + sys.path[0] + "/css/metro-bootstrap.min.css")
    html = html.replace("js/jquery/jquery.min.js", "file://" + sys.path[0] + "/js/jquery/jquery.min.js")
    html = html.replace("js/jquery/jquery.widget.min.js", "file://" + sys.path[0] + "/js/jquery/jquery.widget.min.js")
    html = html.replace("js/metro.min.js", "file://" + sys.path[0] + "/js/metro.min.js")
    html = html.replace("js/metro-notify.js", "file://" + sys.path[0] + "/js/metro-notify.js")

    app = QtGui.QApplication([""])
    webView = QtWebKit.QWebView()
    mainFrame = webView.page().mainFrame()
    mainFrame.setScrollBarPolicy(QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
    mainFrame.setScrollBarPolicy(QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)

    bridge = Bridge()
    mainFrame.addToJavaScriptWindowObject("pyBridge", bridge)
    webView.setHtml(html)

    window = QtGui.QMainWindow()
    window.setCentralWidget(webView)
    window.show()

    sys.exit(app.exec_())
