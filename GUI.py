"""GUI.py

Contains the PKE GUI elements constructed using PyQt5

References:
https://pythonprogramminglanguage.com/pyqt/
"""

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QLineEdit, QScrollArea, QFormLayout, QGroupBox, QVBoxLayout
from PyQt5.QtCore import QSize
from Backend import search_for_string


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

        searchResults = SearchResultsWidget()
        gridLayout.addWidget(searchResults, 1, 0)
        
        """Adding test results to search results box"""
        searchResults.addResults(testlist, testlist2)
        searchResults.addOneResult("Test File", "Test Preview")

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
        pybutton.clicked.connect(self.searchButtonClicked)
        self.search_is_running = [False]

    def searchButtonClicked(self):
        """Function that's called when the search button is pressed.
        """
        if self.search_is_running[0]:
            print('search in progress')
        else:
            # TODO Collect information to pass into search
            key = 'key'
            include_paths = ['.']
            include_exts = ['.txt']
            exclude_paths = []
            # TODO Show that the search is starting
            print('starting search')
            self.search_is_running[0] = True
            search_for_string(
                key,
                self.search_is_running,
                include_paths,
                include_exts,
                exclude_paths,
            )
            # TODO Show that the search is finished
            self.search_is_running[0] = False
            print('search finished')


class SearchResultsWidget(QWidget):

    """Initializes the search results box. 
    The box is scrollable and size adjustable."""
    def __init__(self):
        """PyQt widget containing the list of search results

        This widget might just be a table of SearchResultEntryWidget
        widgets.
        """
        QWidget.__init__(self)

        self.fileList = []
        self.filePreview = []

        self.rowLayout = QFormLayout()
        groupBox = QGroupBox("Search Results")

        groupBox.setLayout(self.rowLayout)
        scrollBox = QScrollArea()
        scrollBox.setWidgetResizable(True)
        scrollBox.setWidget(groupBox)

        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(scrollBox)

        self.setLayout(verticalLayout)

    """Takes as input two lists and adds them to the results box.
    The first list is a column of button widgets
    The second list is a column of labels"""
    def addResults(self, fileNames, previewSearch):
        for fileIndex in range(len(fileNames)):
            self.fileList.append(QPushButton(fileNames[fileIndex]))
            self.filePreview.append(QLabel(previewSearch[fileIndex]))
            self.rowLayout.addRow(self.fileList[fileIndex], self.filePreview[fileIndex])
    
    """Takes as input two strings and adds the to results box
    The first string is added as a button and the second string
    is added as a label"""
    def addOneResult(self, fileName, previewSearch):
            self.fileList.append(QPushButton(fileName))
            self.filePreview.append(QLabel(previewSearch))
            self.rowLayout.addRow(self.fileList[-1], self.filePreview[-1])


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

