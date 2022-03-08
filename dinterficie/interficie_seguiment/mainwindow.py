# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDateEdit, QFormLayout,
                               QGroupBox, QLabel, QMainWindow, QMenuBar,
                               QPushButton, QSizePolicy, QStatusBar, QTextEdit,
                               QWidget)
import sys


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(402, 438)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.formLayoutWidget = QWidget(self.centralwidget)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 10, 381, 203))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.alumnes_etiqueta = QLabel(self.formLayoutWidget)
        self.alumnes_etiqueta.setObjectName(u"alumnes_etiqueta")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.alumnes_etiqueta)

        self.alumnes_desplegable = QComboBox(self.formLayoutWidget)
        self.alumnes_desplegable.setObjectName(u"alumnes_desplegable")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.alumnes_desplegable)

        self.motius_etiqueta = QLabel(self.formLayoutWidget)
        self.motius_etiqueta.setObjectName(u"motius_etiqueta")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.motius_etiqueta)

        self.motius_desplegable = QComboBox(self.formLayoutWidget)
        self.motius_desplegable.setObjectName(u"motius_desplegable")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.motius_desplegable)

        self.dateEdit = QDateEdit(self.formLayoutWidget)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setCalendarPopup(True)

        self.formLayout.setWidget(2, QFormLayout.SpanningRole, self.dateEdit)

        self.textEdit = QTextEdit(self.formLayoutWidget)
        self.textEdit.setObjectName(u"textEdit")

        self.formLayout.setWidget(3, QFormLayout.SpanningRole, self.textEdit)

        self.Registrar = QPushButton(self.formLayoutWidget)
        self.Registrar.setObjectName(u"Registrar")

        self.formLayout.setWidget(4, QFormLayout.SpanningRole, self.Registrar)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(10, 220, 351, 80))
        self.alumnes_etiqueta_2 = QLabel(self.groupBox)
        self.alumnes_etiqueta_2.setObjectName(u"alumnes_etiqueta_2")
        self.alumnes_etiqueta_2.setGeometry(QRect(0, 20, 52, 24))
        self.alumnes_desplegable_2 = QComboBox(self.groupBox)
        self.alumnes_desplegable_2.setObjectName(u"alumnes_desplegable_2")
        self.alumnes_desplegable_2.setGeometry(QRect(60, 20, 288, 24))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 402, 20))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.alumnes_etiqueta.setText(QCoreApplication.translate("MainWindow", u"Alumne: ", None))
        self.motius_etiqueta.setText(QCoreApplication.translate("MainWindow", u"Motiu:", None))
        self.dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"dd/MM/yyyy", None))
        self.Registrar.setText(QCoreApplication.translate("MainWindow", u"Registrar", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Crear informe de:", None))
        self.alumnes_etiqueta_2.setText(QCoreApplication.translate("MainWindow", u"Alumne: ", None))
    # retranslateUi



