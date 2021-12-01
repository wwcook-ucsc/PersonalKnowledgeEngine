"""GUI.py

Contains the PKE GUI elements constructed using PyQt5

References:
https://pythonprogramminglanguage.com/pyqt/
https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
"""


import sys
import subprocess
import os
import traceback
from PyQt5 import QtCore
from PyQt5.QtCore import (
    QSize,
    QObject,
    pyqtSignal,
    pyqtSlot,
    QRunnable,
    QThreadPool,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QGridLayout,
    QWidget,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QFormLayout,
    QGroupBox,
    QVBoxLayout,
)
from Backend import search_for_string


class BackendWorkerSignals(QObject):
    """
    Signals that the backend thread can emit to the GUI thread

    Supported signals:

    search_hit: file_path : str, (line_num : int, line: str)
        emitted when the search function finds a search hit

    finished: None
        emitted when the search function completes

    error: tuple (exctype, value, traceback.format_exc() )
        emitted when an exception is raised in the backend
    """
    search_hit = pyqtSignal(str, tuple)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)


class BackendWorker(QRunnable):

    def __init__(self, terminate_search, key,
                 include_paths, include_exts, exclude_paths):
        """Runs and communicates with the backend in a new thread.

        :param terminate_search: single-element list containing a bool that
                                 tells the backend whether to terminate the
                                 search early
        :param key: string to search for
        :param include_paths: list of paths to include in the search
        :param include_exts: list of file extensions in the form e.g. '.txt'
                             may instead be `None` to search all files
        :param exclude_paths: list of paths to exclude from the search
        """
        super(BackendWorker, self).__init__()
        self.terminate_search = terminate_search
        self.key = key
        self.include_paths = include_paths
        self.include_exts = include_exts
        self.exclude_paths = exclude_paths
        self.signals = BackendWorkerSignals()

    def resultCallback(self, path, search_hits):
        """Emits a `search_hit` signal containing the file path and context.

        Called by the backend whenever a search hit is found.

        :param path: path of file containing the search hit
        :param search_hits: info about the file's context of the search hit
        """
        for hit in search_hits:
            self.signals.search_hit.emit(path, hit)

    def finishedCallback(self):
        """Emits a `finished` signal.

        Called by the backend when the search completes.
        """
        self.signals.finished.emit()

    @pyqtSlot()
    def run(self):
        """Calls the backend search function in a separate thread
        """
        try:
            search_for_string(
                self.resultCallback,
                self.finishedCallback,
                self.terminate_search,
                self.key,
                self.include_paths,
                self.include_exts,
                self.exclude_paths,
            )
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()


class PkeAppWindow(QMainWindow):

    def __init__(self):
        """Main Qt window used to run the entire application
        """
        QMainWindow.__init__(self)

        self.threadpool = QThreadPool()

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle('Personal Knowledge Engine')

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        gridLayout = QGridLayout(self)
        centralWidget.setLayout(gridLayout)

        self.searchResults = SearchResultsWidget()
        gridLayout.addWidget(self.searchResults, 1, 0)

        self.searchBar = SearchBarWidget(self)
        gridLayout.addWidget(self.searchBar, 0, 0)

    def runSearch(self, key, include_paths, include_exts, exclude_paths):
        """Spawns a worker thread in the threadpool for the backend

        :param key: string to search for
        :param include_paths: list of paths to include in the search
        :param include_exts: list of file extensions in the form e.g. '.txt'
                             may instead be `None` to search all files
        :param exclude_paths: list of paths to exclude from the search
        """
        worker = BackendWorker(
            self.searchBar.terminate_search,
            key,
            include_paths,
            include_exts,
            exclude_paths,
        )
        worker.signals.search_hit.connect(self.searchResults.addOneResult)
        worker.signals.finished.connect(self.searchBar.searchCompletedCallback)

        # self.searchResults.clearResults()
        self.searchResults.addHeader(key, include_paths, include_exts, exclude_paths)

        self.threadpool.start(worker)


