"""GUI.py

Contains the PKE GUI elements constructed using PyQt5

References:
https://pythonprogramminglanguage.com/pyqt/
"""



# IMPORTS
import os
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QLineEdit, QScrollArea, QFormLayout, QGroupBox, QVBoxLayout
from PyQt5.QtCore import QSize

import Backend



# GUI CLASSES

class PkeAppWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle('Personal Knowledge Engine')

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        gridLayout = QGridLayout(self)
        centralWidget.setLayout(gridLayout)

        self.searchBar = SearchBarWidget(self.perform_search)
        gridLayout.addWidget(self.searchBar, 0, 0)

        self.searchResults = SearchResultsWidget()
        gridLayout.addWidget(self.searchResults, 1, 0)


    def perform_search(self):
        """
        Event function, for when search button is clicked; performs the search
        :return: void
        """

        # CLEAR RESULTS
        self.searchResults.clearResults()

        # GET TEXT VALUES
        search_key, file_path = self.searchBar.get_text_values()

        # CHECK IF FILE EXISTS
        if not os.path.isfile(file_path): # file does not exist
            self.searchResults.addOneResult("ERROR_MESSAGE", "There is no file at the given path. Please check "
                    "your input values.")
            return

        try:  # backend code

            # PERFORM SEARCH
            search_results = Backend.search_file_for_string(path=file_path, key=search_key)

            # PARSE RESULTS
            pass
        except Exception:  # unhandled exception in backend code; print error and return
            self.searchResults.addOneResult("ERROR_MESSAGE", "Some internal Exception in the Backend could not"
                    " be handled.")
            return

        # PRESENT RESULTS
        if search_results:
            self.searchResults.addResults(search_results)
        else:
            self.searchResults.addOneResult("NOT FOUND", "Your search key was not found within the file(s) searched.")


class SearchBarWidget(QWidget):

    def __init__(self, perform_search):
        """PyQt widget containing a search bar and search button
        """
        QWidget.__init__(self)

        gridLayout = QGridLayout(self)
        self.setLayout(gridLayout)

        title = QLabel('', self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        gridLayout.addWidget(title, 0, 0)

        """Adding text input"""
        self.setMinimumSize(QSize(300,270))    
        self.setWindowTitle("PKE Search Engine") 

        nameLabel = QLabel(self)
        nameLabel.setText('Search For:')
        self.search_line = QLineEdit(self)

        self.search_line.move(100, 20)
        self.search_line.resize(200, 32)
        nameLabel.move(40, 20)

        nameLabel = QLabel(self)
        nameLabel.setText('File Path:')
        self.file_line = QLineEdit(self)

        self.file_line.move(360, 20)
        self.file_line.resize(200, 32)
        nameLabel.move(310, 20)

        pybutton = QPushButton('Start Search/Cancel', self)
        pybutton.resize(180,32)
        pybutton.move(150,70)

        pybutton.clicked.connect(perform_search)


    def get_text_values(self) -> (str, str):
        """
        Get the values in the text input boxes
        :return: (search_key, file_path)
        """
        return self.search_line.text(), self.file_line.text()


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


    """Clear all results"""
    def clearResults(self):
        self.fileList = []
        self.filePreview = []
        for _ in range(self.rowLayout.rowCount()):
            self.rowLayout.removeRow(0)


    """Takes as input a list of tuples (file name, preview) and adds them to the results box.
    The first column are button widgets
    The second column are labels"""
    def addResults(self, rows):
        for file_name, preview in rows:
            self.fileList.append(QPushButton(str(file_name)))
            self.filePreview.append(QLabel(str(preview)))
            self.rowLayout.addRow(self.fileList[-1], self.filePreview[-1])


    """Takes as input two strings and adds them to results box
    The first string is added as a button and the second string
    is added as a label"""
    def addOneResult(self, fileName, previewSearch):
        self.fileList.append(QPushButton(str(fileName)))
        self.filePreview.append(QLabel(str(previewSearch)))
        self.rowLayout.addRow(self.fileList[-1], self.filePreview[-1])


# class SearchResultEntryWidget(QWidget):
#
#     def __init__(self):
#         """PyQt widget containing a single search result
#
#         This might contain, for example: the name of the file and/or path to
#         the file; an excerpt from the file, showing what the search matched;
#         a button to open the file location in the file browser; a button to
#         open the file in a text editor.
#         """
#         QWidget.__init__(self)
#
#         gridLayout = QGridLayout(self)
#         self.setLayout(gridLayout)
#
#         title = QLabel('This is a single search result', self)
#         title.setAlignment(QtCore.Qt.AlignCenter)
#         gridLayout.addWidget(title, 0, 0)
#
