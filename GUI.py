"""GUI.py

Contains the PKE GUI elements constructed using PyQt5

References:
https://pythonprogramminglanguage.com/pyqt/
"""

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QLineEdit, QScrollArea, QFormLayout, QGroupBox, QVBoxLayout
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

        """Test list inputs for the search results"""
        testlist = []
        testlist2 = []
        for x in range(20):
            testlist.append("test filename")
            testlist2.append("test other column")

        searchResults = SearchResultsWidget(testlist, testlist2)
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

    """Takes two lists as input 
    Prints out the two lists, first list as a column of button widgets and
    second list as a column of labels. The results are scrollable and size adjustable"""
    def __init__(self, fileNames, previewSearch):
        """PyQt widget containing the list of search results

        This widget might just be a table of SearchResultEntryWidget
        widgets.
        """
        QWidget.__init__(self)

        rowLayout = QFormLayout()
        groupBox = QGroupBox("Search Results")

        fileList = []
        filePreview = []

        for fileIndex in range(len(fileNames)):
            fileList.append(QPushButton(fileNames[fileIndex]))
            filePreview.append(QLabel(previewSearch[fileIndex]))
            rowLayout.addRow(fileList[fileIndex], filePreview[fileIndex])

        groupBox.setLayout(rowLayout)
        scrollBox = QScrollArea()
        scrollBox.setWidgetResizable(True)
        scrollBox.setWidget(groupBox)

        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(scrollBox)

        self.setLayout(verticalLayout)


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