class SearchBarWidget(QWidget):

    def __init__(self, app_widget):
        """PyQt widget containing a search bar and search button

        :param app_widget: main app window widget instance
        """
        QWidget.__init__(self)

        self.Editor = "No Editor"

        self.saved_searches = []

        self.app_widget = app_widget

        gridLayout = QGridLayout(self)
        self.setLayout(gridLayout)

        title = QLabel('', self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        gridLayout.addWidget(title, 0, 0)

        # The basic GUI elements
        self.setMinimumSize(QSize(300, 270))
        self.setWindowTitle('PKE Search Engine')

        # Text box to put in what to search for
        searchLabel = QLabel(self)
        searchLabel.setText('Search For:')
        searchLabel.move(10, 20)

        self.search_line = QLineEdit(self)
        self.search_line.move(90, 20)
        self.search_line.resize(200, 32)
        self.search_line.returnPressed.connect(self.searchButtonClicked)

        # Text box to put in which paths to include
        includePathsLabel = QLabel(self)
        includePathsLabel.setText('Path(s)<br>Included:')
        includePathsLabel.move(310, 20)

        self.file_line = QLineEdit(self)
        self.file_line.move(400, 20)
        self.file_line.resize(200, 32)
        self.file_line.returnPressed.connect(self.searchButtonClicked)

        # Text box to put in which paths to exclude
        excludePathsLabel = QLabel(self)
        excludePathsLabel.setText('Path(s)<br>Excluded:')
        excludePathsLabel.move(10, 85)

        self.path_line = QLineEdit(self)
        self.path_line.move(90, 85)
        self.path_line.resize(200, 32)
        self.path_line.returnPressed.connect(self.searchButtonClicked)

        # Text box to put in which extensions to include
        includeExtensionsLabel = QLabel(self)
        includeExtensionsLabel.setText('Extension(s)<br>Included:')
        includeExtensionsLabel.move(310, 85)

        self.ext_line = QLineEdit(self)
        self.ext_line.move(400, 85)
        self.ext_line.resize(200, 32)
        self.ext_line.returnPressed.connect(self.searchButtonClicked)

        editorLabel = QLabel(self)
        editorLabel.setText('Editor Path:')
        editorLabel.move(10, 150)

        self.currentEditor = QLabel(self)
        self.currentEditor.setText("Current Editor: " + self.Editor)
        self.currentEditor.move(310, 150)
        self.currentEditor.resize(200, 32)

        self.editor_line = QLineEdit(self)
        self.editor_line.move(90, 150)
        self.editor_line.resize(200, 32)
        self.editor_line.returnPressed.connect(self.searchButtonClicked)

        self.search_is_running = False
        self.terminate_search = [False]

        #BUTTONS
        #to start the search:
        self.startbutton = QPushButton('Start Search', self)
        self.startbutton.resize(180, 32)
        self.startbutton.move(195, 220)
        self.startbutton.clicked.connect(self.searchButtonClicked)

        #to cancel the search (Hidden when Start button Displayed)
        self.cancelbutton = QPushButton('Cancel Search', self)
        self.cancelbutton.resize(180, 32)
        self.cancelbutton.move(195, 220)
        self.cancelbutton.clicked.connect(self.cancelButtonClicked)
        self.cancelbutton.hide()

        #to clear the search history
        self.clearbutton = QPushButton('Clear Search', self)
        self.clearbutton.resize(180, 32)
        self.clearbutton.move(195, 245)
        self.clearbutton.clicked.connect(self.app_widget.searchResults.clearResults)

    def searchCompletedCallback(self):
        """Updates the GUI to reflect the completion of a search

        Called by Qt through the BackendWorker class
        """
        if self.search_is_running:
            self.search_is_running = False
            self.cancelbutton.hide()
            self.startbutton.show()
            print('search finished')

    def searchButtonClicked(self):
        """Function that's called when the search button is pressed.
        """
        if not self.search_is_running:
            (
                key,
                include_paths,
                include_exts,
                exclude_paths,
            ) = self.getSearchInfo()

            #adds search info to list of previous searches
            self.saved_searches.append(
                (key,
                include_paths,
                include_exts,
                exclude_paths,)
                )

            # sets the editor program
            if self.app_widget.searchResults.setEditor(self.editor_line.text()):
                self.currentEditor.setText("Current Editor: " + os.path.basename(self.editor_line.text()))

            # format file extensions properly
            include_exts = ['.' + ext for ext in include_exts]

            if key == '':
                self.app_widget.searchResults.addHeader(key, include_paths, include_exts, exclude_paths)
                self.app_widget.searchResults.addOneResult(
                    '!', 'search bar is empty')
                return
            elif len(include_paths) == 0:
                self.app_widget.searchResults.addHeader(key, include_paths, include_exts, exclude_paths)
                self.app_widget.searchResults.addOneResult(
                    '!', 'no file paths included in search')
                return
            elif len(include_exts) == 0:
                include_exts = None

            self.startbutton.hide()
            self.cancelbutton.show()
            print('starting search')
            self.terminate_search[0] = False
            self.search_is_running = True

            self.app_widget.runSearch(
                key,
                include_paths,
                include_exts,
                exclude_paths,
            )

    def cancelButtonClicked(self):
        """Function that's called when the cancel button is pressed.
        """
        if self.search_is_running and not self.terminate_search[0]:
            self.terminate_search[0] = True
            print('search thread notified of cancellation')

    def getSearchInfo(self):
        """Collects the search criteria from their corresponding GUI elements.
        """
        key = self.search_line.text()

        include_paths = self.file_line.text().split(',')
        include_paths = list(filter(lambda x: x, include_paths))

        include_exts = self.ext_line.text().split(',')
        include_exts = list(filter(lambda x: x, include_exts))

        exclude_paths = self.path_line.text().split(',')
        exclude_paths = list(filter(lambda x: x, exclude_paths))

        return key, include_paths, include_exts, exclude_paths


class SearchResultsWidget(QWidget):

    def __init__(self):
        """PyQt widget containing the list of search results

        The box is scrollable and size adjustable.
        """
        QWidget.__init__(self)

        self.fileList = []
        self.filePreview = []
        self.editorSet = False
        self.editor = ""

        self.rowLayout = QFormLayout()
        groupBox = QGroupBox('Search Results')

        groupBox.setLayout(self.rowLayout)
        scrollBox = QScrollArea()
        scrollBox.setWidgetResizable(True)
        scrollBox.setWidget(groupBox)

        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(scrollBox)

        self.setLayout(verticalLayout)

    def addHeader(self, key, include_paths, include_exts, exclude_paths):
        """Writes a header to the search results box that contains the inputs for that search

        :param key: string to search for
        :param include_paths: list of paths to include in the search
        :param include_exts: list of file extensions in the form e.g. '.txt'
                             may instead be `None` to search all files
        :param exclude_paths: list of paths to exclude from the search
        """
        # button = QPushButton(search_string)
        label = QLabel("Search term: " + str(key) + 
                        ", Path: " + str(include_paths) + 
                        ", Included Extensions: " + str(include_exts)  + 
                        ", Excluded Paths: " + str(exclude_paths) )
        self.rowLayout.addRow(label)

    def clearResults(self):
        """Clears all results
        """
        self.fileList = []
        self.filePreview = []
        for _ in range(self.rowLayout.rowCount()):
            self.rowLayout.removeRow(0)

    def addOneResult(self, file_name, preview):
        """Takes as input two strings and adds them to results box

        The first string is added as a button and the second string
        is added as a label

        :param file_name: path to file
        :param preview: string of search hit context
        """
        fileBase = os.path.basename(file_name) 
        self.fileList.append(QPushButton(fileBase))
        self.fileList[-1].setToolTip(file_name)
        self.filePreview.append(QLabel(str(preview)))
        self.rowLayout.addRow(self.fileList[-1], self.filePreview[-1])
        self.connectOneButton(self.fileList[-1], file_name)

    def addResults(self, results):
        """Adds a list of (path, results) pairs to the results box.

        :param results: list of 2-tuples containing (path, search hits)
        """
        for file_name, preview in results:
            self.addOneResult(file_name, preview)

    def pathValid(self, filePath):
        """Returns True if file path exists
        :param filePath: the file path to be verified
        """
        return os.path.exists(filePath)

    def editorValid(self, editorPath):
        """Returns True if file path ends in a .exe file
        :param editorPath: the file path to be verified
        """
        fileName, fileExtension = os.path.splitext(editorPath)

        if os.path.isfile(editorPath) and fileExtension == '.exe':
            return True
        else:
            return False

    def setEditor(self, editorPath):
        """Returns true if editor has been set
        :param editorPath: the file path to be set
        """
        if self.editorValid(editorPath):
            self.editor = editorPath
            self.editorSet = True
            print("Editor set!\n")
            return True
        else:
            return False

    def openWithEditor(self, file):
        """Opens input file using the currently set editor
        :param file: the file path of the file to open
        """
        if self.editorSet == True and self.pathValid(file):
            subprocess.Popen([self.editor, file])

    def connectOneButton(self, fileButton, filePath):
        """Connects the button to the openWithEditor function
        :param fileButton: the button widget to be connected
        :param filePath: the file path of the to connect the button with
        """
        if self.editorValid(self.editor):
            fileButton.clicked.connect(lambda: self.openWithEditor(filePath))
