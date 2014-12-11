# -*- coding: utf8 -*-

import json
import time
from PyQt5 import QtCore, QtWidgets, QtWebKitWidgets

from searchEngine import *

class JThread(QtCore.QThread):

  def __init__(self, trigger, args, method):

    QtCore.QThread.__init__(self)
    self.args = args
    self.func = method
    self.trigger = trigger

  def run(self):

    self.trigger.emit("threadNotify", json.dumps(self.func + " ..."))
    result = globals()[self.func](self.args)
    self.trigger.emit("threadDone", json.dumps(result))

class Bridge(QtCore.QObject):

  trigger = QtCore.pyqtSignal(str, str)

  def __init__(self, mf):

    QtCore.QObject.__init__(self)
    self.mainFrame = mf

  @QtCore.pyqtSlot(str)
  def runThread(self, jsonArgs):

    args = json.loads(str(jsonArgs))

    self.call = args['callback']
    self.noti = args['notify']

    self.thread = JThread(self.trigger, args['params'], args['method'])
    self.trigger.connect(self.threadNotify)

    self.thread.start()

  def threadNotify(self, signal, info):

    if signal == "threadNotify": self.mainFrame.evaluateJavaScript(self.noti + "(%s)" % info)
    elif signal == "threadDone": self.runThreadDone(info)

  def runThreadDone(self, info):

    self.mainFrame.evaluateJavaScript(self.call + "(%s)" % info)
    self.trigger.disconnect(self.threadNotify)

    self.thread.terminate()
