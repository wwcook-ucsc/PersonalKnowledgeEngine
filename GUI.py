"""GUI.py

Contains the PKE GUI elements constructed using PyQt5

References:
https://pythonprogramminglanguage.com/pyqt/
https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
"""


import sys
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
        """Calls the backend search function in a separate thread
        """
        super(BackendWorker, self).__init__()
        self.terminate_search = terminate_search
        self.key = key
        self.include_paths = include_paths
        self.include_exts = include_exts
        self.exclude_paths = exclude_paths
        self.signals = BackendWorkerSignals()

    def resultCallback(self, path, search_hits):
        for hit in search_hits:
            self.signals.search_hit.emit(path, hit)

    def finishedCallback(self):
        self.signals.finished.emit()

    @pyqtSlot()
    def run(self):
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
        except Exception as e:
            del e  # prevent unused variable warning
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

        self.searchResults.clearResults()

        self.threadpool.start(worker)


class SearchBarWidget(QWidget):

    def __init__(self, app_widget):
        """PyQt widget containing a search bar and search button

        :param app_widget: main app window widget instance
        """
        QWidget.__init__(self)

        self.app_widget = app_widget

        gridLayout = QGridLayout(self)
        self.setLayout(gridLayout)

        title = QLabel('', self)
        title.setAlignment(QtCore.Qt.AlignCenter)
        gridLayout.addWidget(title, 0, 0)

        # Add text input
        self.setMinimumSize(QSize(300, 270))
        self.setWindowTitle('PKE Search Engine')

        searchLabel = QLabel(self)
        searchLabel.setText('Search For:')
        searchLabel.move(10, 20)

        self.search_line = QLineEdit(self)
        self.search_line.move(90, 20)
        self.search_line.resize(200, 32)
        self.search_line.returnPressed.connect(self.searchButtonClicked)

        includePathsLabel = QLabel(self)
        includePathsLabel.setText('Path(s)<br>Included:')
        includePathsLabel.move(310, 20)

        self.file_line = QLineEdit(self)
        self.file_line.move(400, 20)
        self.file_line.resize(200, 32)
        self.file_line.returnPressed.connect(self.searchButtonClicked)

        excludePathsLabel = QLabel(self)
        excludePathsLabel.setText('Path(s)<br>Excluded:')
        excludePathsLabel.move(10, 100)

        self.path_line = QLineEdit(self)
        self.path_line.move(90, 100)
        self.path_line.resize(200, 32)
        self.path_line.returnPressed.connect(self.searchButtonClicked)

        includeExtensionsLabel = QLabel(self)
        includeExtensionsLabel.setText('Extension(s)<br>Included:')
        includeExtensionsLabel.move(310, 100)

        self.ext_line = QLineEdit(self)
        self.ext_line.move(400, 100)
        self.ext_line.resize(200, 32)
        self.ext_line.returnPressed.connect(self.searchButtonClicked)

        self.search_is_running = False
        self.terminate_search = [False]

        self.startbutton = QPushButton('Start Search', self)
        self.startbutton.resize(180, 32)
        self.startbutton.move(195, 150)
        self.startbutton.clicked.connect(self.searchButtonClicked)

        self.cancelbutton = QPushButton('Cancel Search', self)
        self.cancelbutton.resize(180, 32)
        self.cancelbutton.move(195, 150)
        self.cancelbutton.clicked.connect(self.cancelButtonClicked)
        self.cancelbutton.hide()

    def searchResultCallback(self, path, output_instances):
        if self.search_is_running and not self.terminate_search[0]:
            print('result found in file:', path)
            print('result:', output_instances)
            self.search_results_widget.addOneResult(path, output_instances)

    def searchCompletedCallback(self):
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

            # format file extensions properly
            include_exts = ['.' + ext for ext in include_exts]

            if key == '':
                self.app_widget.searchResults.clearResults()
                self.app_widget.searchResults.addOneResult(
                    '!', 'search bar is empty')
                return
            elif len(include_paths) == 0:
                self.app_widget.searchResults.clearResults()
                self.app_widget.searchResults.addOneResult(
                    '!', 'no file paths included in search')
                return
            elif len(include_exts) == 0:
                self.app_widget.searchResults.clearResults()
                self.app_widget.searchResults.addOneResult(
                    '!', 'no file extensions included in search')
                return

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

        self.rowLayout = QFormLayout()
        groupBox = QGroupBox('Search Results')

        groupBox.setLayout(self.rowLayout)
        scrollBox = QScrollArea()
        scrollBox.setWidgetResizable(True)
        scrollBox.setWidget(groupBox)

        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(scrollBox)

        self.setLayout(verticalLayout)

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
        self.fileList.append(QPushButton(str(file_name)))
        self.filePreview.append(QLabel(str(preview)))
        self.rowLayout.addRow(self.fileList[-1], self.filePreview[-1])

    def addResults(self, results):
        """Adds a list of (path, results) pairs to the results box.

        :param results: list of 2-tuples containing (path, search hits)
        """
        for file_name, preview in results:
            self.addOneResult(file_name, preview)


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
