"""GUI.py

Contains the PKE GUI elements constructed using PyQt5

References:
https://pythonprogramminglanguage.com/pyqt/
https://www.tutorialspoint.com/pyqt5/pyqt5_signals_and_slots.htm
https://zetcode.com/gui/pyqt5/eventssignals/

TODO use Qt signals instead of callbacks for inter-thread communication
"""



# IMPORTS
import os
import traceback
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QLineEdit, QScrollArea, QFormLayout, QGroupBox, QVBoxLayout
from PyQt5.QtCore import QSize
from Backend import search_for_string
from threading import Thread  # just use threading instead of multiprocessing
                              # because we just need the GUI to update

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

        self.searchResults = SearchResultsWidget()
        gridLayout.addWidget(self.searchResults, 1, 0)

        self.searchBar = SearchBarWidget(self.searchResults)
        gridLayout.addWidget(self.searchBar, 0, 0)


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
            print("UNHANDLED EXCEPTION:")
            print(traceback.format_exc())
            self.searchResults.addOneResult("ERROR_MESSAGE", "Some internal Exception in the Backend could not"
                    " be handled.")
            return

        # PRESENT RESULTS
        if search_results:
            self.searchResults.addResults(search_results)
        else:
            self.searchResults.addOneResult("NOT FOUND", "Your search key was not found within the file(s) searched.")


class SearchBarWidget(QWidget):

    def __init__(self, search_results_widget):
        """PyQt widget containing a search bar and search button
        """
        QWidget.__init__(self)

        self.search_results_widget = search_results_widget

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

        self.search_is_running = False
        self.terminate_search = [False]

        self.startbutton = QPushButton('Start Search', self)
        self.startbutton.resize(180,32)
        self.startbutton.move(150,70)
        self.startbutton.clicked.connect(self.searchButtonClicked)

        
        self.cancelbutton = QPushButton('Cancel Search', self)
        self.cancelbutton.resize(180,32)
        self.cancelbutton.move(150,70)
        self.cancelbutton.clicked.connect(self.cancelButtonClicked)
        self.cancelbutton.hide()

    def searchResultCallback(self, path, output_instances):
        if self.search_is_running and not self.terminate_search[0]:
            print('result found in file:', path)
            print('result:', output_instances)
            self.search_results_widget.addOneResult(path, output_instances)

    def searchCompletedCallback(self):
        self.search_is_running = False
        self.cancelbutton.hide()
        self.startbutton.show()
        print('search finished')

    def searchButtonClicked(self):
        """Function that's called when the search button is pressed.
        """
        if not self.search_is_running:
            # TODO Collect information to pass into search
            key = self.search_line.text()
            include_paths = self.file_line.text().split(',')
            include_exts = ['.txt']
            exclude_paths = []
            self.terminate_search[0] = False
            backend_thread = Thread(
                target=search_for_string,
                args=(
                    key,
                    self.searchResultCallback,
                    self.searchCompletedCallback,
                    self.terminate_search,
                    include_paths,
                    include_exts,
                    exclude_paths
                )
            )
            self.startbutton.hide()
            self.cancelbutton.show()
            print('starting search')
            self.search_results_widget.clearResults()
            self.search_is_running = True
            backend_thread.start()

    def cancelButtonClicked(self):
        """Function that's called when the cancel button is pressed.
        """
        if self.search_is_running and not self.terminate_search[0]:
            self.terminate_search[0] = True
            print('search thread notified of cancellation')


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
