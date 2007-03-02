#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from os import getpid
from os.path import abspath, dirname, join, pardir
from subprocess import Popen, PIPE

from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import QFrame, QMessageBox

from profit.lib import Signals
from profit.widgets.ui_connectionwidget import Ui_ConnectionWidget


hasXterm = Popen(['which', 'xterm'], stdout=PIPE).communicate()[0].strip()


def commandStrings():
    binDir = abspath(join(dirname(abspath(__file__)), pardir, 'bin'))
    keyCmd =  join(binDir, 'login_helper') + ' -v'
    brokerCmd = join(binDir, 'ib_tws')
    if hasXterm:
        commandFs = 'xterm -title %s -e %s'
        keyCmd = commandFs % ('helper', keyCmd, )
        brokerCmd = commandFs % ('ibtws', brokerCmd, )
    return keyCmd, brokerCmd


class defaults(object):
    host = 'localhost'
    port = 7496
    client = 0 # getpid()


class ConnectionDisplay(QFrame, Ui_ConnectionWidget):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.session = session
        self.hostNameEdit.setText(defaults.host)
        self.portNumberEdit.setValue(defaults.port)
        self.clientIdEdit.setValue(defaults.client)
        keyHelperCommand, brokerCommand = commandStrings()
        self.keyHelperCommandEdit.setText(keyHelperCommand)
        self.brokerCommandEdit.setText(brokerCommand)
        self.pids = {'broker':[], 'helper':[]}
        session.registerMeta(self)
        self.connect(session, Signals.connectedTWS, self.on_connectedTWS)

    def on_session_ConnectionClosed(self, message):
        self.setEnabledButtons(True, False)
        self.serverVersionEdit.setText('')
        self.connectionTimeEdit.setText('')

    def on_connectedTWS(self):
        session = self.session
        if session.isConnected:
            self.setEnabledButtons(False, True)
            try:
                session.requestTickers()
                session.requestAccount()
                session.requestOrders()
            except (Exception, ), exc:
                QMessageBox.critical(self, 'Session Error', str(exc))
            else:
                self.serverVersionEdit.setText(
                    str(session.connection.serverVersion())
                    )
                self.connectionTimeEdit.setText(
                    session.connection.TwsConnectionTime()
                    )
        else:
            QMessageBox.critical(self, 'Connection Error',
                                 'Unable to connect.')
            self.setEnabledButtons(True, False)

    @pyqtSignature('')
    def on_connectButton_clicked(self):
        clientId = self.clientId()
        if clientId is None:
            return
        portNo = self.portNo()
        if portNo is None:
            return
        hostName = str(self.hostNameEdit.text())
        session = self.session
        try:
            session.connectTWS(hostName, portNo, clientId)
        except (Exception, ), exc:
            QMessageBox.critical(self, 'Connection Error', str(exc))

    @pyqtSignature('')
    def on_disconnectButton_clicked(self):
        if self.session and self.session.isConnected:
            self.session.disconnectTWS()
            self.setEnabledButtons(True, False)
            self.setNextClientId()

    def canClose(self):
        return not (self.session and self.session.isConnected)

    def clientId(self):
        try:
            clientId = self.clientIdEdit.value()
        except (ValueError, ), exc:
            clientId = None
            QMessageBox.critical(self, 'Client Id Error', str(exc))
        return clientId

    def portNo(self):
        try:
            portNo = self.portNumberEdit.value()
        except (ValueError, ), exc:
            portNo = None
            QMessageBox.critical(self, 'Port Number Error', str(exc))
        return portNo

    def setEnabledButtons(self, connect, disconnect):
        self.connectButton.setEnabled(connect)
        self.disconnectButton.setEnabled(disconnect)
        self.clientIdEdit.setReadOnly(disconnect)
        self.portNumberEdit.setReadOnly(disconnect)
        self.hostNameEdit.setReadOnly(disconnect)

    def setNextClientId(self):
        try:
            value = self.clientIdEdit.value()
        except (ValueError, ):
            pass
        else:
            self.clientIdEdit.setValue(value+1)


    @pyqtSignature('')
    def on_keyHelperCommandRunButton_clicked(self):
        args = str(self.keyHelperCommandEdit.text()).split()
        try:
            proc = Popen(args)
        except (OSError, ), exc:
            QMessageBox.critical(self, 'Key Helper Command Error', str(exc))
        else:
            pid = proc.pid
            self.pids['helper'].append(pid)


    @pyqtSignature('')
    def on_brokerCommandRunButton_clicked(self):
        args = str(self.brokerCommandEdit.text()).split()
        try:
            proc = Popen(args)
        except (OSError, ), exc:
            QMessageBox.critical(self, 'Broker Command Error', str(exc))
        else:
            pid = proc.pid
            self.pids['broker'].append(pid)