# -*- coding: utf8 -*-

import sys

from distutils.core import setup
from Cython.Build import cythonize

setup(

    name = 'Data harvest',
    ext_modules = cythonize("src/*.pyx"),
    license = "GNU GPL Version 3",
    script_args = ['build_ext', '--build-lib=lib', '--build-temp=.build']
)

sys.path.append(sys.path[0] + '/lib')

from threadEngine import *

'''

import geocoder

class Geolocation:

    def __init__(self, input):

        if (type(input) == str): self.data = geocoder.google(input)
        if (type(input) == list): self.data = geocoder.google(input, method="reverse")

    def getCoords(self): return self.data.lat, self.data.lng
    def getAddress(self): return self.data.address

    c = Geodata(sys.argv[1])
    coords = c.getCoords()
    print str(coords[0]) + ", " + str(coords[1])

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

'''


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    # Get desktop info
    desktop = QtWidgets.QDesktopWidget()
    geom = desktop.availableGeometry()

    # Webkit view setting
    webView = QtWebKitWidgets.QWebView()
    mainFrame = webView.page().mainFrame()
    mainFrame.setScrollBarPolicy(QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)
    mainFrame.setScrollBarPolicy(QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)

    # Bridge
    bridge = Bridge(mainFrame)
    mainFrame.addToJavaScriptWindowObject("pyBridge", bridge)
    webView.load(QtCore.QUrl("file://" + sys.path[0] + "/gui.html"))

    # Window setting
    window = QtWidgets.QMainWindow()
    window.resize(800, 600)
    window.move(int((geom.width()-800)/2.0), int((geom.height()-600)/2.0))
    window.setWindowTitle('Data harvest')

    window.setCentralWidget(webView)
    window.show()

    app.exec_()
    app.deleteLater()
    sys.exit()
