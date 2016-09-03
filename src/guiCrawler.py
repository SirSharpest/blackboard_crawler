import sys
import main
from PyQt4 import QtCore, QtGui, uic

qtCreatorFile = "bbcrawler.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Setup connectors to UI
        self.login.clicked.connect(self.login_via_main)

        # Setup the crawler stuff
        main.setup()

    def login_via_main(self):
        main.login_bb(self.username.text(), self.password.text())


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
