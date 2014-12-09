# -*- coding: utf8 -*-

import json
from PyQt4 import QtCore, QtGui, QtWebKit

from searchEngine import *

class JThread(QtCore.QThread):

  def __init__(self, args, method):

    QtCore.QThread.__init__(self)
    self.args = args
    self.func = method

  def run(self):

    self.emit(QtCore.SIGNAL("threadNotify(QString)"), json.dumps(self.func + " ..."))
    result = globals()[self.func](self.args)
    self.emit(QtCore.SIGNAL("threadDone(QString)"), json.dumps(result))

class Bridge(QtCore.QObject):

  def __init__(self, mf):

    QtCore.QObject.__init__(self)
    self.mainFrame = mf

  @QtCore.pyqtSlot(str)
  def runThread(self, jsonArgs):

    args = json.loads(str(jsonArgs))

    self.call = args['callback']
    self.noti = args['notify']

    self.thread = JThread(args['params'], args['method'])
    self.connect(self.thread, QtCore.SIGNAL("threadDone(QString)"), self.runThreadDone)
    self.connect(self.thread, QtCore.SIGNAL("threadNotify(QString)"), self.threadNotify)

    self.thread.start()

  def threadNotify(self, info): self.mainFrame.evaluateJavaScript(self.noti + "(%s)" % info)

  def runThreadDone(self, info):

    self.mainFrame.evaluateJavaScript(self.call + "(%s)" % info)
    self.disconnect(self.thread, QtCore.SIGNAL("threadDone(QString)"), self.runThreadDone)
    self.disconnect(self.thread, QtCore.SIGNAL("threadNotify(QString)"), self.threadNotify)

    self.thread.terminate()
