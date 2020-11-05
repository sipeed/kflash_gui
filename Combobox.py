from PyQt5.QtWidgets import QComboBox,QListView
from PyQt5.QtCore import pyqtSignal


class ComboBox(QComboBox):
    clicked = pyqtSignal()
    # popupAboutToBeShown = pyqtSignal()

    def __init__(self):
        """
        Returns a list of items.

        Args:
            self: (todo): write your description
        """
        QComboBox.__init__(self)
        listView = QListView()
        self.setView(listView)
        return

    def mouseReleaseEvent(self, QMouseEvent):
        """
        Reimplemented to hide the : meth : qwidget.

        Args:
            self: (dict): write your description
            QMouseEvent: (todo): write your description
        """
        self.showItems()

    def showPopup(self):
        """
        Clearsesupupupup mode.

        Args:
            self: (todo): write your description
        """
        # self.popupAboutToBeShown.emit()
        # prevent show popup, manually call it in mouse release event
        pass
    
    def showItems(self):
        """
        Displays the current user to the inputed list of items \. : return <bool >

        Args:
            self: (todo): write your description
        """
        super(ComboBox, self).showPopup()

    def mousePressEvent(self, QMouseEvent):
        """
        Reimplemented to handle.

        Args:
            self: (todo): write your description
            QMouseEvent: (todo): write your description
        """
        self.clicked.emit()


