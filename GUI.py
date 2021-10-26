"""GUI.py

Contains the PKE GUI elements constructed using PyQt5

References:
https://pythonprogramminglanguage.com/pyqt/
"""

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QLineEdit
from PyQt5.QtCore import QSize


class PkeAppWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle('Personal Knowledge Engine')

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        gridLayout = QGridLayout(self)
        centralWidget.setLayout(gridLayout)

        searchBar = SearchBarWidget()
        gridLayout.addWidget(searchBar, 0, 0)

        searchResults = SearchResultsWidget()
        gridLayout.addWidget(searchResults, 1, 0)


class SearchBarWidget(QWidget):

    def __init__(self):
        """PyQt widget containing a search bar and search button
        """
        QWidget.__init__(self)

        gridLayout = QGridLayout(self)
        self.setLayout(gridLayout)

        title = QLabel('This is the search bar widget', self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        gridLayout.addWidget(title, 0, 0)

        """Adding text input"""
        self.setMinimumSize(QSize(300,270))    
        self.setWindowTitle("PKE Search Engine") 
        self.nameLabel = QLabel(self)
        # self.nameLabel.setText('Search Term')
        self.line = QLineEdit(self)

        self.line.move(100, 20)
        self.line.resize(200, 32)
        self.nameLabel.move(20, 20)

        pybutton = QPushButton('Start Search/Cancel', self)
        pybutton.resize(180,32)
        pybutton.move(320,15)

class SearchResultsWidget(QWidget):

    def __init__(self):
        """PyQt widget containing the list of search results

        This widget might just be a table of SearchResultEntryWidget
        widgets.
        """
        QWidget.__init__(self)

        gridLayout = QGridLayout(self)
        self.setLayout(gridLayout)

        title = QLabel('These is the search results widget', self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        gridLayout.addWidget(title, 0, 0)


class SearchResultEntryWidget(QWidget):

    def __init__(self):
        """PyQt widget containing a single search result

        This might contain, for example: the name of the file and/or path to
        the file; an exerpt from the file, showing what the search matched;
        a button to open the file location in the file browser; a button to
        open the file in a text editor.
        """
        QWidget.__init__(self)

        gridLayout = QGridLayout(self)
        self.setLayout(gridLayout)

        title = QLabel('This is a single search result', self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        gridLayout.addWidget(title, 0, 0)

