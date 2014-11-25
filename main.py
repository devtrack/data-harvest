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

class Target(QtCore.QThread):

    def __init__(self, target):

        QtCore.QThread.__init__(self)
        self.username = str(target)
        self.relatedUsers = []

    def run(self):

        users = self.googlePlusSearch(self.username)
        self.emit(QtCore.SIGNAL("threadDone(QString)"), json.dumps(users))

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
                userList.append([user, ident, photo])

            pageToken = re.search(googlePlusToken, text)
            if pageToken == None: break
            else:
                data = {'f.req' : '[["'+ username +'",2,,,,,,],['+ pageToken.group() +'"],[,,,,,[,,,,[,],]],,,]'}

        return userList

class Bridge(QtCore.QObject):

    def __init__(self):
        QtCore.QObject.__init__(self)

    @QtCore.pyqtSlot(str)
    def search(self, target):

        self.c = Target(target)
        self.connect(self.c, QtCore.SIGNAL("threadDone(QString)"), self.searchThreadDone)

        self.c.start()

    def searchThreadDone(self, info):

        mainFrame.evaluateJavaScript("searchCallback(%s)" % info)
        self.disconnect(self.c, QtCore.SIGNAL("threadDone(QString)"), self.searchThreadDone)

if __name__ == '__main__':

    app = QtGui.QApplication([""])

    # Get desktop info
    desktop = QtGui.QDesktopWidget()
    geom = desktop.availableGeometry()

    # Webkit view setting
    webView = QtWebKit.QWebView()
    mainFrame = webView.page().mainFrame()
    mainFrame.setScrollBarPolicy(QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
    mainFrame.setScrollBarPolicy(QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)

    # Bridge
    bridge = Bridge()
    mainFrame.addToJavaScriptWindowObject("pyBridge", bridge)
    webView.load(QtCore.QUrl("file://" + sys.path[0] + "/gui.html"))

    # Window setting
    window = QtGui.QMainWindow()
    window.resize(800, 600)
    window.move(int((geom.width()-800)/2.0), int((geom.height()-600)/2.0))
    window.setWindowTitle('Data harvest')

    window.setCentralWidget(webView)
    window.show()

    sys.exit(app.exec_())
