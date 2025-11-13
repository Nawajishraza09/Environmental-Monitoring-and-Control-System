from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__(QPixmap("src/main/python/ui/resources/icons/210.png")) # path of your image file (png)
        self.setFont(QFont("Arial", 16))
        self.showMessage("Loading Environmental Monitoring System...", Qt.AlignBottom | Qt.AlignLeft, Qt.black)

    def start(self, main_window_callback):
        self.show()
        # Wait 2.5 seconds before launching the main window
        QTimer.singleShot(3000, lambda: self._finish(main_window_callback))

    def _finish(self, callback):
        self.close()
        callback()
