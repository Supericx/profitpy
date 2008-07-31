#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import Qt, pyqtSignature
from PyQt4.QtGui import QFrame, QKeyEvent
from profit.lib.widgets.ui_extendedshell import Ui_ExtendedShell

## save/load splitter state

class ExtendedPythonShell(QFrame, Ui_ExtendedShell):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)

    @pyqtSignature('')
    def on_execButton_clicked(self):
        shell = self.shellWidget
        #shell.runLines(str(self.editorWidget.text()).split('\n'))
        shell.insertPlainText(self.editorWidget.text())
        e = QKeyEvent(QKeyEvent.KeyPress,
                      Qt.Key_Return, Qt.NoModifier)
        shell.keyPressEvent(e)

