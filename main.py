"""
PersonalKnowledgeEngine



GUI script which by affect of standard GUI construction is also master script.
Run this script to start the application.
"""


# IMPORTS (remember to list installed packages in "requirements.txt")
import sys
if sys.version_info[0:3] != (3, 6, 8):
    print('#######################################\n'
          '|                                     |\n'
          '|   WARNING: NOT USING PYTHON 3.6.8   |\n'
          '|                                     |\n'
          '#######################################')
    raise Exception('Please use Python 3.6.8 to avoid dependency conflicts')

from GUI import PkeAppWindow
from PyQt5 import QtWidgets


# HARDCODED VARS (no magic numbers; all caps for names)


# DEFINITIONS (define all requisite classes/functions)


# SCRIPT (instantiate and run app)
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = PkeAppWindow()
    mainWin.show()
    sys.exit(app.exec_())
